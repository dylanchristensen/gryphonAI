from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu
from find_and_replace_dialog_wrapper import FindAndReplaceDialogWrapper

"""
Provides a code editor menu.
"""

def make_code_editor_menu(preferences_manager, mp_code_view_1, mp_code_view_2):
    @Slot()
    def _about_to_show():
        preferences_manager.action_use_code_editor_split_screen.setChecked(
                   preferences_manager.gui_manager.mp_code_column
                   .using_code_editor_split_screen())
        mp_code_view_1.action_find_and_replace.setDisabled(
                   FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible)
        mp_code_view_2.action_find_and_replace.setDisabled(
                   FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible
                   or not preferences_manager \
                         .action_use_code_editor_split_screen.isChecked())
        
    menu = QMenu("&Code editor")
    line_mode_menu = QMenu("Line mode", menu)
    menu.addMenu(line_mode_menu)
    line_mode_menu.addAction(preferences_manager.action_no_wrap)
    line_mode_menu.addAction(preferences_manager.action_wrap_at_edge)
    line_mode_menu.addAction(preferences_manager.action_wrap_at_word)
    menu.addAction(preferences_manager.action_use_auto_indent)
    menu.addAction(preferences_manager.action_use_code_editor_split_screen)
    menu.addSeparator()
    menu.addAction(mp_code_view_1.action_find_and_replace)
    menu.addAction(mp_code_view_2.action_find_and_replace)
    menu.aboutToShow.connect(_about_to_show)
    return menu

