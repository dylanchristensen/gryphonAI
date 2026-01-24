from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject
from PySide6.QtGui import QStatusTipEvent

# make consistent MP-style menu button
def mp_menu_button(menu, icon, text, tooltip):
    button = QToolButton()
    button.setMenu(menu)
    button.setIcon(icon)
    button.setText(text)
    button.setToolTip(tooltip)
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
 
    return button

# prevent menubar hover from clearing statusbar text
# adapted from https://stackoverflow.com/questions/24695200/qstatusbar-message-disappears-on-menu-hover
class MenuBarStatusTipEventRemover(QObject):
    def __init__(self, parent):
        super().__init__(parent)
    def eventFilter(self, watched, event):
        if isinstance(event, QStatusTipEvent):
            # drop the event
            return True
        else:
            # forward the event
            return super().eventFilter(watched, event)

