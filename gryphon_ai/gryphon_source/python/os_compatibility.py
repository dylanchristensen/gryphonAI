# Compensate for differences between OS systems
from platform import system
from PySide6.QtCore import Qt
#zzzz from PySide6.QtGui import qt_set_sequence_auto_mnemonic

# On Mac keyboard, CRTL returns META instead of CTRL, so compensate.
def control_modifier():
    if system() == "Darwin":
        return Qt.KeyboardModifier.MetaModifier
    else:
        return Qt.KeyboardModifier.ControlModifier

