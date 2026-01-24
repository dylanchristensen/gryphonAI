from os import path
from os.path import join, exists, normpath, dirname
from shutil import copy2
from glob import glob
import json
from paths_gryphon import TRACE_GENERATOR_PATH_FILENAME, RIGAL_SCRATCH
from bundled import is_bundled, require_unbundled

# global paths, do not modify externally
trace_generator_paths = dict()

# set trace_generator_paths and prepare by copying files
def set_trace_generator_paths():
    if is_bundled():
        trace_generator_root = path.abspath(path.join(path.dirname(__file__),
                                                   "trace-generator"))
    elif exists(TRACE_GENERATOR_PATH_FILENAME):
        try:
            with open(TRACE_GENERATOR_PATH_FILENAME, encoding='utf-8-sig') as f:
                trace_generator_root = json.load(f)
        except Exception as e:
            print("Error reading trace generator pathfile: %s" % str(e))
    else:
        trace_generator_root = normpath(join(dirname(__file__),
                                    "..", "..", "trace-generator"))

    # set global values into trace_generator_paths
    rigal_bin = join(trace_generator_root, "RIGAL", "rigsc.446", "bin")
    rigal_rc = join(rigal_bin, "rc")
    rigal_ic = join(rigal_bin, "ic")
    rigal_code = join(trace_generator_root, "Code")

    # put in fresh requisite RIGAL files
    files = glob(join(rigal_code, "*.h"))
    files.extend(glob(join(rigal_code, "*.rig")))
    for f in files:
        copy2(f, RIGAL_SCRATCH)

    # set global paths
    trace_generator_paths["trace_generator_root"] = trace_generator_root
    trace_generator_paths["rigal_rc"] = rigal_rc
    trace_generator_paths["rigal_ic"] = rigal_ic

# set constants on load
set_trace_generator_paths()

