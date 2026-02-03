from os.path import join, exists, normpath, dirname
from shutil import copy2
from glob import glob
import json
from PySide6 import QtCore
from message_popup import message_popup
from paths_gryphon import EXAMPLES_PATH_FILENAME

# global paths, do not modify externally
examples_paths = dict()

def _set_examples_paths():
    if exists(EXAMPLES_PATH_FILENAME):
        try:
            with open(EXAMPLES_PATH_FILENAME) as f:
                examples_root = json.load(f)
        except Exception as e:
            print("Error reading examples pathfile: %s" % str(e))
    else:
        examples_root = normpath(join(dirname(__file__),
                                      "..", "..", "preloaded-examples"))

    # set global values into examples_paths
    examples_paths["examples_root"] = examples_root
    examples_paths["models"] = join(examples_root, "models")
    examples_paths["snippets"] = join(examples_root, "snippets")
    examples_paths["mp_code_default_example"] = join(examples_root, "models",
                          "Example03_ATMWithdrawal_BehaviorOfEnvironment.mp")

def change_examples_paths(new_examples_root):
    examples_root = new_examples_root
    # save examples root to file
    try:
        with open(EXAMPLES_PATH_FILENAME, "w") as f:
            json.dump(examples_root, f)
    except Exception as e:
        message_popup(None,
                      "Error saving examples pathfile: %s" % str(e))
    _set_examples_paths()

def validate_examples_paths(parent_window):
    models_path = examples_paths["examples_root"]
    if not exists(examples_paths["models"]):
        # the user should install preloaded-examples
        message_popup(None,
              "Preloaded examples are not installed at path %s.  "
              "Please install preloaded-examples and then click on menu "
              '"Settings | Preloaded Examples Path..." to set the path '
              "to preloaded examples."%examples_paths["examples_root"])

def schedule_validate_examples_paths(parent_window):
    def validate_examples_paths_function():
        validate_examples_paths(parent_window)
    QtCore.QTimer.singleShot(0, validate_examples_paths_function)

# set constants on load
_set_examples_paths()

