from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Slot

"""
Provides the top level edit menu for code editor functions.

Menus for MP code view 1 are used unless view 2 has focus and split-screen
is active.
"""

class EditMenu(QMenu):
    def __init__(self, gui_manager):
        super().__init__("&Edit")
        self.mp_code_column = gui_manager.mp_code_column
        self.mp_code_view_1 = gui_manager.mp_code_view_1
        self.mp_code_view_2 = gui_manager.mp_code_view_2

        self.aboutToShow.connect(self._set_menu_visibility)

    @Slot()
    def _set_menu_visibility(self):
        self.clear()
        if self.mp_code_view_2.hasFocus() \
                   and self.mp_code_column.is_using_code_editor_split_screen():
            menu = self.mp_code_view_2.mp_code_view_menu()
        else:
            menu = self.mp_code_view_1.mp_code_view_menu()
        actions = menu.actions()
        for action in actions:
            self.addAction(action)

