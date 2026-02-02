from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu

"""
Provides a settings menu for code editor settings.
"""

def make_code_editor_settings_menu(gui_manager):
    preferences_manager = gui_manager.preferences_manager
    mp_code_column = gui_manager.mp_code_column
    spellcheck_dialog = gui_manager.spellcheck_whitelist_dialog_wrapper

    @Slot()
    def _about_to_show():
        # split screen
        preferences_manager.action_use_code_editor_split_screen.setChecked(
                         mp_code_column.is_using_code_editor_split_screen())

        # spellchecker whitelist dialog
        spellcheck_dialog.action_open_spellcheck_whitelist_dialog.setDisabled(
                      spellcheck_dialog.isVisible())

    menu = QMenu("&Code editor")
    menu.addAction(preferences_manager.action_use_spellchecker)
    menu.addAction(spellcheck_dialog.action_open_spellcheck_whitelist_dialog)
    menu.addSeparator()
    line_mode_menu = QMenu("Line mode", menu)
    menu.addMenu(line_mode_menu)
    line_mode_menu.addAction(preferences_manager.action_no_wrap)
    line_mode_menu.addAction(preferences_manager.action_wrap_at_edge)
    line_mode_menu.addAction(preferences_manager.action_wrap_at_word)
    menu.addAction(preferences_manager.action_use_auto_indent)
    menu.addAction(preferences_manager.action_use_code_editor_split_screen)
    menu.aboutToShow.connect(_about_to_show)
    return menu

