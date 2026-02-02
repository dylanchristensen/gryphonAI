"""Track the currently opened filename.
Although the full path may be provided, only the tail is returned.
This allows us to use the user's folder for opened examples.

set_active_mp_code_filename is called:
* In mp_code_manager in set_text when MP code text is set by loading .mp,
  loading .gry, or by closing the .mp file.
* In gui_manager in save_mp_code_file in case the user renames the file.

active_mp_code_filename is called:
* in gui_manager in save_mp_code_file to suggest the active filename.
"""
from os.path import split
_filename = ""

def set_active_mp_code_filename(filename):
    global _filename
    _filename = filename

def active_mp_code_filename():
    _head, tail = split(_filename)
    return tail
