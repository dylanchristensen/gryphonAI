import os
import traceback
from subprocess import Popen, PIPE
import json
from PySide6.QtCore import QPointF
from node import Node
from edge import Edge

"""Manages open, save, import, and export operations for MP JSON files.

Interfaces:

read_mp_code_file(mp_code_filename):
    read MP Code file.  Return (status, mp_code_text)

save_mp_code_file(self, mp_code_filename):
    save MP Code to file.  Return status

import_gry_file(gry_filename):
    import JGF Gryphon file.  Return (status, metadata fields and graphs)

export_gry_file(gry_filename, gry_data)
    export JGF Gryphon file.  Return status 
"""

# read MP Code file.  Return (status, mp_code_text)
def read_mp_code_file(mp_code_filename):
    try:
        # use utf-8-sig to remove any BOM
        with open(mp_code_filename, encoding='utf-8-sig') as f:
            mp_code_text = f.read()
        return ("", mp_code_text)

    except Exception as e:
        return ("Error reading MP Code file '%s': %s" % (mp_code_filename, str(e)), "")

# save MP Code to file.  Return status
def save_mp_code_file(mp_code_text, mp_code_filename):
    if not mp_code_filename:
        return "Error: save MP Code file filename not provided."

    try:
        # save lines with \n after each line
        with open(mp_code_filename, 'w') as f:
            f.write(mp_code_text)
        return ""
    except Exception as e:
        status = "Error sving file '%s': %s" % (mp_code_filename, str(e))
        return status

# import JSON graph.  Return (status, metadata fields and graphs)
def import_gry_file(gry_filename):
    """Import JSON graph Gryphon file, return status, metadata fields
       and graphs."""

    # parse gry_filename
    try:
        # get json graph data
        gry_data = json.load(open(gry_filename))
        return "", gry_data

    except Exception as e:
        status = "Error reading Gryphon file '%s': %s" % (
                                         gry_filename, str(e))
        print("import_gry_file exception: %s"%status)
        traceback.print_exc()
        return (status, None)

# export JSON graph Gryphon file.  Return (status)
def export_gry_file(gry_filename, gry_data):

    # export the JSON multigraph Gryphon file
    try:
        with open(gry_filename, "w") as f:
            json.dump(gry_data, f, indent=4, sort_keys=4)
        return ""

    except Exception as e:
        status = "Error exporting Gryphon file '%s': %s" % (
                                         gry_filename, str(e))
        traceback.print_exc()
        return status

