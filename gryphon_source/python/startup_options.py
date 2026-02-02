from sys import version
from argparse import ArgumentParser
import inspect
import json

from PySide6.QtCore import QTimer
from PySide6 import __version__ as pyside_version
from PySide6.QtCore import __version__ as qt_version

from verbose import set_verbose
from settings import settings
from message_popup import message_popup
from paths_examples import examples_paths
from paths_gryphon import TRACE_GENERATED_OUTFILE_TG, \
                          TRACE_GENERATED_OUTFILE_GRY, \
                          PREVIOUS_SESSION_FILENAME \

def _open_file(infile, gui_manager):
    if infile:
        # shortcut for run-generated files
        if infile == "tg":
            infile = TRACE_GENERATED_OUTFILE_TG
        elif infile == "gry":
            infile = TRACE_GENERATED_OUTFILE_GRY
        elif infile == "prev_gry":
            infile = PREVIOUS_SESSION_FILENAME

        try:
            if infile[-3:] == ".mp":
                # MP code
                gui_manager.open_mp_code(infile)

            elif infile[-3:] == ".tg":
                # trace-generator generated JSON
                with open(infile, encoding='utf-8-sig') as f:
                    generated_json = json.loads(f.read())
                    gui_manager._proposed_mp_code = \
                                             "/* Text not available */"
                    gui_manager._proposed_schema_name = \
                                             "Schema name not available"
                    gui_manager._proposed_scope = 0
                    gui_manager._proposed_settings = settings.copy()
                    gui_manager.mp_code_manager.set_text(infile,
                                             gui_manager._proposed_mp_code)
                    gui_manager.response_compile_mp_code("", generated_json, "")

            elif infile[-4:] == ".gry":
                # .gry file
                gui_manager.gry_manager.import_gry_file(infile)

            # unrecognized
            else:
                error = "File extension not recognized in file: '%s'"%infile
                print(error)
                message_popup(gui_manager.w, error)

        except FileNotFoundError as e:
            print("Error reading infile %s:"%infile, e)
            message_popup(gui_manager.w, "Error reading infile %s: %s"%(infile, str(e)))

    else:
        # use hard-coded default
        gui_manager.open_mp_code(examples_paths["mp_code_default_example"])

"""Currently only -i is supported for starting with an alternate default file.
Starts MP with default .mp file else specified .mp, .tg, .gry."""
def parse_startup_options(gui_manager):
    # args
    parser = ArgumentParser(description="Gryphon GUI for trace-generator views")
    parser.add_argument("-i", "--infile", type=str, default="",
                        help="Open an input file on startup, may also "
                             "use tg or gry for cache of last TG run, "
                             "prev_gry for last Gryphon run")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print verbose output in the command window")
    args = parser.parse_args()
    set_verbose(args.verbose)

    if args.verbose:
        # Python version
        print("Python version %s"%version)

        # Qt version
        print("PySide version %s compiled by Qt version %s"
                                        %(pyside_version, qt_version))

    def open_file_function():
        _open_file(args.infile, gui_manager)

    QTimer.singleShot(0, open_file_function)

