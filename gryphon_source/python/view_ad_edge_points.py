from math import sqrt
from PySide6.QtCore import QPointF
from view_ad_node import START_TYPE, END_TYPE, DECISION_TYPE

def _edge_end(edge_start, edge_vector):
    # find edge end direction
    if edge_start == "h":
        if len(edge_vector) % 2 == 1:
            edge_end = "h"
        else:
            edge_end = "v"
    elif edge_start == "v":
        if len(edge_vector) % 2 == 0:
            edge_end = "h"
        else:
            edge_end = "v"
    else:
        raise RuntimeError("bad")
    return edge_end

def _fraction(node_type, x_or_y, node_x_or_y, w_or_h):
    if node_type == DECISION_TYPE:
        # diamond shape
        return 1.0 - abs(x_or_y - node_x_or_y) / (w_or_h / 2)

    elif node_type == START_TYPE or node_type == END_TYPE:
        # circular
        return sqrt(abs((w_or_h / 2) ** 2 - (x_or_y - node_x_or_y) ** 2)) \
                          / (w_or_h / 2)
    else:
        # rectangular
        return 1.0

# get start_x, start_y, end_x, end_y
def _endpoints(edge):
    from_node = edge.from_node
    to_node = edge.to_node
    edge_start = edge.edge_start
    edge_vector = edge.edge_vector
    gap = 0.4 
    if not edge_vector:
        raise RuntimeError("bad")

    # x0, y0 starting h toward next x
    if edge_start == "h":
        y0 = edge_vector[0]

        if len(edge_vector) == 1:
            next_x = to_node.x()
        else:
            next_x = edge_vector[1]

        fraction = _fraction(from_node.node_type, y0, from_node.y(),
                             from_node.h)
        if from_node.x() < next_x:
            x0 = from_node.x() + from_node.w / 2 * fraction + gap
        else:
            x0 = from_node.x() - from_node.w / 2 * fraction - gap

    # x0, y0 starting v toward next y
    elif edge_start == "v":
        x0 = edge_vector[0]

        if len(edge_vector) <= 1:
            next_y = to_node.y()
        else:
            next_y = edge_vector[1]
        fraction = _fraction(from_node.node_type, x0, from_node.x(),
                             from_node.w)
        if from_node.y() < next_y:
            y0 = from_node.y() + from_node.h / 2 * fraction + gap
        else:
            y0 = from_node.y() - from_node.h / 2 * fraction - gap

    else:
        raise RuntimeError("bad")

    # find edge end direction
    edge_end = _edge_end(edge_start, edge_vector)

    # xn, yn for h from previous x
    if edge_end == "h":
        yn = edge_vector[-1]

        if len(edge_vector) == 1:
            previous_x = from_node.x()
        else:
            previous_x = edge_vector[-2]

        fraction = _fraction(to_node.node_type, yn, to_node.y(),
                             to_node.h)
        if previous_x < to_node.x():
            xn = to_node.x() - to_node.w / 2 * fraction - gap
        else:
            xn = to_node.x() + to_node.w / 2 * fraction + gap

    # xn, yn for v from previous y
    elif edge_end == "v":
        xn = edge_vector[-1]

        if len(edge_vector) == 1:
            previous_y = from_node.y()
        else:
            previous_y = edge_vector[-2]

        fraction = _fraction(to_node.node_type, xn, to_node.x(),
                             to_node.w)
        if previous_y < to_node.y():
            yn = to_node.y() - to_node.h / 2 * fraction - gap
        else:
            yn = to_node.y() + to_node.h / 2 * fraction + gap

    else:
        raise RuntimeError("bad")

    return x0, y0, xn, yn

def edge_to_points(edge):
    edge_vector = edge.edge_vector
    edge_start = edge.edge_start

    if not edge_vector:
        # no points
        return []

    edge_points = list()

    # endpoints
    x0, y0, xn, yn = _endpoints(edge)

    # start edge point
    edge_points.append(QPointF(x0, y0))

    # middle edge points
    xi = x0
    yi = y0

    for i in range(1, len(edge_vector)):
        if (edge_start == "h" and i % 2 == 0) \
                  or (edge_start == "v" and i % 2 == 1):
            # h
            yi = edge_vector[i]
        else:
            # v
            xi = edge_vector[i]
        edge_points.append(QPointF(xi, yi))

    # final edge point
    edge_points.append(QPointF(xn, yn))

    return edge_points

def points_to_vector(edge_start, points):
    if edge_start == "h":
        mod_check = 0
    elif edge_start == "v":
        mod_check = 1
    else:
        raise RuntimeError("bad")
    vector = list()
    for i in range(len(points)):
        if i % 2 == mod_check:
            vector.append(points[i].y())
        else:
            vector.append(points[i].x())
    return vector

def points_to_grip_points(edge_points):
    grip_points = list()
    for i in range(1, len(edge_points)):
        grip_points.append(QPointF(
                    (edge_points[i-1].x() + edge_points[i].x()) / 2,
                    (edge_points[i-1].y() + edge_points[i].y()) / 2))
    return grip_points

