"""
When nodes are collapsed/uncollapsed, the set of edges in Scene changes.
We do this using GraphMainScene.reset_scene().
But we don't want to give others access to this scene singleton object.
So we provide this global function which GraphMainScene initializes.
"""
_reset_scene_function = None

def set_reset_scene_function(f):
    global _reset_scene_function
    _reset_scene_function = f

def reset_scene():
    _reset_scene_function()

