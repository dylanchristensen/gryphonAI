from pathlib import Path
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot
"""The top-level directory contains category directories and .mp files.
   Category directories contain .mp files and are not nested."""

def _load_example_function_function(load_example_function, posix_path):
    @Slot(bool)
    def _load_example_function(_is_checked):
        load_example_function(posix_path)
    return _load_example_function

def _add_paths(posix_dir_path, posix_paths, dir_menu, load_example_function):
    len_prefix_text = len(posix_dir_path.as_posix())
    for posix_path in posix_paths:
        full_text = posix_path.as_posix()
        shown_text = full_text[len_prefix_text+1:]
        action = QAction(shown_text,
                         dir_menu) # dir_menu is just a handle for persistence
        action.triggered.connect(_load_example_function_function(
                                       load_example_function, posix_path))
        dir_menu.addAction(action)

def fill_examples_menu(examples_menu, path, action_function):
    examples_menu.clear()
    posix_path = Path(path)

    # top-level menu of top-level paths and files
    posix_dir_paths = sorted([x for x in posix_path.iterdir() if x.is_dir()])
    posix_file_paths = sorted([x for x in posix_path.iterdir() if x.is_file()])

    # add top-level paths and add their contents under them
    for posix_dir_path in posix_dir_paths:

        # add examples nestable under posix_dir_path
        dir_menu = examples_menu.addMenu(posix_dir_path.name)
        posix_paths = sorted(posix_dir_path.rglob("*.mp"),
                             key=lambda x: x.name.casefold())
        _add_paths(posix_dir_path, posix_paths, dir_menu, action_function)

    # add top-level examples
    _add_paths(posix_path, posix_file_paths, examples_menu, action_function)

