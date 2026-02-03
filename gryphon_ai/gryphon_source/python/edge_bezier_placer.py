from collections import defaultdict
from PySide6.QtCore import QLineF, QPointF

# usually update old_ep0 and old_ep3 to new positions
def move_cubic_bezier_path(edge):

    # endpoints are same node
    if edge.from_node == edge.to_node:
        delta = edge.ep0 - edge.old_ep0
        edge.ep1 += delta
        edge.ep2 += delta

        # move old endpoints to new position
        edge.old_ep0 = edge.ep0
        return

    # old line angle and length
    l = QLineF(edge.old_ep0, edge.old_ep3)
    old_angle = l.angle()
    old_length = l.length()

    # new line angle and length
    l = QLineF(edge.ep0, edge.ep3)
    new_angle = l.angle()
    new_length = l.length()

    # too close to matter and can cause /0 error
    if new_length < 1:
        return

    # establish values if old endpoints were the same
    if old_length == 0:
        # manually separate Cubic Bezier points since not established yet
        edge.ep1 = (2*edge.ep0 + edge.ep3)/3 # 1/3 across
        edge.ep2 = (edge.ep0 + 2*edge.ep3)/3 # 2/3 across

        # move old endpoints to new position
        edge.old_ep0 = edge.ep0
        edge.old_ep3 = edge.ep3
        return

    # the scale and delta angle for calculating edge points
    scale = new_length / old_length
    angle = new_angle - old_angle

    # p1 angle and length with respect to old_ep0
    l1 = QLineF(edge.old_ep0, edge.ep1)
    l1_angle = l1.angle()
    l1_length = l1.length()

    # new l1 starting at ep0 with scaled length and adjusted angle
    new_l1 = QLineF(edge.ep0, edge.ep0 + QPointF(l1_length * scale, 0))
    new_l1.setAngle(l1_angle + angle)

    # new p1
    edge.ep1 = new_l1.p2()

    # p2 angle and length with respect to old_ep0
    l2 = QLineF(edge.old_ep0, edge.ep2)
    l2_angle = l2.angle()
    l2_length = l2.length()

    # new l2 starting at ep0 with scaled length and adjusted angle
    new_l2 = QLineF(edge.ep0, edge.ep0 + QPointF(l2_length * scale, 0))
    new_l2.setAngle(l2_angle + angle)

    # new p2
    edge.ep2 = new_l2.p2()

    # move old endpoints to new position
    edge.old_ep0 = edge.ep0
    edge.old_ep3 = edge.ep3

# return ep1x, ep1y, ep2x, ep2y
def _place_points(src_id, src_x, src_y, dest_id, dest_x, dest_y, count):
    scale = 20

    # edge connects same node
    if src_id == dest_id:
        # origin point
        p = QPointF(src_x, src_y)

        # edge to same node so identify a length higher than the node
        h = 100 + 2*scale * count
        l = QLineF(QPointF(0, 0), QPointF(h, 0))
        # 0 degrees is at 3 o'clock, increasing clockwise
        l.setAngle(90+60)
        ep1 = p + l.p2()
        l.setAngle(90-60)
        ep2 = p + l.p2()

    # edge connects separate nodes
    else:

        # node points
        source_p = QPointF(src_x, src_y)
        dest_p = QPointF(dest_x, dest_y)
        ep1 = (2*source_p + dest_p)/3 # 1/3 across
        ep2 = (source_p + 2*dest_p)/3 # 2/3 across

        # skew overlapping edges
        if count > 0:
            angle = QLineF(source_p, dest_p).angle()
            l = QLineF(QPointF(0, 0), QPointF(scale * count, 0))
            l.setAngle(angle+90)

            # bow depending on orientation of nodes
            if src_x < dest_x or (src_x == dest_x and src_y > dest_y):
                ep1 += l.p2()
                ep2 += l.p2()
            else:
                ep1 -= l.p2()
                ep2 -= l.p2()

    return ep1.x(), ep1.y(), ep2.x(), ep2.y()

class EdgeBezierPlacer():
    """Set Cubic Bezier points ep1 and ep2 for the edge if not already set."""

    def __init__(self):

        # placed edges keyed by (source_id lower, source_id higher) pair
        self.placed_edges = defaultdict(int)

    # return cubic bezier points ep1x, ep1y, ep2x, ep2y
    def place_cubic_bezier_points(self, src_id, src_x, src_y,
                                        dest_id, dest_x, dest_y):

        # identify key as (source_id lower, source_id higher) pair
        if src_id < dest_id:
            key = (src_id, dest_id)
        else:
            key = (dest_id, src_id)

        count = self.placed_edges[key]
        self.placed_edges[key] += 1
        return _place_points(src_id, src_x, src_y,
                             dest_id, dest_x, dest_y, count)

