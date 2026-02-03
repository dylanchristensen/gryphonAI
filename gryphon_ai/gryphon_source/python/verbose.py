"""Modules can choose to print diagnostics to the command window."""
_verbose = False

def set_verbose(is_verbose):
    global _verbose
    _verbose = is_verbose

def verbose():
    return _verbose

