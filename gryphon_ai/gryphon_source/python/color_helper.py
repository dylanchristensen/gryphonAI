# brightness from https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color

# may prefer settings_manager preferred_pen()
from PySide6.QtGui import QColor, QPen

_T_CONTRAST = 144
"""Get text color of black or white based on given background QColor."""
def text_color_name(background_color):
    brightness = 0.299*background_color.red()+0.587*background_color.green() \
                +0.114*background_color.blue()
    if brightness > _T_CONTRAST:
        text_color = "black"
    else:
        text_color = "white"
    return text_color

def node_text_pen(node_color_name):
    node_text_color = QColor(text_color_name(QColor(node_color_name)))
    return QPen(node_text_color, 0)

