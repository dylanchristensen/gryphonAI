from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import Qt

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

