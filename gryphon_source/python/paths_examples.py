import sys
from os import path
from os.path import join, exists, normpath, dirname
from shutil import copy2
from glob import glob
import json
from PySide6 import QtCore
from message_popup import message_popup
from paths_gryphon import EXAMPLES_PATH_FILENAME
from bundled import is_bundled, require_unbundled

# global paths, do not modify externally
examples_paths = dict()

def _set_examples_paths():
    if is_bundled():
        examples_root = path.abspath(path.join(path.dirname(__file__),
                                                   "preloaded-examples"))
    elif exists(EXAMPLES_PATH_FILENAME):
        try:
            with open(EXAMPLES_PATH_FILENAME, encoding='utf-8-sig') as f:
                examples_root = json.load(f)
        except Exception as e:
            print("Error reading examples pathfile: %s" % str(e))
            examples_root = None
    else:
        examples_root = None
    
    # If no path set yet, try to find examples relative to this file
    # First try in same directory as this file (gryphon_source/python/preloaded-examples)
    if not examples_root or not exists(examples_root):
        local_examples = normpath(join(dirname(__file__), "preloaded-examples"))
        if exists(local_examples) and exists(join(local_examples, "models")):
            examples_root = path.abspath(local_examples)
        else:
            # Fallback to project root (../preloaded-examples)
            project_root_examples = normpath(join(dirname(__file__),
                                                  "..", "..", "preloaded-examples"))
            if exists(project_root_examples) and exists(join(project_root_examples, "models")):
                examples_root = path.abspath(project_root_examples)
            else:
                # Last resort: use the local path even if it doesn't exist yet
                examples_root = path.abspath(local_examples)

    # set global values into examples_paths
    examples_paths["examples_root"] = examples_root
    examples_paths["models"] = join(examples_root, "models")
    examples_paths["snippets"] = join(examples_root, "snippets")
    examples_paths["mp_code_default_example"] = join(examples_root, "models",
                          "Example03_ATMWithdrawal_BehaviorOfEnvironment.mp")

def change_examples_paths(parent_window, new_examples_root):
    require_unbundled()
    examples_root = new_examples_root
    # save examples root to file
    try:
        with open(EXAMPLES_PATH_FILENAME, "w", encoding='utf-8') as f:
            json.dump(examples_root, f)
    except Exception as e:
        message_popup(parent_window,
                      "Error saving examples pathfile: %s" % str(e))
    _set_examples_paths()

def validate_examples_paths(parent_window):
    require_unbundled()
    models_path = examples_paths["examples_root"]
    if not exists(examples_paths["models"]):
        # the user should install preloaded-examples
        message_popup(parent_window,
              "Preloaded examples are not installed at path %s.  "
              "Please install preloaded-examples and then click on menu "
              '"Settings | Preloaded Examples Path..." to set the path '
              "to preloaded examples."%examples_paths["examples_root"])

def schedule_validate_examples_paths(parent_window):
    require_unbundled()
    def validate_examples_paths_function():
        validate_examples_paths(parent_window)
    QtCore.QTimer.singleShot(0, validate_examples_paths_function)

# set constants on load
_set_examples_paths()

