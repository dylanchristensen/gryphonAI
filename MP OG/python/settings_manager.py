from os.path import join, split
from PySide6.QtCore import QObject, Signal, Slot # for signal/slot support
from PySide6.QtGui import QAction
from preferences import preferences
from settings import settings, user_settings, save_settings, \
               save_color_settings, change_setting_values, factory_settings, \
               color_theme_settings
from settings_defaults import COLOR_THEMES, DARK_COLOR_THEMES, \
                              LIGHT_MODE_COLORS, DARK_MODE_COLORS, \
                              LIGHT_MODE_GRAYSCALE, DARK_MODE_GRAYSCALE
from mp_logger import log
from message_popup import message_popup
from verbose import verbose
from mp_file_dialog import get_open_filename, get_save_filename
"""
Manage settings:
  class:
  * change_settings(settings)
  * change_named_theme(theme_name) - signals change
  * change_one_setting(key, value)
  * reset_to_defaults()
  * open_settings_editor()
  * _maybe_switch_dark_or_light_theme_colors() - run on change_settings

signals:
  signal_settings_changed
  signal_multiple_settings_changed - used by settings_dialog_wrapper

global:
  settings<dict>
"""

_STG_FILTER_TEXT = "MP Gryphon theme or color theme settings " \
                   "(*.stg);;All Files (*)"

def _remember_preferred_path(settings_filename):
    head, _tail = split(settings_filename)
    # no need to signal change for this preference so change it directly
    preferences["preferred_settings_dir"] = head

class SettingsManager(QObject):

    # signals
    signal_settings_changed = Signal(name='settingsChanged')
    signal_multiple_settings_changed = Signal(
                                          name='multipleSettingsChanged')

    def __init__(self, parent_window, signal_preferences_changed):
        super().__init__(parent_window)
        self.parent_window = parent_window

        # This custom setting is here instead of under the custom settings
        # view tab in settings_dialog_wrapper because it needs to be highly
        # visible to the user.
        # action show type 1 probability
        self.action_show_type_1_probability = QAction(
                                           "Show Type 1 probabilities")
        self.action_show_type_1_probability.setToolTip(
                         "Show Type 1 probabilities "
                         "in the navigation pane and in exported .png graphs")
        self.action_show_type_1_probability.setCheckable(True)
        self.action_show_type_1_probability.triggered.connect(
                         self._set_show_type_1_probability)

        # connect
        signal_preferences_changed.connect(self._manage_dark_mode)

    @Slot(bool)
    def _set_show_type_1_probability(self, do_show):
        self.change_one_setting("trace_show_type_1_probability", do_show)
  
    # use requested settings, maybe compensating for dark or light mode
    def change_settings(self, requested_settings):
        change_setting_values(requested_settings)
        self._maybe_switch_dark_or_light_theme_colors()
        self.signal_settings_changed.emit()
        self.signal_multiple_settings_changed.emit()

    @Slot()
    def reset_to_defaults(self):
        self.change_settings(factory_settings())

    @Slot()
    def change_named_theme(self, theme_name):
        self.change_settings(COLOR_THEMES[theme_name])

    def change_one_setting(self, setting_key, setting_value):
        if settings[setting_key] == setting_value:
            # stay quiet
            return

        settings[setting_key] = setting_value
        if verbose():
            print("change one setting:", setting_key, settings[setting_key])
        self.signal_settings_changed.emit()

    @Slot()
    def select_and_open_settings(self):
        suggested_filename = join(preferences["preferred_settings_dir"],
                                         "mp_gryphon_theme_settings.stg")
        settings_filename = get_open_filename(self.parent_window,
                     "Import MP Gryphon theme or color theme settings",
                     suggested_filename, _STG_FILTER_TEXT)

        if settings_filename:

            # remember the preferred path
            _remember_preferred_path(settings_filename)

            # open graph settings from file
            try:
                new_settings = user_settings(settings_filename)
                self.change_settings(new_settings)
                status = "Imported theme settings file %s"%settings_filename

            except Exception as e:
                status = "Error importing theme settings file: %s" % str(e)
                message_popup(self.parent_window, status)
            log(status)

    @Slot()
    def select_and_save_settings(self):
        suggested_filename = join(preferences[
                          "preferred_settings_dir"],
                          "mp_gryphon_theme_settings.stg")

        settings_filename = get_save_filename(self.parent_window,
                        "Export all MP Gryphon theme settings"
                        " (colors + custom settings)",
                        suggested_filename, _STG_FILTER_TEXT)

        if settings_filename:

            # remember the preferred path
            _remember_preferred_path(settings_filename)

            # save settings to file
            try:
                save_settings(settings_filename)
                status = "Exported theme settings file %s"%settings_filename
            except Exception as e:
                status = "Error exporting theme settings file: %s" % str(e)
                message_popup(self.parent_window, status)
            log(status)

    @Slot()
    def select_and_save_color_settings(self):
        suggested_filename = join(preferences[
                          "preferred_settings_dir"],
                          "mp_gryphon_color_theme_settings.stg")

        settings_filename = get_save_filename(self.parent_window,
                        "Export MP Gryphon theme settings (colors only)",
                        suggested_filename, _STG_FILTER_TEXT)

        if settings_filename:

            # remember the preferred path
            _remember_preferred_path(settings_filename)

            # save color theme settings to file
            try:
                save_color_settings(settings_filename)
                status = "Saved color theme settings file %s"%settings_filename
            except Exception as e:
                status = "Error saving color theme settings file: %s" % str(e)
                message_popup(self.parent_window, status)
            log(status)

    # maybe change color theme settings directly.  Does not signal here.
    def _maybe_switch_dark_or_light_theme_colors(self):
        color_settings = color_theme_settings()
        use_dark_mode = preferences["use_dark_mode"]

        # color themes
        for theme in ["NPS", "Firebird", "SERC", "Navy"]:
            if use_dark_mode:
                # now in dark mode
                if color_settings == COLOR_THEMES[theme]:
                    # change light mode to dark
                    settings.update(DARK_MODE_COLORS)
                    return
                if color_settings == DARK_COLOR_THEMES[theme]:
                    # dark mode stays dark
                    return
            else:
                # now in light mode
                if color_settings == DARK_COLOR_THEMES[theme]:
                    # change dark mode to light
                    settings.update(LIGHT_MODE_COLORS)
                    return
                if color_settings == COLOR_THEMES[theme]:
                    # light mode stays light
                    return

        # grayscale themes
        if use_dark_mode:
            # now in dark mode
            if color_settings == LIGHT_MODE_GRAYSCALE:
                # change light mode to dark
                settings.update(DARK_MODE_GRAYSCALE)
                return
            if color_settings == DARK_MODE_GRAYSCALE:
                # dark mode stays dark
                return
        else:
            # now in light mode
            if color_settings == LIGHT_MODE_GRAYSCALE:
                # light mode stays light
                return
            if color_settings == DARK_MODE_GRAYSCALE:
                # dark mode to light
                settings.update(LIGHT_MODE_GRAYSCALE)
                return

        # no default match so no dark or light theme switch
        text = "Your custom settings are preserved when switching between" \
               " light and dark modes.  You may need to adjust your custom" \
               " settings to look right in either mode, or create and save" \
               " separate theme settings files for each mode."
        message_popup(self.parent_window, text)

    def _manage_dark_mode(self):
        # issuing settings change manages dark mode
        self.change_settings(dict())

