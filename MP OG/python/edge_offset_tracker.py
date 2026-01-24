from collections import defaultdict
from PySide6.QtCore import QLineF, QPointF
from settings import settings
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

