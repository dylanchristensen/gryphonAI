"""UI preferences as opposed to model settings.
Use this to modify preferences.  Do not modify preferences directly.

Signals:
  * signal_preferences_changed

Actions:
  Many preferences have action selections for setting them.
  Window geometry preferences and dark/light mode interact with the GUI
  and may not signal preferences changed.
"""

import json
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Signal, Slot # for signal/slot support
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QMenu
import qdarktheme

from paths_gryphon import USER_PREFERENCES_FILENAME
from preferences import preferences, DEFAULT_PREFERENCES
from message_popup import message_popup

class PreferencesManager(QObject):
    """
    Modify and signal preference changes during runtime.
    """

    # signal
    signal_preferences_changed = Signal(name='preferencesChanged')

    def __init__(self, gui_manager):
        super(PreferencesManager, self).__init__()
        self.gui_manager = gui_manager
        self._define_actions()
        self._block_signal_preferences_changed = False
        self._set_dark_or_light_mode_state()

    def save_preferences(self):
        # update preferences that are not updated in realtime
        geometry = self.gui_manager.w.geometry()
        preferences["main_window_w"] = geometry.width()
        preferences["main_window_h"] = geometry.height()
        preferences["main_splitter_sizes"] = \
                              self.gui_manager.main_splitter.sizes()
        preferences["code_column_splitter_sizes"] = \
                              self.gui_manager.mp_code_column.splitter_sizes()
        preferences["graph_pane_scale"] \
                   = self.gui_manager.main_graph_view.transform().m11()

        # export preferences in JSON
        try:
            with open(USER_PREFERENCES_FILENAME, "w", encoding='utf-8') as f:
                json.dump(preferences, f, indent=4, sort_keys=True)
        except Exception as e:
            message_popup(self.gui_manager.w,
                          "Error saving user preferences: %s"%str(e))

    @Slot()
    def _reset_all_preferences(self):
        # reset global preference values
        preferences.update(DEFAULT_PREFERENCES)

        # reset the main window position and size
        self.gui_manager.w.set_w_geometry()

        # set split pane widths
        self.gui_manager.main_splitter.setSizes(
                                        preferences["main_splitter_sizes"])
        # NOTE: setSizes does not fire splitterMoved so we do this
        self.gui_manager.navigation_column_width_manager.set_width(
                                  preferences["main_splitter_sizes"][2])
        self.gui_manager.mp_code_column.set_splitter_sizes(
                                    preferences["code_column_splitter_sizes"])

        # set the main graph scale
        self.gui_manager.main_graph_view.scale_view(
                                             preferences["graph_pane_scale"])

        # set action states
        self.set_action_states()

        # set dark or light mode
        self._set_dark_or_light_mode_state()

        # signal change for registered listeners
        self.signal_preferences_changed.emit()

    def _change_preference(self, key, value):
        if not key in preferences:
            raise RuntimeError("bad")
        preferences[key] = value
        self.signal_preferences_changed.emit()

    def _define_actions(self):
        # code editor use spell checker
        self.action_use_spellchecker = QAction("Spell checker")
        self.action_use_spellchecker.setToolTip("Enable spell checker")
        self.action_use_spellchecker.setCheckable(True)
        self.action_use_spellchecker.triggered.connect(
                                               self._set_use_spellchecker)

        # code editor text no wrap
        self.action_no_wrap = QAction("No line wrap")
        self.action_no_wrap.setToolTip("Do not wrap long lines of text")
        self.action_no_wrap.setData("no_wrap")
        self.action_no_wrap.setCheckable(True)

        # code editor text wrap at edge
        self.action_wrap_at_edge = QAction("Wrap at window edge")
        self.action_wrap_at_edge.setToolTip(
                               "Wrap long lines of text at window edge")
        self.action_wrap_at_edge.setData("wrap_at_edge")
        self.action_wrap_at_edge.setCheckable(True)

        # code editor text wrap at word boundary
        self.action_wrap_at_word = QAction("Wrap at word boundary")
        self.action_wrap_at_word.setToolTip(
                               "Wrap long lines of text at word boundaries")
        self.action_wrap_at_word.setData("wrap_at_word")
        self.action_wrap_at_word.setCheckable(True)

        # code editor word wrap preference group
        self.wrap_group = QActionGroup(self)
        self.wrap_group.addAction(self.action_no_wrap)
        self.wrap_group.addAction(self.action_wrap_at_edge)
        self.wrap_group.addAction(self.action_wrap_at_word)
        self.wrap_group.triggered.connect(self._set_wrap_mode)

        # code editor text use auto indent
        self.action_use_auto_indent = QAction("Auto-indent")
        self.action_use_auto_indent.setToolTip("Auto-indent code editor text")
        self.action_use_auto_indent.setCheckable(True)
        self.action_use_auto_indent.triggered.connect(self._set_use_auto_indent)

        # code editor split screen checkbox
        self.action_use_code_editor_split_screen = QAction("Split screen")
        self.action_use_code_editor_split_screen.setToolTip(
                            "Use a split screen for editing .mp code text")
        self.action_use_code_editor_split_screen.setCheckable(True)
        self.action_use_code_editor_split_screen.triggered.connect(
                            self._set_use_code_editor_split_screen)

        # graph list scroll per pixel radio button
        self.action_scroll_per_pixel = QAction("Smooth scroll")
        self.action_scroll_per_pixel.setToolTip("Scroll smoothly")
        self.action_scroll_per_pixel.setData("scroll_per_pixel")
        self.action_scroll_per_pixel.setCheckable(True)

        # graph list scroll per item radio button
        self.action_scroll_per_item = QAction("Scroll by item")
        self.action_scroll_per_item.setToolTip("Scroll by each item")
        self.action_scroll_per_item.setData("scroll_per_item")
        self.action_scroll_per_item.setCheckable(True)

        # graph list scroll mode preference group
        self.scroll_group = QActionGroup(self)
        self.scroll_group.addAction(self.action_scroll_per_pixel)
        self.scroll_group.addAction(self.action_scroll_per_item)
        self.scroll_group.triggered.connect(self._set_scroll_mode)

        # dark mode
        self.action_use_dark_mode = QAction("&Dark mode")
        self.action_use_dark_mode.setToolTip(
                      "Switch between dark and light mode user interfaces")
        self.action_use_dark_mode.setCheckable(True)
        self.action_use_dark_mode.triggered.connect(
                                       self._set_dark_or_light_mode)
        icon = QIcon()
        icon.addFile(":/icons/dark_mode", state=QIcon.State.Off)
        icon.addFile(":/icons/light_mode", state=QIcon.State.On)
        self.action_use_dark_mode.setIcon(icon)

        # reset preferences
        self.action_reset_preferences = QAction(
                                      "Reset GUI preferences", self)
        self.action_reset_preferences.setToolTip(
                        "Reset user interface preferences to default values")
        self.action_reset_preferences.triggered.connect(
                                               self._reset_all_preferences)

        # graph list preferences menu
        self.graph_list_menu = QMenu("&Navigation pane")
        self.graph_list_menu.addAction(self.action_scroll_per_pixel)
        self.graph_list_menu.addAction(self.action_scroll_per_item)

    # do not set action states before gui_manager subsystems are initialized
    def set_action_states(self):
        # do not signal when changing action states
        self._block_signal_preferences_changed = True

        # spell checker
        self.action_use_spellchecker.setChecked(
                                          preferences["use_spellchecker"])

        # wrap mode selection
        wrap_mode = preferences["wrap_mode"]
        if wrap_mode == "no_wrap":
            self.action_no_wrap.setChecked(True)
        elif wrap_mode == "wrap_at_edge":
            self.action_wrap_at_edge.setChecked(True)
        elif wrap_mode == "wrap_at_word":
            self.action_wrap_at_word.setChecked(True)
        else:
            print("wrap mode %s not supported."%(wrap_mode))

        # auto-indent
        self.action_use_auto_indent.setChecked(preferences["use_auto_indent"])

        # split screen: no, see code_editor_menu
        self.action_use_code_editor_split_screen.setChecked(
                                self.gui_manager.mp_code_column \
                                .is_using_code_editor_split_screen())

        # scroll
        scroll_mode = preferences["scroll_mode"]
        if scroll_mode == "scroll_per_pixel":
            self.action_scroll_per_pixel.setChecked(True)
        elif scroll_mode == "scroll_per_item":
            self.action_scroll_per_item.setChecked(True)
        else:
            print("mode %s not supported."%scroll_mode)

        # dark mode
        self.action_use_dark_mode.setChecked(preferences["use_dark_mode"])

        self._block_signal_preferences_changed = False

    # set dark mode or light mode to preference setting
    def _set_dark_or_light_mode_state(self):
        if preferences["use_dark_mode"]:
            # dark mode stylesheet and button text
            self.gui_manager.application.setStyleSheet(
                                          qdarktheme.load_stylesheet())
            self.action_use_dark_mode.setText("Use light mode")
        else:
            # light mode stylesheet and button text
            self.gui_manager.application.setStyleSheet("")
            self.action_use_dark_mode.setText("Use dark mode")

    @Slot(QAction)
    def _set_wrap_mode(self, action):
        self._change_preference("wrap_mode", action.data())

    @Slot(bool)
    def _set_use_spellchecker(self, do_use):
        self._change_preference("use_spellchecker", do_use)

    @Slot(bool)
    def _set_use_auto_indent(self, do_use):
        self._change_preference("use_auto_indent", do_use)

    @Slot(bool)
    def _set_use_code_editor_split_screen(self, do_use):
        self.gui_manager.mp_code_column.set_use_code_editor_split_screen(do_use)

    @Slot(QAction)
    def _set_scroll_mode(self, action):
        self._change_preference("scroll_mode", action.data())

    @Slot(bool)
    def _set_dark_or_light_mode(self, use_dark_mode):
        self._change_preference("use_dark_mode", use_dark_mode)
        self._set_dark_or_light_mode_state()

