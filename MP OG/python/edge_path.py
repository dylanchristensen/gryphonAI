from math import sin, cos, pi
from math import isnan
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath, QPolygonF

# get the path between node centers
def path_and_arrow(from_node, to_node, ep1, ep2, arrow_size):
    center_to_center_path = QPainterPath(from_node.pos())
    center_to_center_path.cubicTo(ep1, ep2, to_node.pos())
    if not center_to_center_path.length():
        # no path
        return center_to_center_path, QPolygonF()
    from_path = from_node.mouse_path.translated(from_node.pos())
    to_path = to_node.mouse_path.translated(to_node.pos())

    # scan from to_node to the half-way point looking for the first crossing
    divisions = 20
    for i in range(divisions - 1, 1, -1):
        if not to_path.contains(center_to_center_path.pointAtPercent(i/20)):
            break
    t = (i + 0.5) / divisions
    m = 1 / divisions / 4

    # use binary search for remaining precision
    for _i in range(10):
        arrow_tip = center_to_center_path.pointAtPercent(t)
        if to_path.contains(arrow_tip):
            # inside to_path so move back
            t -= m
        else:
            # outside to_path so move toward
            t += m
        m /= 2

    # create the arrow
    theta = center_to_center_path.angleAtPercent(t) * pi / 180
    if isnan(theta):
        # when the line is really short theta can be NaN
        theta = 0
    to_point = center_to_center_path.pointAtPercent(t)
    dest_p1 = to_point + QPointF(
               sin(theta - pi / 3) * arrow_size,
               cos(theta - pi / 3) * arrow_size)
    dest_p2 = to_point + QPointF(
               sin(theta - pi + pi / 3) * arrow_size,
               cos(theta - pi + pi / 3) * arrow_size)
    arrow = QPolygonF([to_point, dest_p1, dest_p2, to_point])

    return center_to_center_path, arrow

