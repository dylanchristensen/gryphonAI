from os.path import join
import threading
from subprocess import Popen, PIPE
from paths_trace_generator import trace_generator_paths
from paths_gryphon import RIGAL_SCRATCH
from socket_client_endpoint import selected_endpoint
from socket_client import socket_mp_check_syntax

# the syntax checker runs RIGAL commands in the GUI thread
def _run_rigal_now(cmd):
    # the mp file must be in the same directory as the trace-generator commands
    p = Popen(cmd, stdout=PIPE, cwd=RIGAL_SCRATCH)
    lines = p.communicate(timeout=1.0)[0].decode('utf-8').split("\n")
    if p.returncode != 0:
        print("error with command", cmd)
        print("lines", lines)
        print("Aborting.")
        raise Exception("_run_rigal command aborted.")

    return lines

class SyntaxCheckerThread(threading.Thread):
    def __init__(self, schema_name, mp_code_text, callback):
        super().__init__()
        self.schema_name = schema_name
        self.mp_code_text = mp_code_text
        self.callback = callback

    def run(self):
        # paths
        rigal_rc = trace_generator_paths["rigal_rc"]
        rigal_ic = trace_generator_paths["rigal_ic"]

        # write MP Code text to file for RIGAL tools
        try:
            mp_filename = join(RIGAL_SCRATCH, "%s.mp" % self.schema_name)
            with open(mp_filename, 'w', encoding='utf-8') as f:
                f.write(self.mp_code_text)
        except Exception as e:
            self.callback("Error writing temporary %s.mp file: %s"
                          % (self.schema_name, str(e)))
            return

        try:
            # rc MP2-parser
            _lines_1 = _run_rigal_now([rigal_rc, "MP2-parser"])

            # rc schema
            lines_2 = _run_rigal_now([rigal_ic, "MP2-parser", self.schema_name,
                                      "tree", "1"])
        except Exception as e:
            self.callback("Error running the trace-generator: %s"%str(e))
            return

        # maybe return error
        error_lines = list()
        track_errors = False
        for l in lines_2:
            if l[:14] == "*** error: at ":
                track_errors = True
            if l[:18] == "Errors detected...":
                track_errors = False
            if track_errors:
                error_lines.append(l.strip())

        # done, return any error on one line
        self.callback(" ".join(error_lines))
        return

def mp_check_syntax(schema_name, mp_code_text, callback):
    if selected_endpoint()["use_socket"]:
        socket_mp_check_syntax(schema_name, mp_code_text, callback)
        return

    syntax_checker_thread = SyntaxCheckerThread(
                                    schema_name, mp_code_text, callback)
    syntax_checker_thread.start()

