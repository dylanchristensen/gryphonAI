from os.path import exists
import json
from PySide6 import QtCore
from paths_gryphon import TRACE_GENERATOR_PATH_FILENAME
from message_popup import message_popup
from paths_trace_generator import trace_generator_paths, \
                                  set_trace_generator_paths

def change_trace_generator_paths(parent_window, new_trace_generator_root):
    # save trace-generator root to file
    try:
        with open(TRACE_GENERATOR_PATH_FILENAME, "w", encoding='utf-8') as f:
            json.dump(new_trace_generator_root, f)
        set_trace_generator_paths()
    except Exception as e:
        message_popup(parent_window,
                      "Error saving trace generator pathfile: %s" % str(e))

