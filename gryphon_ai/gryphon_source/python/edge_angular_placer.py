from collections import defaultdict
from PySide6.QtCore import QLineF, QPointF
from settings_manager import settings
from view_ad_node import START_TYPE, END_TYPE, DECISION_TYPE, BAR_TYPE
_CAN_H_TYPES = {START_TYPE, END_TYPE, DECISION_TYPE}
_DELTA_OFFSET = 10

"""
Consider node rows and columns when placing edges.
When placing an edge between nodes:
    If the column is the same but there is a node at that column in a row
    between, then apply an offset:
        If column=0: offset left else offet right.  First offset is 3/5
        node width.  Subsequent offsets is 1/5 node width.

Each node offers a connection point and whether that connection is to be
entered horizontally (h) or vertically (v).  We conect node pairs with
either one or two right-angle jog jogs depending on what the nodes provide:

   Entry angle  Entry angle  Flow
   -----------  -----------  -----
        h            h       x y x
        h            v       x y
        v            h       y x
        v            v       y x y

There are five node types, each with its own shape and rules for snap point
placement:

    Node type    Shape       snap points
    ---------    -----       -------------
    start        round       pick right angle closest to destination
    end          round       pick right angle closest to destination
    decision     diamond     pick right angle closest to destination
    action       rectangle   vertical only, top center in, bottom center out
    bar          horizontal  vertical only, top area in, bottom area out

To get the snap point and approach to a node, provide from point and direction:
      snap_pint, approach = node.placer_snap_point(other_point<p>, is_to<bool>)
"""

class OffsetTracker():
    def __init__(self, nodes):
        self.right_offset = _DELTA_OFFSET
        self.left_offset = _DELTA_OFFSET

        # create dict of list where keys are y and values are
        # a set of (x_min, x_max) tuples representing where nodes lie.
        # if an edge crosses a node then we should go around it using xyx.
        self.occupied_positions = defaultdict(set)
        for node in nodes:
            x = node.x()
            half_width = node.boundingRect().width() / 2
            self.occupied_positions[node.y()].add((x-half_width, x+half_width))

    # return a recommended x value to use for going around nodes or just x
    def recommended_x(self, x, y_from, y_to):
        x_new = x
        y_min = min(y_from, y_to)
        y_max = max(y_from, y_to)
        should_adjust_left = False
        should_adjust_right = False
        for y, values in self.occupied_positions.items():
            if y > y_min and y < y_max:
                for x_min, x_max in values:
                    if x >= x_min and x <= x_max:
                        if x <= 0:
                            should_adjust_left = True
                            x_new = min(x_new, x_min - self.left_offset)
                        else:
                            should_adjust_right = True
                            x_new = max(x_new, x_max + self.right_offset)
        return x_new

    def increase_left_offset(self):
        self.left_offset += _DELTA_OFFSET

    def increase_right_offset(self):
        self.right_offset += _DELTA_OFFSET

def _map_xyx(edge):
    edge.ep1 = QPointF(edge.ep0)
    edge.ep2 = QPointF(edge.ep3)
    x_mid = (edge.ep0.x() + edge.ep3.x()) / 2
    edge.ep1.setX(x_mid)
    edge.ep2.setX(x_mid)

def _map_yxy(edge):
    edge.ep1 = QPointF(edge.ep0)
    edge.ep2 = QPointF(edge.ep3)
    y_mid = (edge.ep0.y() + edge.ep3.y()) / 2
    edge.ep1.setY(y_mid)
    edge.ep2.setY(y_mid)

def _map_xy(edge):
    edge.ep1 = QPointF(edge.ep0)
    edge.ep2 = QPointF(edge.ep3)
    edge.ep1.setX(edge.ep3.x())
    edge.ep2.setY(edge.ep0.y())

def _map_yx(edge):
    edge.ep1 = QPointF(edge.ep0)
    edge.ep2 = QPointF(edge.ep3)
    edge.ep1.setY(edge.ep3.y())
    edge.ep2.setX(edge.ep0.x())

def _map_over_x(edge, offset):
    edge.ep1 = QPointF(edge.ep0)
    edge.ep2 = QPointF(edge.ep3)
    dx = edge.ep0.x() + offset
    edge.ep1.setX(dx)
    edge.ep2.setX(dx)


# place edge points so they go around something
def _place_around(edge, offset_tracker, recommended_x):
    # over to recommended_x then y then return
    edge.ep0, _from_approach = edge.from_node.placer_snap_point(
                           QPointF(recommended_x, edge.from_node.y()), False)
    edge.ep3, _to_approach = edge.to_node.placer_snap_point(
                           QPointF(recommended_x, edge.to_node.y()), True)
    _map_over_x(edge, recommended_x)
    if recommended_x < 0:
        offset_tracker.increase_left_offset()
    else:
        offset_tracker.increase_right_offset()

# place edge points without going around anything
def _place_to(edge):
 
    if edge.from_node.node_type == BAR_TYPE \
                                and edge.to_node.node_type == BAR_TYPE:
        # bar to bar, place yxy bar center to bar center
        edge.ep0, _from_approach = edge.from_node.placer_snap_point(
                                    QPointF(edge.from_node.x(), 0), False)
        edge.ep3, _to_approach = edge.to_node.placer_snap_point(
                                    QPointF(edge.to_node.x(), 0), True)
        _map_yxy(edge)

    else:

        # place snap-point to snap-point
        edge.ep0, from_approach = edge.from_node.placer_snap_point(
                                                 edge.to_node.pos(), False)
        edge.ep3, to_approach = edge.to_node.placer_snap_point(edge.ep0, True)
        if from_approach == "h" and to_approach == "h":
            _map_xyx(edge)
        elif from_approach == "h" and to_approach == "v":
            _map_xy(edge)
        elif from_approach == "v" and to_approach == "h":
            _map_yx(edge)
        elif from_approach == "v" and to_approach == "v":
            _map_yxy(edge)
        else:
            raise RuntimeError("bad")
    edge.reset_appearance()

def _place_edge(edge, offset_tracker):
    from_x = edge.from_node.x()
    from_y = edge.from_node.y()
    to_x = edge.to_node.x()
    to_y = edge.to_node.y()

    # bar center to bar center
    if edge.from_node.node_type == BAR_TYPE \
                      and edge.to_node.node_type == BAR_TYPE:
        from_x = edge.from_node.x()
        from_y = edge.from_node.y()
        to_x = edge.to_node.x()
        to_y = edge.to_node.y()
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

    edge.reset_appearance()

# place edge points for all edges
def place_edges(nodes, edges):
    offset_tracker = OffsetTracker(nodes)
    for edge in edges:
        _place_edge(edge, offset_tracker)

