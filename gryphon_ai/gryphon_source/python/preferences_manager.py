"""Access persistent user preferences using this manager.

Interfaces:
 * wrap_mode
 * use_auto_indent

Signals:
  * signal_wrap_mode_changed
  * signal_use_auto_indent_changed
  * signal_show_type_1_probability_changed
  * signal_scroll_mode_changed
  * signal_use_dark_mode_changed

Menus:
  * action_use_dark_mode
  * code_editor_menu
  * graph_list_menu

Provides preferences and actions.
Change preferences using interfaces.  Do not change preferences directly.
Global preferences could be split to separate preferences.py file.
"""
import os
import json
import traceback
from os.path import expanduser, join
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Signal, Slot # for signal/slot support
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMenu
try:
    import qdarkstyle
except ModuleNotFoundError:
    print("note: qdarkstyle not available")

from paths_gryphon import USER_PREFERENCES_FILENAME
from message_popup import message_popup

# code editor: mode, action label, action status tip
_NO_WRAP = ["no_wrap", "No line wrap", "Do not wrap long lines of text"]
_WRAP_AT_EDGE = ["wrap_at_edge", "Wrap at window edge",
                 "Wrap long lines of text at window edge"]
_WRAP_AT_WORD = ["wrap_at_word", "Wrap at word boundary",
                 "Wrap long lines of text at word boundaries"]
_WRAP_MODES = {_NO_WRAP[0], _WRAP_AT_EDGE[0], _WRAP_AT_WORD[0]}
_DEFAULT_WRAP_MODE = _NO_WRAP[0]

# code editor: apply auto-indent on CR
_DEFAULT_AUTO_INDENT = True

# graph list: mode, action label, action status tip
_SCROLL_PER_PIXEL = ["scroll_per_pixel", "Smooth scroll", "Scroll smoothly"]
_SCROLL_PER_ITEM = ["scroll_per_item", "Scroll by item", "Scroll by each item"]
_SCROLL_MODES = {_SCROLL_PER_PIXEL[0], _SCROLL_PER_ITEM[0]}
_DEFAULT_SCROLL_MODE = _SCROLL_PER_ITEM[0]

# graph pane scale
_DEFAULT_GRAPH_PANE_SCALE = 1.7

DEFAULT_PREFERENCES = {
   "main_window_w": 1492,
   "main_window_h": 974,
   "main_splitter_sizes": [635, 694, 155],
   "code_column_splitter_sizes": [677, 0, 206],
   "wrap_mode": "%s"%_DEFAULT_WRAP_MODE,
   "use_auto_indent": True,
   "show_type_1_probability": False,
   "scroll_mode": "%s"%_DEFAULT_SCROLL_MODE,
   "preferred_settings_dir": expanduser("~"),
   "preferred_mp_code_dir": expanduser("~"),
   "preferred_gry_file_dir": expanduser("~"),
   "preferred_trace_dir": expanduser("~"),
   "preferred_personal_collection_dir": join(expanduser("~"), "my_mp_files"),
   "preferred_save_selection_dir": expanduser("~"),
   "use_dark_mode": False,
   "graph_pane_scale": _DEFAULT_GRAPH_PANE_SCALE,
}

# update preferences where keys are valid
def _set_valid_preferences(requested_preferences):
    default_keys = set(DEFAULT_PREFERENCES.keys())
    requested_keys = set(requested_preferences.keys())
    if default_keys != requested_keys:
        print("Preference keys changed.")

        # remove obsoleted preferences
        obsoleted_keys = requested_keys - default_keys
        for key in obsoleted_keys:
             print("removing key %s"%key)
             del requested_preferences[key]

        # add new preferences to preferences
        new_keys = default_keys - requested_keys
        for key in new_keys:
             print("adding key %s"%key)
             requested_preferences[key] = DEFAULT_PREFERENCES[key]

    # now use cleaned preferences
    preferences.update(requested_preferences)

# global preferences
preferences = dict()
def _load_preferences():
    # user preferences
    if os.path.exists(USER_PREFERENCES_FILENAME):
        try:
            with open(USER_PREFERENCES_FILENAME) as f:
                p_user = json.load(f)
                _set_valid_preferences(p_user)
        except Exception as e:
            traceback.print_exc()
            print("Invalid preferences file %s: %s"
                  %(USER_PREFERENCES_FILENAME, str(e)))
            preferences.update(DEFAULT_PREFERENCES)
    else:
        preferences.update(DEFAULT_PREFERENCES)
