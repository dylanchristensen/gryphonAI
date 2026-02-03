import settings_raw as s

def _new_settings(defaults, new):
    settings = defaults.copy()
    settings.update(new)
    return settings

SETTINGS_THEMES = {
           "NPS theme": _new_settings(s.defaults, s.NPS_THEME),
           "Firebird theme": _new_settings(s.defaults, s.FIREBIRD_THEME),
           "Black-and-white": _new_settings(s.defaults,
                                            s.BLACK_AND_WHITE_THEME),
           "SERC theme": _new_settings(s.defaults, s.SERC_THEME),
           "Navy theme": _new_settings(s.defaults, s.NAVY_THEME),
           "Printer-friendly": _new_settings(s.defaults,
                                            s.PRINTER_FRIENDLY_THEME),
           "High contrast": _new_settings(s.defaults, s.HIGH_CONTRAST_THEME),
}

DARK_SETTINGS_THEMES = {
           "NPS theme (dark)": _new_settings(s.defaults, s.DARK_NPS_THEME),
           "Firebird theme (dark)": _new_settings(s.defaults,
                                            s.DARK_FIREBIRD_THEME),
           "Black-and-white (dark)": _new_settings(s.defaults,
                                            s.DARK_BLACK_AND_WHITE_THEME),
           "SERC theme (dark)": _new_settings(s.defaults, s.DARK_SERC_THEME),
           "Navy theme (dark)": _new_settings(s.defaults, s.DARK_NAVY_THEME),
           "Printer-friendly (dark)": _new_settings(s.defaults,
                                            s.DARK_PRINTER_FRIENDLY_THEME),
           "High contrast (dark)": _new_settings(s.defaults,
                                            s.DARK_HIGH_CONTRAST_THEME),
}

DEFAULT_SETTINGS = SETTINGS_THEMES["NPS theme"].copy()
DARK_DEFAULT_SETTINGS = DARK_SETTINGS_THEMES["NPS theme (dark)"].copy()

