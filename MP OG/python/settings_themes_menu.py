from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from preferences import preferences
from settings import color_theme_settings
from settings_defaults import COLOR_THEMES, DARK_COLOR_THEMES
from settings import settings, save_settings
from paths_gryphon import DEFAULT_SETTINGS_FILENAME
from settings_dialog_wrapper import SettingsDialogWrapper
from message_popup import message_popup
from mp_logger import log

"""
Provides the settings theme management menu and some actions.
"""

# extends QMenu
class SettingsThemesMenu(QMenu):

    def _theme_name_triggered_function_function(self, theme_name):
        @Slot(bool)
        def _theme_name_triggered_function(_is_checked):
            self.settings_manager.change_named_theme(theme_name)
        return _theme_name_triggered_function

    @Slot()
    def _fill_preset_themes_menu(self):
        self._preset_color_themes_menu.clear()
        if preferences["use_dark_mode"]:
            themes = DARK_COLOR_THEMES
        else:
            themes = COLOR_THEMES
        color_settings = color_theme_settings()
        for theme_name in themes.keys():
            action = QAction(theme_name, self)
            action.setCheckable(True)
            action.setChecked(color_settings == COLOR_THEMES[theme_name]
                       or color_settings == DARK_COLOR_THEMES[theme_name])
            action.triggered.connect(
                     self._theme_name_triggered_function_function(theme_name))
            self._preset_color_themes_menu.addAction(action)

    @Slot()
    def _make_default_on_startup(self):
        try:
            save_settings(DEFAULT_SETTINGS_FILENAME)
            status = "Theme settings saved for use when starting Gryphon"
        except Exception as e:
            status = "Error saving theme settings file for use " \
                     "as default: %s" % str(e)
            message_popup(self.parent_w, status)
        log(status)

    @Slot()
    def _reset_to_defaults(self):
        self.settings_manager.reset_to_defaults()
        log("Theme settings reset to Gryphon defaults")

    def __init__(self, parent_w, settings_manager):
        super().__init__("&Themes")
        self.parent_w = parent_w
        self.settings_manager = settings_manager
        self._settings_dialog_wrapper = None # avoid multiple settings dialogs

        # submenu preset color themes
        self._preset_color_themes_menu = QMenu("&Preset color themes")
        self._preset_color_themes_menu.aboutToShow.connect(
                                            self._fill_preset_themes_menu)

        # action custom theme settings
        self._action_custom_settings = QAction("&Custom theme...")
        self._action_custom_settings.setToolTip("Change graph theme settings")
        self._action_custom_settings.triggered.connect(
                                         self._open_settings_editor)

        # action export theme color settings
        self._action_export_color_settings = QAction(
                                             "&Export theme (colors only)...")
        self._action_export_color_settings.setToolTip(
                                             "Export color theme settings")
        self._action_export_color_settings.triggered.connect(
                        self.settings_manager.select_and_save_color_settings)

        # action export theme settings
        self._action_export_settings = QAction("Export &all theme settings"
                             " (colors + custom settings)...")
        self._action_export_settings.setToolTip(
                             "Export color and custom theme settings")
        self._action_export_settings.triggered.connect(
                             self.settings_manager.select_and_save_settings)

        # action import theme settings
        self._action_import_settings = QAction(
                                          "&Import theme or color theme...")
        self._action_import_settings.setToolTip("Import graph theme settings")
        self._action_import_settings.triggered.connect(
                             self.settings_manager.select_and_open_settings)

        # action default on startup
        self._action_default_on_startup = QAction(
                         "&Use current theme settings when starting Gryphon")
        self._action_default_on_startup.setToolTip("Take a snapshot of the "
                       "current settings and use them when starting Gryphon")
        self._action_default_on_startup.triggered.connect(
                                         self._make_default_on_startup)

        # action reset style settings
        self._action_reset_style_settings = QAction(
                                 "&Reset theme settings to Gryphon defaults")
        self._action_reset_style_settings.setToolTip(
                        "Reset theme and color settings to defaults")
        self._action_reset_style_settings.triggered.connect(
                                         self._reset_to_defaults)

        # the settings | themes menu
        self.addMenu(self._preset_color_themes_menu)
        self.addAction(self._action_custom_settings)
        self.addSeparator()
        self.addAction(self._action_export_color_settings)
        self.addAction(self._action_export_settings)
        self.addAction(self._action_import_settings)
        self.addSeparator()
        self.addAction(self._action_default_on_startup)
        self.addAction(self._action_reset_style_settings)

    def _open_settings_editor(self):
        if not self._settings_dialog_wrapper:
            self._settings_dialog_wrapper = SettingsDialogWrapper(
                                      self.parent_w, self.settings_manager)
        self._settings_dialog_wrapper.show()

