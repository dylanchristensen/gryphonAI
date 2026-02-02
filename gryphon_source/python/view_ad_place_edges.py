from collections import defaultdict
from PySide6.QtCore import QLineF, QPointF
from settings import settings
from edge_offset_tracker import OffsetTracker
from view_ad_node import ACTION_TYPE, START_TYPE, END_TYPE, \
                         DECISION_TYPE, BAR_TYPE
_CAN_H_TYPES = {START_TYPE, END_TYPE, DECISION_TYPE}
_DELTA_OFFSET = 10

"""
There are five node types, each with its own shape and defaults for initial
snap point placement:

    Node type    Shape       snap points
    ---------    -----       -------------
    start        round       pick right angle closest to destination
    end          round       pick right angle closest to destination
    decision     diamond     pick right angle closest to destination
    action       rectangle   vertical only, top center in, bottom center out
    bar          horizontal  vertical only, top area in, bottom area out

All placements use _place_to or _place_around.

The edge vector is from from_node to to_node starting in h or v edge_start
direction with alternating coordinates.
"""

def _mid_y(from_node, to_node):
    return (from_node.y() + to_node.y()) / 2

# set edge vector to go around something
def _place_around(edge, offset_tracker, recommended_x):
    # over to recommended_x then y then return
    from_y = edge.from_node.y()
    to_y = edge.to_node.y()
    edge.set_edge_vector("h", [from_y, recommended_x, to_y])

    if recommended_x < 0:
        offset_tracker.increase_left_offset()
    else:
        offset_tracker.increase_right_offset()

# set edge vector that does not go around other nodes
def _place_to(edge):
    from_node = edge.from_node
    to_node = edge.to_node
    from_x = from_node.x()
    from_y = from_node.y()
    to_x = to_node.x()
    to_y = to_node.y()
 
    # do not make an organized path if nodes overlap
    if to_node.spans_x(from_x) and to_node.spans_y(from_y):
        # no edge segments on full overlap
        edge.set_edge_vector("none", [])
    elif to_node.spans_x(from_x):
        # h edge segment on horizontal overlap
        edge.set_edge_vector("v", [from_x])
    elif to_node.spans_y(from_y):
        # v edge segment on vertical overlap
        edge.set_edge_vector("h", [from_y])

    elif from_node.node_type == BAR_TYPE \
                                and to_node.node_type == BAR_TYPE:
        # bar center to bar center
        edge.set_edge_vector("v", [from_x, _mid_y(from_node, to_node), to_x])

    elif from_node.node_type == BAR_TYPE:
        # bar to non-bar
        if from_node.spans_x(to_x):
            edge.set_edge_vector("v", [to_x])
        else:
            if to_node == ACTION_TYPE:
                edge.set_edge_vector("v",
                                     [from_x, _mid_y(from_node, to_node), to_x])
            else:
                edge.set_edge_vector("v", [from_x, to_y])

    elif to_node.node_type == BAR_TYPE:
        # non-bar to bar
        if to_node.spans_x(from_x):
            edge.set_edge_vector("v", [from_x])
        else:
            if from_node == ACTION_TYPE:
                edge.set_edge_vector("v",
                                     [from_x, _mid_y(from_node, to_node), to_x])
            else:
                edge.set_edge_vector("v", [from_x, to_y])

    elif from_node.node_type == ACTION_TYPE \
                           and to_node.node_type == ACTION_TYPE:
        # action to action
        edge.set_edge_vector("v", [from_x, _mid_y(from_node, to_node), to_x])

    elif from_node.node_type == ACTION_TYPE:
        # action to start, end, or decision
        edge.set_edge_vector("v", [from_x, to_y])

    elif to_node.node_type == ACTION_TYPE: \
        # start, end, or decision to action
        edge.set_edge_vector("h", [from_y, to_x])

    elif from_node.node_type in _CAN_H_TYPES \
                           and to_node.node_type in _CAN_H_TYPES:
        # start, end, or decision to start, end, or decision
        edge.set_edge_vector("h", [from_y, to_x])

    else:
        raise RuntimeError("bad")

# use _place_to or _place_around unless nodes overlap
def _place_edge(edge, offset_tracker):
    from_node = edge.from_node
    to_node = edge.to_node
    from_x = from_node.x()
    from_y = from_node.y()
    to_x = to_node.x()
    to_y = to_node.y()

    # bar center to bar center
    if edge.from_node.node_type == BAR_TYPE \
                      and edge.to_node.node_type == BAR_TYPE:

        # check for crossing with respect to from_node and to_node
        recommended_x = offset_tracker.recommended_x(from_x, from_y, to_y)
        if recommended_x == from_x:
            # no crossing, how about to_node
            recommended_x = offset_tracker.recommended_x(to_x, from_y, to_y)
        if recommended_x == to_x:
            # still no crossing
            _place_to(edge)
        else:
            # crossing so go over, down, back
            _place_around(edge, offset_tracker, recommended_x)

    # bar to non-bar or non-bar to bar
    elif edge.from_node.node_type == BAR_TYPE \
                      or edge.to_node.node_type == BAR_TYPE:
        from_x = edge.from_node.x()
        to_x = edge.to_node.x()
        if edge.from_node.node_type == BAR_TYPE:
            half_width = edge.from_node.boundingRect().width() / 2
            wide_x = from_x
            narrow_x = to_x
        else:
            half_width = edge.to_node.boundingRect().width() / 2
            wide_x = to_x
            narrow_x = from_x
        x_min = wide_x - half_width
        x_max = wide_x + half_width

        if narrow_x >= x_min and narrow_x <= x_max:
            # edge would be straight down so maybe go around
            from_y = edge.from_node.y()
            to_y = edge.to_node.y()
            recommended_x = offset_tracker.recommended_x(narrow_x, from_y, to_y)
            if recommended_x == narrow_x:
                # no crossing
                _place_to(edge)
            else:
                # crossing so go over, down, back
                _place_around(edge, offset_tracker, recommended_x)

        else:
            _place_to(edge)

    # non-bar to non-bar
    else:
        if edge.from_node.x() == edge.to_node.x():
            from_x = edge.from_node.x()
            from_y = edge.from_node.y()
            to_y = edge.to_node.y()
            recommended_x = offset_tracker.recommended_x(from_x, from_y, to_y)
            if recommended_x == from_x:
                # no crossing
                _place_to(edge)
            else:
                # crossing so go over, down, back
                _place_around(edge, offset_tracker, recommended_x)
        else:
            _place_to(edge)

    edge.prepareGeometryChange()

# place edge points for all edges
def place_edges(nodes, edges):
    offset_tracker = OffsetTracker(nodes)
    for edge in edges:
        _place_edge(edge, offset_tracker)

