from os.path import isfile
import json
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import QFile, QTextStream, QIODevice
from paths_gryphon import DEFAULT_SETTINGS_FILENAME
from preferences import preferences
from settings_defaults import DARK_MODE_COLORS
from color_helper import contrasting_color
"""
Do not change settings without using the settings_manager which
signals change.

global:
  settings<dict>
  factory_settings
  user_settings
  save_settings
  save_color_settings
  change_setting_values
  preferred_pen()
"""

def factory_settings():
    # read resource
    f = QFile(":/settings/default_settings")
    f.open(QIODevice.ReadOnly | QIODevice.Text)
    text = QTextStream(f).readAll()
    return json.loads(text)

# load or raise exception
def user_settings(filename):
    with open(filename, encoding='utf-8-sig') as f:
        return json.load(f)

# save settings or raise exception
def save_settings(filename):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(settings, f, indent=4, sort_keys=True)

def color_theme_settings():
    color_settings = dict()
    for key, value in settings.items():
        if "color" in key:
            color_settings[key] = value
    return color_settings


# save color properties of settings or raise exception
def save_color_settings(filename):
    color_settings = color_theme_settings()
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(color_settings, f, indent=4, sort_keys=True)

# replace settings with requested settings
def change_setting_values(requested_settings):
    default_keys = set(settings.keys())
    for key, value in requested_settings.items():
        if key in default_keys:
            settings[key] = value

# set settings:
# start with factory settings
settings = factory_settings()

# maybe replace with user's default settings
if isfile(DEFAULT_SETTINGS_FILENAME):
    change_setting_values(user_settings(DEFAULT_SETTINGS_FILENAME))

# maybe adjust for dark mode
if preferences["use_dark_mode"]:
    settings.update(DARK_MODE_COLORS)

# the preferred pen to use for contrasting against the background color
def preferred_pen():
    return QPen(QColor(contrasting_color(
                                 QColor(settings["background_color"]))))

