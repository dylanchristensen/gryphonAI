import sys

# We should not set the preloaded examples path or the trace generator path
# when bundled.
def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def require_unbundled():
    if is_bundled():
        raise RuntimeError("bad")

