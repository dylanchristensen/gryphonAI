"""UI preferences as opposed to model settings.
Global:
 * preferences - Do not change preferences directly.  Use the preferences
manager to do this.

Code editor line wrap modes: no_wrap, wrap_at_edge, wrap_at_line
Graph list scroll modes: scroll_per_pixel, scroll_per_item
"""

import json
import traceback
from os.path import expanduser, join, exists
from paths_gryphon import USER_PREFERENCES_FILENAME

# graph pane scale
DEFAULT_GRAPH_PANE_SCALE = 1.0

# defaults
DEFAULT_PREFERENCES = {
   "main_window_w": 1492,
   "main_window_h": 974,
   "main_splitter_sizes": [635, 694, 155],
   "code_column_splitter_sizes": [677, 0, 206],
   "wrap_mode": "no_wrap",
   "use_spellchecker": True,
   "use_auto_indent": True,
   "scroll_mode": "scroll_per_item",
   "preferred_settings_dir": expanduser("~"),
   "preferred_mp_code_dir": expanduser("~"),
   "preferred_gry_file_dir": expanduser("~"),
   "preferred_trace_dir": expanduser("~"),
   "preferred_personal_collection_dir": join(expanduser("~"), "my_mp_files"),
   "preferred_save_selection_dir": expanduser("~"),
   "use_dark_mode": False,
   "graph_pane_scale": DEFAULT_GRAPH_PANE_SCALE,
}

# global preferences
preferences = DEFAULT_PREFERENCES.copy()

# load user preferences else load default preferences
def _load_preferences():
    # start with defaults
    for key in DEFAULT_PREFERENCES.keys():
        preferences[key] = DEFAULT_PREFERENCES[key]

    # replace saved values
    if exists(USER_PREFERENCES_FILENAME):
        try:
            with open(USER_PREFERENCES_FILENAME, encoding='utf-8-sig') as f:
                p = json.load(f)
                for key in DEFAULT_PREFERENCES.keys():
                    if key in p:
                        preferences[key] = p[key]
        except Exception as e:
            traceback.print_exc()
            print("Invalid preferences file %s: %s"
                  %(USER_PREFERENCES_FILENAME, str(e)))
_load_preferences()