_load_preferences()

def _wrap_mode(label):
    if label == _NO_WRAP[1]:
        mode = _NO_WRAP[0]
    elif label == _WRAP_AT_EDGE[1]:
        mode = _WRAP_AT_EDGE[0]
    elif label == _WRAP_AT_WORD[1]:
        mode = _WRAP_AT_WORD[0]
    else:
        raise RuntimeError("bad")
    return mode

def _scroll_mode(label):
    if label == _SCROLL_PER_PIXEL[1]:
        mode = _SCROLL_PER_PIXEL[0]
    elif label == _SCROLL_PER_ITEM[1]:
        mode = _SCROLL_PER_ITEM[0]
    else:
        raise RuntimeError("bad")
    return mode

def _make_show_box_action(parent, text, key):
    action = QAction(text, parent)
    action.setCheckable(True)
    action.setChecked(preferences[key])
    @Slot(bool)
    def action_function(is_checked):
        preferences[key] = is_checked
    action.triggered.connect(action_function)
    return action

class PreferencesManager(QObject):
    """
    Supports user preferences.
    """

    # signal
    signal_wrap_mode_changed = Signal(str, name='wrapModeChanged')
    signal_use_auto_indent_changed = Signal(bool, name='autoIndentChanged')
    signal_show_type_1_probability_changed \
                             = Signal(name='type1ProbabilityChanged')
    signal_scroll_mode_changed = Signal(str, name='scrollModeChanged')
    signal_use_dark_mode_changed = Signal(bool, name='darkModeChanged')

    def save(self):
        # collect preferences that are not updated in realtime
        geometry = self.gui_manager.w.geometry()
        preferences["main_window_w"] = geometry.width()
        preferences["main_window_h"] = geometry.height()
        preferences["main_splitter_sizes"] = \
                              self.gui_manager.main_splitter.sizes()
        preferences["code_column_splitter_sizes"] = \
                              self.gui_manager.mp_code_column.splitter_sizes()
        preferences["wrap_mode"] = self.wrap_mode()
        preferences["use_auto_indent"] = self.use_auto_indent()
        preferences["scroll_mode"] = self.scroll_mode()
        preferences["graph_pane_scale"] \
                   = self.gui_manager.graph_main_widget.view.transform().m11()

        # export preferences in JSON
        try:
            with open(USER_PREFERENCES_FILENAME, "w") as f:
                json.dump(preferences, f)
        except Exception as e:
            message_popup(None, "Error saving user preferences: %s"%str(e))

    def __init__(self, gui_manager):
        super(PreferencesManager, self).__init__()
        self.gui_manager = gui_manager

        # action settings preferences code editor text no wrap
        self.action_no_wrap = QAction(_NO_WRAP[1])
        self.action_no_wrap.setStatusTip(_NO_WRAP[2])
        self.action_no_wrap.setCheckable(True)

        # action settings preferences code editor text wrap at edge
        self.action_wrap_at_edge = QAction(_WRAP_AT_EDGE[1])
        self.action_wrap_at_edge.setStatusTip(_WRAP_AT_EDGE[2])
        self.action_wrap_at_edge.setCheckable(True)

        # action settings preferences code editor text wrap at word boundary
        self.action_wrap_at_word = QAction(_WRAP_AT_WORD[1])
        self.action_wrap_at_word.setStatusTip(_WRAP_AT_WORD[2])
        self.action_wrap_at_word.setCheckable(True)

        # code editor word wrap preference group
        self.wrap_group = QActionGroup(self)
        self.wrap_group.addAction(self.action_no_wrap)
        self.wrap_group.addAction(self.action_wrap_at_edge)
        self.wrap_group.addAction(self.action_wrap_at_word)
        self.wrap_group.triggered.connect(self._set_wrap_mode)

        # action settings preferences code editor text wrap at word boundary
        self.action_use_auto_indent = QAction("Auto-indent")
        self.action_use_auto_indent.setStatusTip("Auto-indent code editor text")
        self.action_use_auto_indent.setCheckable(True)
        self.action_use_auto_indent.triggered.connect(self._set_use_auto_indent)

        # action settings preferences code editor show type 1 probability
        self.action_show_type_1_probability = QAction(
                                           "Show Type 1 probabilities")
        self.action_show_type_1_probability.setStatusTip(
                         "Show Type 1 probabilities "
                         "in the navigation pane and in exported .png graphs")
        self.action_show_type_1_probability.setCheckable(True)
        self.action_show_type_1_probability.triggered.connect(
                         self._set_show_type_1_probability)

        # action settings preferences code editor split screen checkbox
        self.action_use_code_editor_split_screen = QAction("Split screen")
        self.action_use_code_editor_split_screen.setStatusTip(
                            "Use a split screen for editing .mp code text")
        self.action_use_code_editor_split_screen.setCheckable(True)
        self.action_use_code_editor_split_screen.triggered.connect(
                            self._set_use_code_editor_split_screen)

        # action settings graph list preferences scroll per pixel
        self.action_scroll_per_pixel = QAction(_SCROLL_PER_PIXEL[1])
        self.action_scroll_per_pixel.setStatusTip(_SCROLL_PER_PIXEL[2])
        self.action_scroll_per_pixel.setCheckable(True)

        # action settings graph list preferences scroll per item
        self.action_scroll_per_item = QAction(_SCROLL_PER_ITEM[1])
        self.action_scroll_per_item.setStatusTip(_SCROLL_PER_ITEM[2])
        self.action_scroll_per_item.setCheckable(True)

        # graph list scroll mode preference group
        self.scroll_group = QActionGroup(self)
        self.scroll_group.addAction(self.action_scroll_per_pixel)
        self.scroll_group.addAction(self.action_scroll_per_item)
        self.scroll_group.triggered.connect(self._set_scroll_mode)

        # action dark mode
        self.action_use_dark_mode = QAction("Use &dark mode")
        self.action_use_dark_mode.setStatusTip(
                        "Select to use the dark user interface")
        self.action_use_dark_mode.setCheckable(True)
        self.action_use_dark_mode.triggered.connect(self._set_use_dark_mode)

        # action reset user interface preferences
        self.action_reset_preferences = QAction(
                                      "Reset GUI preferences", self)
        self.action_reset_preferences.setStatusTip(
                        "Reset user interface preferences to default values")
        self.action_reset_preferences.triggered.connect(
                                               self._reset_all_preferences)

        # graph list preferences menu
        self.graph_list_menu = QMenu("&Navigation pane")
        self.graph_list_menu.addAction(self.action_scroll_per_pixel)
        self.graph_list_menu.addAction(self.action_scroll_per_item)
        self.graph_list_menu.addSeparator()
        self.graph_list_menu.addAction(self.action_show_type_1_probability)

        # install initial preferences
        self._set_wrap_action(preferences["wrap_mode"])
        self.action_use_auto_indent.setChecked(preferences["use_auto_indent"])
        self.action_show_type_1_probability.setChecked(
                                    preferences["show_type_1_probability"])
        self._set_scroll_action(preferences["scroll_mode"])
        self.action_use_dark_mode.setChecked(preferences["use_dark_mode"])
        self._set_use_dark_mode(preferences["use_dark_mode"])

    def wrap_mode(self):
        return _wrap_mode(self.wrap_group.checkedAction().text())

    def use_auto_indent(self):
        return self.action_use_auto_indent.isChecked()

    def show_type_1_probability(self):
        return self.action_show_type_1_probibility.isChecked()

    def scroll_mode(self):
        return _scroll_mode(self.scroll_group.checkedAction().text())

    def use_dark_mode(self):
        return self.action_use_dark_mode.isChecked()

    # set the active wrap action
    def _set_wrap_action(self, wrap_mode):
        if wrap_mode == _NO_WRAP[0]:
            self.action_no_wrap.setChecked(True)
        elif wrap_mode == _WRAP_AT_EDGE[0]:
            self.action_wrap_at_edge.setChecked(True)
        elif wrap_mode == _WRAP_AT_WORD[0]:
            self.action_wrap_at_word.setChecked(True)
        else:
            print("mode %s not supported.  Using %s."%(wrap_mode,
                                                       _DEFAULT_WRAP_MODE))
            if _DEFAULT_WRAP_MODE == _NO_WRAP[0]:
                self.action_no_wrap.setChecked(True)
            elif _DEFAULT_WRAP_MODE == _WRAP_AT_EDGE[0]:
                self.action_wrap_at_edge.setChecked(True)
            elif _DEFAULT_WRAP_MODE == _WRAP_AT_WORD[0]:
                self.action_wrap_at_word.setChecked(True)
            else:
                raise RuntimeError("bad")

    # set the active scroll action
    def _set_scroll_action(self, scroll_mode):
        if scroll_mode == _SCROLL_PER_PIXEL[0]:
            self.action_scroll_per_pixel.setChecked(True)
        elif scroll_mode == _SCROLL_PER_ITEM[0]:
            self.action_scroll_per_item.setChecked(True)
        else:
            print("mode %s not supported.  Using %s."%(scroll_mode,
                                                       _DEFAULT_SCROLL_MODE))
            if _DEFAULT_SCROLL_MODE == _SCROLL_PER_PIXEL[0]:
                self.action_scroll_per_pixel.setChecked(True)
            elif _DEFAULT_SCROLL_MODE == _SCROLL_PER_ITEM[0]:
                self.action_scroll_per_item.setChecked(True)
            else:
                raise RuntimeError("bad")

    @Slot()
    def _set_split_screen_checkbox(self):
        self.action_use_code_editor_split_screen.setChecked(
                   self.gui_manager.mp_code_column
                   .using_code_editor_split_screen())

    @Slot(QAction)
    def _set_wrap_mode(self, action):
        wrap_mode = _wrap_mode(action.text())
        self.signal_wrap_mode_changed.emit(_wrap_mode(action.text()))

    @Slot(bool)
    def _set_use_auto_indent(self, is_auto_indent):
        self.signal_use_auto_indent_changed.emit(
                                   self.action_use_auto_indent.isChecked())

    @Slot(bool)
    def _set_show_type_1_probability(self, show_type_1_probability):
        preferences["show_type_1_probability"] = show_type_1_probability
        self.signal_show_type_1_probability_changed.emit()

    @Slot(bool)
    def _set_use_code_editor_split_screen(self, use):
        self.gui_manager.mp_code_column.set_use_code_editor_split_screen(use)

    @Slot(QAction)
    def _set_scroll_mode(self, action):
        scroll_mode = _scroll_mode(action.text())
        self.signal_scroll_mode_changed.emit(_scroll_mode(action.text()))

    @Slot(bool)
    def _set_use_dark_mode(self, use_dark_mode):
        preferences["use_dark_mode"] = use_dark_mode
        if use_dark_mode:
            try:
                self.gui_manager.application.setStyleSheet(
                                    qdarkstyle.load_stylesheet())
            except NameError:
                message_popup(None, "Error: qdarkstyle not available.")

        else:
            self.gui_manager.application.setStyleSheet("")
        self.signal_use_dark_mode_changed.emit(use_dark_mode)

    # main window position and dimensions
    def set_w_geometry(self):
        self.gui_manager.w.setGeometry(200, 100,
                                       preferences["main_window_w"],
                                       preferences["main_window_h"])

    @Slot()
    def _reset_all_preferences(self):
        preferences.update(DEFAULT_PREFERENCES)
        self.set_w_geometry()
        self.gui_manager.main_splitter.setSizes(
                                        preferences["main_splitter_sizes"])
        # NOTE: setSizes does not fire splitterMoved so we do this
        self.gui_manager.navigation_column_width_manager.set_width(
                                  preferences["main_splitter_sizes"][2])
        self.gui_manager.mp_code_column.set_splitter_sizes(
                                    preferences["code_column_splitter_sizes"])
        self._set_wrap_action(preferences["wrap_mode"])
        self.signal_wrap_mode_changed.emit(preferences["wrap_mode"])
        self.action_use_auto_indent.setChecked(preferences["use_auto_indent"])
        self.signal_use_auto_indent_changed.emit(
                                   self.action_use_auto_indent.isChecked())
        self.action_show_type_1_probability.setChecked(
                                    preferences["show_type_1_probability"])
        self.signal_show_type_1_probability_changed.emit()
        self._set_scroll_action(preferences["scroll_mode"])
        self.signal_scroll_mode_changed.emit(preferences["scroll_mode"])
        self.action_use_dark_mode.setChecked(preferences["use_dark_mode"])
        self._set_use_dark_mode(preferences["use_dark_mode"])
        self.gui_manager.graph_main_widget.view.scale_view(
                                             preferences["graph_pane_scale"])

