from math import sqrt, pi, sin, cos
from PySide6.QtCore import QPointF
from edge_bezier_placer import EdgeBezierPlacer
# Adapted from https://github.com/svishrut93/Force-Directed-Graph-Drawing

def _adjacency_matrix(nodes, edges):
    # empty node adjacency matrix
    matrix = [len(nodes) * [0.0] for node in nodes]

    # connect edges
    for from_node, to_node in edges:
        matrix[to_node][from_node] = 0.1
        matrix[from_node][to_node] = 0.1

    print("adjacency matrix", matrix)
    return matrix

# push force
def _coulomb_force(xi, yi, xj, yj):
    beta = 0.0001
    dx = xj - xi
    dy = yj - yi
    ds = pow(dx * dx + dy * dy, 1.5)
    if ds == 0.0:
        # same location so apply some non-zero force
        return [0.0, 0.0]
    else:
        force = beta / ds
        return [-force * dx, -force * dy]

# pull force
def _hooke_force(xi, yi, xj, yj, dij):
    k = 1.0
    dx = xj - xi
    dy = yj - yi
    ds = sqrt(dx * dx + dy * dy)
    dl = ds - dij
    const = k * dl / ds
    return [const * dx, const * dy]

def _move_one(X, Y, VX, VY, adjacency_matrix):
    alpha = 1.0 # mass
    eta = 0.99 # dampening
    delta_t = .01
    ekint_x = 0.0
    ekint_y = 0.0
    num_nodes = len(X)

    for i in range(num_nodes):
        fx = 0.0
        fy = 0.0
        for j in range(num_nodes):
            if i == j:
                # node maps to self, no action
                continue
            if X[i] == X[j] and Y[i] == Y[j]:
                # nudge a coordinate, avoid division by zero, and retry
                print("force_directed_layout: unexpected placement")
                X[i] += 0.1
                continue
            dij = adjacency_matrix[i][j]
            fij = 0.0
            if dij == 0.0:
                fxij, fyij = _coulomb_force(X[i], Y[i], X[j], Y[j])
            else:
                fxij, fyij = _hooke_force(X[i], Y[i], X[j], Y[j], dij)
            fx += fxij
            fy += fyij
        VX[i] = (VX[i] + alpha * fx * delta_t) * eta
        VY[i] = (VY[i] + alpha * fy * delta_t) * eta
        ekint_x += alpha * (VX[i] * VX[i])
        ekint_y += alpha * (VY[i] * VY[i])

    for i in range(num_nodes):
        X[i] += VX[i] * delta_t
        Y[i] += VY[i] * delta_t

def _place_nodes(nodes, X, Y, k_x, k_y):
    for i, node in enumerate(nodes):
        node.setX(k_x * X[i])
        node.setY(k_y * Y[i])

def _place_edges(edges):
    placer = EdgeBezierPlacer()
    for edge in edges:
        ep1x, ep1y, ep2x, ep2y = placer.place_cubic_bezier_points(
                  edge.from_id, edge.from_node.x(), edge.from_node.y(),
                  edge.to_id, edge.to_node.x(), edge.to_node.y())
        edge.set_ep(ep1x, ep1y, ep2x, ep2y)

def set_initial_layout(nodes, edges, scale_x, scale_y):
    # place nodes around a circle
    count = len(nodes)
    k = pow(count, .7) # nonlinear radius determined experimentally
    X = [sin(2 * pi * i / count) * k for i in range(count)]
    Y = [-cos(2 * pi * i / count) * k for i in range(count)]
    kx = 0.45 * scale_x # scaling constant determined experimentally
    ky = 0.45 * scale_y
    _place_nodes(nodes, X, Y, kx, ky)
    _place_edges(edges)

def run_force_directed_layout(nodes, edges, scale_x, scale_y, num_iterations):

    # algorithmic scaling
    kx = scale_x * 15
    ky = scale_y * 15

    # establish node x,y lists
    X = [node.x() / kx for node in nodes]
    Y = [node.y() / ky for node in nodes]

    # get node indexes from node IDs
    node_indexes = dict()
    for i, node in enumerate(nodes):
        node_indexes[node.node_id] = i

    # empty adjacency matrix
    adjacency_matrix = [len(nodes) * [0.0] for node in nodes]

    # connect adjacency matrix edges
    for edge in edges:
        from_index = node_indexes[edge.from_id]
        to_index = node_indexes[edge.to_id]
        adjacency_matrix[from_index][to_index] = 0.1
        adjacency_matrix[to_index][from_index] = 0.1

    # run iterations
    num_nodes = len(nodes)
    VX = [0.0] * num_nodes # velocity in x for list
    VY = [0.0] * num_nodes
    for iteration in range(num_iterations):
        _move_one(X, Y, VX, VY, adjacency_matrix)

    # place node points and edge points
    _place_nodes(nodes, X, Y, kx, ky)
    _place_edges(edges)

