"""
The undo stack being managed is the one in the graph_item currently
being displayed in the scene.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoCommand, QIcon
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import LOCATION_POS, LOCATION_BEZIER, LOCATION_AD_EDGE, \
                            LOCATION_NOT_MANAGED
def undo_stack_actions(graph_item, menu):
    undo_action = graph_item.undo_stack.createUndoAction(menu, "Undo move")
    undo_action.setIcon(QIcon(":/icons/move_undo"))
    redo_action = graph_item.undo_stack.createRedoAction(menu, "Redo move")
    redo_action.setIcon(QIcon(":/icons/move_redo"))
    return undo_action, redo_action

def maybe_undo_move(graph_item, key_event):
    if key_event.key() == Qt.Key.Key_Z \
                     and key_event.modifiers() == Qt.ControlModifier \
                     and graph_item.undo_stack.canUndo():
        graph_item.undo_stack.undo()
        key_event.accept()

def maybe_redo_move(graph_item, key_event):
    if key_event.key() == Qt.Key.Key_Y \
                     and key_event.modifiers() == Qt.ControlModifier \
                     and graph_item.undo_stack.canRedo():
        graph_item.undo_stack.redo()
        key_event.accept()

def item_locations(scene):
    items = scene.items()
    locations = dict()
    for item in items:
        item_type = item.type()
        if item_type in LOCATION_POS:
            locations[item] = item.pos()
        elif item_type in LOCATION_BEZIER:
            locations[item] = (item.ep1, item.ep2)
        elif item_type in LOCATION_AD_EDGE:
            locations[item] = (item.edge_start, item.edge_vector)
        elif item_type in LOCATION_NOT_MANAGED:
            pass
        else:
            raise RuntimeError("bad")

    return locations

class _UndoCommand(QUndoCommand):
    def __init__(self, text, locations_before, locations_after):
        super().__init__(text)
        self.locations_before = locations_before
        self.locations_after = locations_after

    def _move(self, locations):
        if not locations:
            raise RuntimeError("bad")

        for item, location in locations.items():
            item_type = item.type()
            if item_type in LOCATION_POS:
                item.setPos(location)
            elif item_type in LOCATION_BEZIER:
                item.ep1, item.ep2 = location
                edge_grip_manager = item.scene().edge_grip_manager
                highlighted_edge = edge_grip_manager.highlighted_edge
                item.reset_appearance()

                # propagate edge position change to QGraphicsItem parents so
                # box sizes adjust since parentItem is not called for edges
                item.parentItem().itemChange(QGraphicsItem.GraphicsItemChange \
                                             .ItemPositionHasChanged, None)

                # maybe move Bezier edge grips
                if item == highlighted_edge:
                    # this item has active grips so move them
                    edge_grip_manager.grip1.setPos(highlighted_edge.ep1)
                    edge_grip_manager.grip2.setPos(highlighted_edge.ep2)

            elif item_type in LOCATION_AD_EDGE:
                item.edge_start, item.edge_vector = location
                edge_grip_manager = item.scene().view_ad_edge_grip_manager
                highlighted_edge = edge_grip_manager.highlighted_edge
                item.reset_appearance()

                # propagate edge position change to QGraphicsItem parents so
                # box sizes adjust since parentItem is not called for edges
                item.parentItem().itemChange(QGraphicsItem.GraphicsItemChange \
                                             .ItemPositionHasChanged, None)

                # maybe move AD edge grips
                if item == highlighted_edge:
                    # this item has potentially different active grips
                    # so reset them by rehighlighting the highlighted edge
                    edge_grip_manager.highlight_edge(item)
                    
            elif item_type in LOCATION_NOT_MANAGED:
                pass
            else:
                raise RuntimeError("bad")

        item.scene().fit_scene()

    def undo(self):
        self._move(self.locations_before)

    def redo(self):
        self._move(self.locations_after)

def push_undo_command(undo_stack, text, locations_before, locations_after):
    undo_command = _UndoCommand(text, locations_before, locations_after)
    undo_stack.push(undo_command)

def push_undo_movement(scene, movement_function, text):
    locations_before = item_locations(scene)
    movement_function()
    locations_after = item_locations(scene)
    scene.fit_scene()
    push_undo_command(scene.graph_item.undo_stack, text,
                      locations_before, locations_after)

"""
Use _locations_before, track_undo_press, and track_undo_release to emplace
mouse-activated moves for QGraphicsItem items that are selectable and
movable.

We use a singleton instead of a class because we can and because scene
is not defined until after item initialization when the item is parented
to the scene.
"""
_locations_before = None

def track_undo_press(item, event):
    global _locations_before

    # move starts on press with only the left button down
    if event.buttons() == Qt.MouseButton.LeftButton:

        # this should never happen
        if _locations_before:
            raise RuntimeError("bad")

        # add locations
        scene = item.scene()
        _locations_before = item_locations(scene)

def track_undo_release(item, text, event):
    global _locations_before
    if not (event.buttons() & Qt.MouseButton.LeftButton) \
                      and _locations_before:

        # left button came up while tracking item locations which
        # means there will be no more movement until the next
        # left-button-only mouse down event
        scene = item.scene()
        locations_after = item_locations(scene)
        if locations_after != _locations_before:

            # movement did happen
            push_undo_command(scene.graph_item.undo_stack,
                              text, _locations_before, locations_after)

        # move time is over
        _locations_before = None

def track_undo_bezier_grip_press(edge, event):
    global _locations_before

    # move starts on press with only the left button down
    if event.buttons() == Qt.MouseButton.LeftButton:

        # this should never happen
        if _locations_before:
            raise RuntimeError("bad")

        # add edge bezier location
        _locations_before = {edge: (edge.ep1, edge.ep2)}

def track_undo_bezier_grip_release(edge, text, event):
    global _locations_before
    if not (event.buttons() & Qt.MouseButton.LeftButton) \
                      and _locations_before:

        # left button came up while tracking edge locations which
        # means there will be no more movement until the next
        # left-button-only mouse down event
        locations_after = {edge: (edge.ep1, edge.ep2)}
        if locations_after != _locations_before:

            # movement did happen
            scene = edge.scene()
            push_undo_command(scene.graph_item.undo_stack,
                              text, _locations_before, locations_after)

        # move time is over
        _locations_before = None

def track_undo_ad_grip_press(edge, event):
    global _locations_before

    # move starts on press with only the left button down
    if event.buttons() == Qt.MouseButton.LeftButton:

        # this should never happen
        if _locations_before:
            raise RuntimeError("bad")

        # add edge bezier location
        _locations_before = {edge: (edge.edge_start, edge.edge_vector)}

def track_undo_ad_grip_release(edge, text, event):
    global _locations_before
    if not (event.buttons() & Qt.MouseButton.LeftButton) \
                      and _locations_before:

        # left button came up while tracking edge locations which
        # means there will be no more movement until the next
        # left-button-only mouse down event
        locations_after = {edge: (edge.edge_start, edge.edge_vector)}
        if locations_after != _locations_before:

            # movement did happen
            scene = edge.scene()
            push_undo_command(scene.graph_item.undo_stack,
                              text, _locations_before, locations_after)

        # move time is over
        _locations_before = None

