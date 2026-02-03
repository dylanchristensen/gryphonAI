from os.path import join, exists, normpath, dirname
from shutil import copy2
from glob import glob
import json
from PySide6 import QtCore
from paths_gryphon import TRACE_GENERATOR_PATH_FILENAME, RIGAL_SCRATCH
from message_popup import message_popup
from socket_client import USE_SOCKET

# global paths, do not modify externally
trace_generator_paths = dict()

def _set_trace_generator_paths():
    if exists(TRACE_GENERATOR_PATH_FILENAME):
        try:
            with open(TRACE_GENERATOR_PATH_FILENAME) as f:
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

def change_trace_generator_paths(new_trace_generator_root):
    trace_generator_root = new_trace_generator_root
    # save trace-generator root to file
    try:
        with open(TRACE_GENERATOR_PATH_FILENAME, "w") as f:
            json.dump(trace_generator_root, f)
    except Exception as e:
        message_popup(None,
                      "Error saving trace generator pathfile: %s" % str(e))
    _set_trace_generator_paths()

def validate_trace_generator_paths(parent_window):
    rc_path = trace_generator_paths["rigal_rc"]
    if not USE_SOCKET and not exists(rc_path):
        # the user should install the trace-generator
        message_popup(None,
              "There is no built trace generator file at %s.  "
              "Please install the trace-generator and then click on menu "
              '"Settings | Trace Generator Path..." to set the path to it.'
              %rc_path)

def schedule_validate_trace_generator_paths(parent_window):
    def validate_trace_generator_paths_function():
        validate_trace_generator_paths(parent_window)
    QtCore.QTimer.singleShot(0, validate_trace_generator_paths_function)

# set constants on load
_set_trace_generator_paths()

