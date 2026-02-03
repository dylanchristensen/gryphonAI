from os import remove
from os.path import isfile, join, split
import json
from PySide6.QtGui import QColor, QPen
from PySide6.QtGui import QAction
from PySide6.QtCore import QObject, Signal, Slot # for signal/slot support
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QFileDialog
from settings_dialog import Ui_SettingsDialog
from preferences_manager import preferences
from paths_gryphon import DEFAULT_SETTINGS_FILENAME
from settings_defaults import DEFAULT_SETTINGS, SETTINGS_THEMES, \
                              DARK_DEFAULT_SETTINGS, DARK_SETTINGS_THEMES
from message_popup import message_popup
from verbose import verbose
from color_helper import text_color_name
"""
Manage graph settings:
  global:
  * default_settings() - return user default settings else default settings
  * set_settings(_settings)

  class:
  * change_settings(settings)
  * change_theme(theme_name) - signals change
  * change_one_setting(key, value)
  * open_settings_editor()


signals:
  signal_settings_changed()

global:
  settings<dict>
"""

def _default_settings():
    if preferences["use_dark_mode"]:
        return DARK_DEFAULT_SETTINGS
    else:
        return DEFAULT_SETTINGS

def default_themes():
    if preferences["use_dark_mode"]:
        return DARK_SETTINGS_THEMES
    else:
        return SETTINGS_THEMES

settings = dict()

# load uncleaned settings or raise exception
def _load_settings(filename):
    with open(filename) as f:
        return json.load(f)

# save or raise exception
def save_settings(filename, settings):
    with open(filename, "w") as f:
        json.dump(settings, f)

# return selected settings else default
def default_settings():
    _settings = _default_settings()
    if isfile(DEFAULT_SETTINGS_FILENAME):
        try:
            _settings = _load_settings(DEFAULT_SETTINGS_FILENAME)
        except Exception as e:
            message_popup(None,
                  "Error loading default graph settings file %s: %s"
                  %(DEFAULT_SETTINGS_FILENAME, str(e)))
    return _settings

# set settings with valid requested settings
def set_settings(requested_settings):
    default_keys = set(DEFAULT_SETTINGS.keys())
    requested_keys = set(requested_settings.keys())
    if default_keys != requested_keys:
        print("Settings manager: Change in settings detected.")

        # remove obsoleted settings
        obsoleted_keys = requested_keys - default_keys
        for key in obsoleted_keys:
             print("removing key %s"%key)
             del requested_settings[key]

        # add new settings to settings
        new_keys = default_keys - requested_keys
        for key in new_keys:
             print("adding key %s"%key)
             requested_settings[key] = DEFAULT_SETTINGS[key]

    # now accept the requested settings
    settings.update(requested_settings)

def set_default_settings():
    set_settings(default_settings())

# the preferred pen to use for contrasting against the background color
def preferred_pen():
    return QPen(QColor(text_color_name(QColor(settings["background_color"]))))

# allow global ability to signal settings since settings is a singleton
_settings_manager_singleton = None
def emit_signal_settings_changed():
    _settings_manager_singleton.signal_settings_changed.emit()

class SettingsManager(QObject):

    # signals
    signal_settings_changed = Signal(name='settingsChanged')
    signal_multiple_settings_changed = Signal(
                                          name='multipleSettingsChanged')

    def __init__(self, parent):
        global _settings_manager_singleton
        super().__init__(parent)
        self.parent = parent
        _settings_manager_singleton = self

    def change_settings(self, requested_settings):
        set_settings(requested_settings)
        self.signal_settings_changed.emit()
        self.signal_multiple_settings_changed.emit()

    @Slot()
    def change_theme(self, theme_name):
        settings.update(default_themes()[theme_name])
        self.signal_settings_changed.emit()
        self.signal_multiple_settings_changed.emit()

    def change_one_setting(self, setting_key, setting_value):
        settings[setting_key] = setting_value
        if verbose():
            print("change one setting:", setting_key, settings[setting_key])
        self.signal_settings_changed.emit()

    @Slot()
    def select_and_open_settings(self):
        suggested_filename = join(preferences[
                          "preferred_settings_dir"],
                          "mp_gryphon_graph_settings.stg")
        settings_filename, _ = QFileDialog.getOpenFileName(None,
                        "Load MP Gryphon graph settings file",
                        suggested_filename,
                        "MP Gryphon graph settings files"
                        " (*.stg);;All Files (*)",
                        options = QFileDialog.Option.DontUseNativeDialog)

        if settings_filename:

            # remember the preferred path
            head, _tail = split(settings_filename)
            preferences["preferred_settings_dir"] = head

            # open graph settings from file
            try:
                _settings = _load_settings(settings_filename)
                self.change_settings(_settings)

            except Exception as e:
                message_popup(None,
                      "Error loading graph settings file: %s" % str(e))

    @Slot()
    def select_and_save_settings(self):
        suggested_filename = join(preferences[
                          "preferred_settings_dir"],
                          "mp_gryphon_graph_settings.stg")

        settings_filename, _ = QFileDialog.getSaveFileName(None,
                        "Save MP Gryphon graph settings file",
                        suggested_filename,
                        "MP Gryphon graph setting theme files"
                        " (*.stg);;All Files (*)",
                        options = QFileDialog.Option.DontUseNativeDialog)

        if settings_filename:

            # remember the preferred path
            head, _tail = split(settings_filename)
            preferences["preferred_settings_dir"] = head

            # save graph settings to file
            try:
                save_settings(settings_filename, settings)
            except Exception as e:
                message_popup(None,
                      "Error saving graph settings file: %s" % str(e))

