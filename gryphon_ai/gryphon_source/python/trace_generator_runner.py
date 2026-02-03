import subprocess
import sys
import threading
import traceback
from os.path import join
import shutil
import io
import json
from paths_gryphon import RIGAL_SCRATCH, TRACE_GENERATED_OUTFILE_TG
from paths_trace_generator import trace_generator_paths
from verbose import verbose

# use popen instead of run to enable kill, https://stackoverflow.com/questions/39187886/what-is-the-difference-between-subprocess-popen-and-subprocess-run/39187984

# trace-generator commands read and write files in the same directory
# they run in.  Therefore we put files in RIGAL_SCRATCH and run
# trace-generator commands in RIGAL_SCRATCH using pwd=RIGAL_SCRATCH.

# Finishes by calling callback with status or "" if okay, generated_json,
# and any log text.

# for synchronous operation when testing, call runner_thread.join().

def _cmd_text(cmd):
    part = "' '".join(cmd)
    return("'%s'"%part)

class RunnerThread(threading.Thread):

    # run cmd, add labeled output to list, raise error on failure
    def _run_one(self, cmd, text_prefix, outputs):
        if self._stop_event.is_set():
            # cancel was requested
            return

        if verbose():
            print("cmd: %s"%_cmd_text(cmd))

        # run the command
        self.cmd_p = subprocess.Popen(cmd, cwd=RIGAL_SCRATCH,
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                  universal_newlines=True)

        # wait for it to finish, collecting all output
        # note that kill delays in communicate() when there is no ouput
        stdout_text, stderr_text= self.cmd_p.communicate()
        if stderr_text:
            self.outputs.append("%s stderr:\n%s"%(text_prefix, stderr_text))
        if stdout_text:
            self.outputs.append("%s stdout:\n%s"%(text_prefix, stdout_text))
        if self.cmd_p.returncode:
            # the cmd program returned an error
            raise RuntimeError("%s error code %d"%(
                                       text_prefix, self.cmd_p.returncode))
        if "*** error: " in stdout_text:
            # unfortuntately trace-generator does not provide a returncode
            # when it fails so we look for indicators in stdout
            raise RuntimeError("%s error:\n%s"%(text_prefix, stdout_text))

    def _log_text(self):
        return "\n".join(self.outputs)

    def __init__(self, schema_name, scope, mp_code_text, callback):
        threading.Thread.__init__(self)
        self.schema_name = schema_name
        self.scope = scope
        self.mp_code_text = mp_code_text
        self.callback = callback
        self.outputs = list()
        self._stop_event = threading.Event()

    def run(self):
        rigal_rc = trace_generator_paths["rigal_rc"]
        rigal_ic = trace_generator_paths["rigal_ic"]

        cmd1 = [rigal_rc, "MP2-parser"]
        cmd2 = [rigal_ic, "MP2-parser", self.schema_name, "tree",
                                                        "%d"%self.scope]
        cmd3 = [rigal_rc, "MP2-generator"]
        cmd4 = [rigal_ic, "MP2-generator", "tree"]
        cmd5 = ["g++", "%s.cpp"%self.schema_name, "-o", self.schema_name, "-O3"]
        cmd6 = ["./%s"%self.schema_name]

        try:
            # write mp_code text to file for trace-generator
            mp_filename = join(RIGAL_SCRATCH, "%s.mp" % self.schema_name)
            with open(mp_filename, 'w') as f:
                f.write(self.mp_code_text)

            # exec the commands
            self._run_one(cmd1, "command 1", self.outputs)
            self._run_one(cmd2, "command 2", self.outputs)
            self._run_one(cmd3, "command 3", self.outputs)
            self._run_one(cmd4, "command 4", self.outputs)
            self._run_one(cmd5, "command 5", self.outputs)
            self._run_one(cmd6, "command 6", self.outputs)

            # read generated_json from trace-generator
            generated_json_filename = join(RIGAL_SCRATCH,
                                           "%s.json"%self.schema_name)
            with open(generated_json_filename) as f:
                generated_text = f.read()
                generated_json = json.loads(generated_text)

            # save JSON in readable format
            with open(TRACE_GENERATED_OUTFILE_TG, "w") as f:
                json.dump(generated_json, f, indent=4, sort_keys=True)

            # successfully done
            self.callback("", generated_json, self._log_text())

        except Exception as e:
            if self._stop_event.is_set():
                # user stopped
                self.callback("trace-generation aborted", dict(),
                                   self._log_text())
            else:
                # trouble
                traceback.print_exc()
                self.callback("Error running trace-generator: %s"%str(e),
                                            dict(), self._log_text())

    # abort this thread and its compilation process
    def mp_cancel_compile(self):
        # signal to stop running commands
        self._stop_event.set()

        # kill any currently running command
        try:
            self.cmd_p.kill()
        except:
            traceback.print_exc()
            pass