# make the adjacent edge segment be in the same position relative to the node
def adjusted_edge_segment(node, edge, dx, dy):
    adjusted_edge_vector = edge.edge_vector.copy()
    if len(edge.edge_vector) >= 2:
        # there is an adjacent edge segment to move
        if edge.from_node == node:
            # move the first segment
            if edge.edge_start == "h":
                adjusted_edge_vector[0] += dy
            elif edge.edge_start == "v":
                adjusted_edge_vector[0] += dx
            else:
                raise RuntimeError("bad")

        elif edge.to_node == node:
            # move the last segment
            edge_end = _edge_end(edge.edge_start, adjusted_edge_vector)
            if edge_end == "h":
                adjusted_edge_vector[-1] += dy
            elif edge_end == "v":
                adjusted_edge_vector[-1] += dx
            else:
                raise RuntimeError("bad")
        else:
            raise RuntimeError("bad")

    elif len(edge.edge_vector) == 1 and edge.from_node == node:
        # move the first segment
        if edge.edge_start == "h":
            adjusted_edge_vector[0] += dy
        elif edge.edge_start == "v":
            adjusted_edge_vector[0] += dx
        else:
            raise RuntimeError("bad")

    else:
        # no change
        pass

    return adjusted_edge_vector

# returns edge_start, edge_vector, changes
# where changes is a list of tuple: "insert"|"remove", value
def adjusted_edge_vector(edge, suggested_edge_start, suggested_edge_vector):
    from_node = edge.from_node
    to_node = edge.to_node
    edge_start = suggested_edge_start
    edge_vector = suggested_edge_vector.copy()
    changes = list()

    # maybe add horizontal when there are no segments
    if not edge_vector and not from_node.spans_x(to_node.x()):
        edge_start = "h"
        edge_vector.insert(0, from_node.y())
        changes.append(("insert", 0))

    # maybe add vertical when there are no segments
    if not edge_vector and not from_node.spans_y(to_node.y()):
        edge_start = "v"
        edge_vector.insert(0, from_node.x())
        changes.append(("insert", 0))

    # maybe add vertical at start by adding x
    if edge_vector and edge_start == "h" \
                                 and not from_node.spans_y(edge_vector[0]):
        edge_start = "v"
        edge_vector.insert(0, from_node.x())
        changes.append(("insert", 0))

    # maybe add horizontal at start by adding y
    if edge_vector and edge_start == "v" \
                                 and not from_node.spans_x(edge_vector[0]):
        edge_start = "h"
        edge_vector.insert(0, from_node.y())
        changes.append(("insert", 0))

    # maybe add vertical at end by adding x
    edge_end = _edge_end(edge_start, edge_vector)
    if edge_vector and edge_end == "h" \
                                 and not to_node.spans_y(edge_vector[-1]):
        index = len(edge_vector)
        edge_vector.insert(index, to_node.x())
        changes.append(("insert", index))

    # maybe add horizontal at end by adding y
    edge_end = _edge_end(edge_start, edge_vector)
    if edge_vector and edge_end == "v" \
                                 and not to_node.spans_x(edge_vector[-1]):
        index = len(edge_vector)
        edge_vector.insert(index, to_node.y())
        changes.append(("insert", index))

    # maybe repeatedly remove segments at start
    while True:
        if edge_start == "h" and len(edge_vector) >= 2 \
                          and from_node.spans_x(edge_vector[1]):
            edge_start = "v"
            del edge_vector[0]
            changes.append(("remove", 0))
        elif edge_start == "v" and len(edge_vector) >= 2 \
                          and from_node.spans_y(edge_vector[1]):
            edge_start = "h"
            del edge_vector[0]
            changes.append(("remove", 0))
        else:
            # nothing removed so done
            break

    # maybe repeatedly remove segments at end
    while True:
        edge_end = _edge_end(edge_start, edge_vector)
        if edge_end == "h" and len(edge_vector) >= 2 \
                          and to_node.spans_x(edge_vector[-2]):
            index = len(edge_vector) - 1
            del edge_vector[index]
            changes.append(("remove", index))
        elif edge_end == "v" and len(edge_vector) >= 2 \
                          and to_node.spans_y(edge_vector[-2]):
            index = len(edge_vector) - 1
            del edge_vector[index]
            changes.append(("remove", index))
        else:
            # nothing removed so done
            break

    # maybe remove all segments because nodes overlap
    if from_node.spans_x(to_node.x()) and from_node.spans_y(to_node.y()):
        while edge_vector:
            del edge_vector[0]
            changes.append(("remove", 0))

    # maybe remove really short inner segments
    done = False
    while not done:
        done = True
        if len(edge_vector) > 3:
            # look for short inner segments
            if abs(edge_vector[0] - edge_vector[2]) < 2:
                # segments 0 and 2 align so remove segments 1 and 2
                # retaining the coordinate at 0 adjacent to the source node
                del edge_vector[1]
                changes.append(("remove", 1))
                del edge_vector[1]
                changes.append(("remove", 1))
                done = False
            else:
                # look for adjacent segments at indexes 1 and above
                for i in range(1, len(edge_vector) - 2):
                    if abs(edge_vector[i] - edge_vector[i+2]) < 2:
                        # segments i and i+2 align so remove segments
                        # i+1 and i+2 retaining the coordinate adjacent
                        # to the destination node
                        del edge_vector[i+1]
                        changes.append(("remove", i+1))
                        del edge_vector[i+1]
                        changes.append(("remove", i+1))
                        done = False
                        break

    return edge_start, edge_vector, changes

