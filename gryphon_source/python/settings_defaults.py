import json
from copy import deepcopy
from PySide6.QtCore import Qt, QFile, QTextStream, QIODevice

# load settings from resources
def _settings(resource):
    # read resource
    f = QFile(resource)
    f.open(QIODevice.ReadOnly | QIODevice.Text)
    text = QTextStream(f).readAll()
    return json.loads(text)

"""
Default settings come from settings/default_settings.stg.  This consists
of all settings plus NPS settings.  Settings get compiled into the
resources file.

Themes consist of settings that include *_color* in their names.  This
includes *_color_gradient.

There are only a select set of differences between dark and light color modes.
For grayscale colors, many gray shades change between dark and light modes.
"""
LIGHT_MODE_GRAYSCALE = _settings(":/settings/grayscale")
DARK_MODE_GRAYSCALE = _settings(":/settings/grayscale_dark")

LIGHT_MODE_COLORS = {
    "ad_edge_color": "#000000",
    "ad_end_color": "#000000",
    "ad_start_color": "#000000",
    "background_color": "#ffffff",
    "code_editor_comment_color": "#606060",
    "code_editor_number_color": "#000000",
    "code_editor_operator_color": "#000000",
    "code_editor_variable_color": "#404040",
    "graph_edge_color": "#000000",
    "trace_edge_follows_color": "#000000",
}

DARK_MODE_COLORS = {
    "ad_edge_color": "#ffffff",
    "ad_end_color": "#ffffff",
    "ad_start_color": "#ffffff",
    "background_color": "#202124",
    "code_editor_comment_color": "#7d7d7d",
    "code_editor_number_color": "#e0e0e0",
    "code_editor_operator_color": "#e0e0e0",
    "code_editor_variable_color": "#686868",
    "graph_edge_color": "#ffffff",
    "trace_edge_follows_color": "#ffffff",
}

# default settings
DEFAULT_SETTINGS = _settings(":/settings/default_settings")

COLOR_THEMES = {
           "NPS": _settings(":/settings/nps"),
           "Firebird": _settings(":/settings/firebird"),
           "Grayscale": LIGHT_MODE_GRAYSCALE.copy(),
           "SERC": _settings(":/settings/serc"),
           "Navy": _settings(":/settings/navy"),
}

DARK_COLOR_THEMES = deepcopy(COLOR_THEMES)
DARK_COLOR_THEMES["NPS"].update(DARK_MODE_COLORS)
DARK_COLOR_THEMES["Firebird"].update(DARK_MODE_COLORS)
DARK_COLOR_THEMES["Grayscale"].update(DARK_MODE_GRAYSCALE)
DARK_COLOR_THEMES["SERC"].update(DARK_MODE_COLORS)
DARK_COLOR_THEMES["Navy"].update(DARK_MODE_COLORS)

