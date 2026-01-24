# brightness from https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color

# use settings_manager preferred_pen() for contrasting against the main
# graph background
from PySide6.QtGui import QColor, QPen

_T_CONTRAST = 144
"""Get text color of black or white based on given background QColor."""
def contrasting_color(background_color):
    brightness = 0.299*background_color.red()+0.587*background_color.green() \
                +0.114*background_color.blue()
    if brightness > _T_CONTRAST:
        text_color = "black"
    else:
        text_color = "white"
    return QColor(text_color)

"""Get a brighter color for dark colors or a darker color for light colors
   to suggest highlighting."""
def highlight_color(background_color):
    r = background_color.red()
    g = background_color.green()
    b = background_color.blue()

    if r < 0x40 and g < 0x40 and b < 0x60:
        # too dark so make gray
        background_color = QColor("#606060")

    brightness = 0.299*r + 0.587*g + 0.114*b
    if brightness > _T_CONTRAST:
        # bright so go darker
        return background_color.darker(125)
    else:
        return background_color.lighter(150)

