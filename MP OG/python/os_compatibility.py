# Compensate for differences between OS systems
from platform import system
from PySide6.QtCore import Qt
"""
In particular, these functions enable compatibility with mouseless Mac
touchpad.

Mac does not automatically underscore menu mnemonic characters.  PySide6
does not support "PySide6.QtGui import qt_set_sequence_auto_mnemonic"
for MacOS.
"""

# On Mac keyboard, CRTL returns META instead of CTRL.  Sometimes we
# want to refer to MAC META as CTRL
def control_modifier():
    if system() == "Darwin":
        return Qt.KeyboardModifier.MetaModifier
    else:
        return Qt.KeyboardModifier.ControlModifier

def is_windows():
    return system() == "Windows"

def is_mac():
    return system() == "Darwin"

def pure_left_button_down(event):
    if event.buttons() != Qt.MouseButton.LeftButton:
        return False
    if not event.modifiers():
        return True
    if system() == "Darwin" and  event.modifiers() == Qt.MetaModifier:
        return True
    return False

def pure_right_button_down(event):
    if event.buttons() != Qt.MouseButton.RightButton:
        return False
    if not event.modifiers():
        return True
    if system() == "Darwin" and  event.modifiers() == Qt.MetaModifier:
        return True
    return False

def pure_shifted_left_button_down(event):
    if event.buttons() != Qt.MouseButton.LeftButton:
        return False
    if event.modifiers() == Qt.ShiftModifier:
        return True
    if system() == "Darwin" and  event.modifiers() == (Qt.MetaModifier
                                                     | Qt.ShiftModifier):
        return True
    return False

