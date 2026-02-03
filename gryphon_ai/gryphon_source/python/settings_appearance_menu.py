from PySide6.QtCore import QObject, Slot # for signal/slot support
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from settings_manager import default_themes, DEFAULT_SETTINGS, \
                      settings, save_settings
from paths_gryphon import DEFAULT_SETTINGS_FILENAME
from settings_dialog_wrapper import SettingsDialogWrapper
from message_popup import message_popup

"""
Provides the graph pane settings menu and some actions.
"""

# extends QMenu
class SettingsAppearanceMenu(QMenu):

    def _theme_name_triggered_function_function(self, theme_name):
        @Slot(bool)
        def _theme_name_triggered_function(_is_checked):
            self.settings_manager.change_theme(theme_name)
        return _theme_name_triggered_function

    @Slot()
    def _fill_preset_themes_menu(self):
        self._preset_themes_menu.clear()
        themes = default_themes()
        for theme_name in themes.keys():
            theme = themes[theme_name]
            action = QAction(theme_name, self)
            action.triggered.connect(
                     self._theme_name_triggered_function_function(theme_name))
            self._preset_themes_menu.addAction(action)

    @Slot()
    def _reset_settings(self):
        print("_reset_settings")
        self.settings_manager.change_settings(DEFAULT_SETTINGS)

    @Slot()
    def _make_default_on_startup(self):
        print("_make_default_on_startu_make_default_on_startupp")
        try:
            save_settings(DEFAULT_SETTINGS_FILENAME, settings)
        except Exception as e:
            message_popup(None,
                  "Error saving graph settings file as default: %s" % str(e))

    def __init__(self, parent_w, settings_manager, graphs_manager):
        super().__init__("&Appearance")
        self.parent_w = parent_w
        self.settings_manager = settings_manager
        self.graphs_manager = graphs_manager
        self._settings_dialog_wrapper = None # avoid multiple settings dialogs

        # submenu preset themes
        self._preset_themes_menu = QMenu("&Preset themes")
        self._preset_themes_menu.aboutToShow.connect(
                                            self._fill_preset_themes_menu)

        # action custom settings
        self._action_custom_settings = QAction("&Custom settings...")
        self._action_custom_settings.setStatusTip("Change graph settings")
        self._action_custom_settings.triggered.connect(
                                         self._open_settings_editor)

        # action export settings
        self._action_export_settings = QAction("&Export settings...")
        self._action_export_settings.setStatusTip("Export graph settings")
        self._action_export_settings.triggered.connect(
                             self.settings_manager.select_and_save_settings)

        # action import settings
        self._action_import_settings = QAction("&Import settings...")
        self._action_import_settings.setStatusTip("Import graph settings")
        self._action_import_settings.triggered.connect(
                             self.settings_manager.select_and_open_settings)

        # action default on startup
        self._action_default_on_startup = QAction(
                                "&Use current settings when starting Gryphon")
        self._action_default_on_startup.setStatusTip("Take a snapshot of the "
                       "current settings and use them when starting Gryphon")
        self._action_default_on_startup.triggered.connect(
                                         self._make_default_on_startup)

        # action reset settings
        self._action_reset_settings = QAction("&Reset to defaults")
        self._action_reset_settings.setStatusTip("Reset settings to defaults")
        self._action_reset_settings.triggered.connect(
                                         self._reset_settings)

        # the graph pane menu
        self.addMenu(self._preset_themes_menu)
        self.addAction(self._action_custom_settings)
        self.addAction(self._action_export_settings)
        self.addAction(self._action_import_settings)
        self.addAction(self._action_default_on_startup)
        self.addSeparator()
        self.addAction(self._action_reset_settings)

    def _open_settings_editor(self):
        if not self._settings_dialog_wrapper:
            self._settings_dialog_wrapper = SettingsDialogWrapper(
                                      self.parent_w, self.settings_manager)
        self._settings_dialog_wrapper.show()

