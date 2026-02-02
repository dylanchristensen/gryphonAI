from edge_bezier_placer import EdgeBezierPlacer
from verbose import verbose
from edge import Edge
"""Provides services:
collapse_below(node): collapse_below starting at the given node
uncollapse_below(node): uncollapse at and below node
at_and_below_in(node): for selecting all IN nodes at and below node
at_and_above_in_uncollapsed(node): for selecting all IN nodes at and above node
"""

# A node's parent IN nodes
def _parent_in_nodes(node):
    parents = list()
    for edge in node.edge_list:
        if edge.to_node == node and edge.relation == "IN":
            parents.append(edge.from_node)
    return parents

# A node's child IN nodes
def _child_in_nodes(node):
    children = list()
    for edge in node.edge_list:
        if edge.from_node == node and edge.relation == "IN":
            children.append(edge.to_node)
    return children

# collapse_below starting at the given node
def collapse_below(node):
    if node.node_type == "R" or node.node_type == "C":
        # mark Root and Composite nodes with collapse_below flag
        node.collapse_below = True

    # get child IN nodes
    children = _child_in_nodes(node)

    for child in children:

        # see if the child has a parent that is not collapsed below
        parents = _parent_in_nodes(child)
        can_collapse_child = True
        for parent in parents:
            # Root and Composite parents can collapse below
            if parent.node_type == "R" or parent.node_type == "C":
                if not parent.collapse_below:
                    # do not collapse below this child
                    can_collapse_child = False

        if can_collapse_child:
            child.collapse = True
            collapse_below(child)

# uncollapse at and below node
def uncollapse_below(node):
    # uncollapse the node
    node.collapse = False
    node.collapse_below = False

    # uncollapse the node's IN children
    children = _child_in_nodes(node)

    for child in children:
        uncollapse_below(child)

def _below_in(node, node_set):
    children = _child_in_nodes(node)
    for child in children:
        node_set.add(child)
        _below_in(child, node_set)

# for selecting all IN nodes at and below node
def at_and_below_in(node):
    node_set = set()
    node_set.add(node)
    _below_in(node, node_set)
    return node_set

# ancestors IN bout not collapsed
def _above_in_uncollapsed(node, node_set):
    parents = _parent_in_nodes(node)
    for parent in parents:
        if not parent.collapse:
            node_set.add(parent)
        else:
            # follow above this parent
            _above_in_uncollapsed(parent, node_set)

# for selecting all IN nodes at and above node
def at_and_above_in_uncollapsed(node):
    node_set = set()
    if not node.collapse:
        node_set.add(node)
    else:
        _above_in_uncollapsed(node, node_set)
    return node_set

# get the set of removable_edges and addable_edge_pairs
def _collapsed_edges(trace):
    if verbose():
        print("_collapsed_edges")

    # make sure there are edges to work with
    if not trace.edges:
        return (list(), list())

    # identify the existing collapsed from_node, to_node edge pairs
    existing_edge_pairs = set()
    existing_edges = dict()
    for edge in trace.edges:
        if edge.relation == "COLLAPSED_FOLLOWS":
            existing_edge_pairs.add((edge.from_node, edge.to_node))
            existing_edges[(edge.from_node, edge.to_node)] = edge
            if verbose():
                print("identified existing edge      %s     to     %s" % (
                      edge.from_node.label, edge.to_node.label))

    # calculate the set of from_node, to_node edge pairs
    edge_pairs = set()
    for edge in trace.edges:
        if edge.relation == "FOLLOWS" and (edge.from_node.collapse
                                           or edge.to_node.collapse):
            if verbose():
                print("will add COLLAPSED_FOLLOWS to bridge: %s    to    %s" % (
                      edge.from_node.label, edge.to_node.label))
            # source and dest nodes
            from_node_set = at_and_above_in_uncollapsed(edge.from_node)
            to_node_set = at_and_above_in_uncollapsed(edge.to_node)
            for from_node in from_node_set:
                for to_node in to_node_set:
                    if from_node != to_node:
                        if verbose():
                            print("adding    %s        to         %s" % (
                                  from_node.label, to_node.label))
                        edge_pairs.add((from_node, to_node))

    # identify edges that need removed
    removable_edges = list()
    removable_pairs = existing_edge_pairs - edge_pairs
    for from_node, to_node in removable_pairs:
        removable_edges.append(existing_edges[(from_node, to_node)])

    # identify edges that need added
    addable_edge_pairs = edge_pairs - existing_edge_pairs

    return (removable_edges, addable_edge_pairs)

# diagnostics
def _print_totals(nodes, edges):
    if not edges:
        print("Totals: None, empty graph.")
        return

    # total items in QGraphicsScene
    graph_main_scene = edges[0].scene()
    scene_item_total = len(graph_main_scene.items())

    # nodes + edges in this trace
    trace_total = len(nodes) + len(edges)

    # edge_list_total
    edge_list_total = 0
    for node in nodes:
        edge_list_total += len(node.edge_list)

    print("Totals: scene: %d, graph: %d, graph nodes: %d, "
          "graph edges: %d, edge list total: %d" % (
               scene_item_total, trace_total,
               len(nodes), len(edges), edge_list_total))

# redo the list of collapsed edges in edges[] based on what is collapsed
def set_collapsed_edges(scene):
    trace = scene.graph_item.trace
    if verbose():
        _print_totals(trace.nodes, trace.edges)

    removable_edges, addable_edge_pairs = _collapsed_edges(trace)

    # create and add the new addable edges
    placer = EdgeBezierPlacer()
    for from_node, to_node in addable_edge_pairs:
        ep1_x, ep1_y, ep2_x, ep2_y = placer.place_cubic_bezier_points(
              from_node.node_id, from_node.x(), from_node.y(),
              to_node.node_id, to_node.x(), to_node.y())
        node_lookup = {from_node.node_id:from_node, to_node.node_id:to_node}
        addable_edge = Edge(trace.box,
                            {"from_id":from_node.node_id,
                             "relation":"COLLAPSED_FOLLOWS",
                             "to_id":to_node.node_id,
                             "label":"",
                             "ep1_x":ep1_x, "ep1_y":ep1_y,
                             "ep2_x":ep2_x, "ep2_y":ep2_y,
                            },
                            node_lookup)
        trace.edges.append(addable_edge)
        addable_edge.reset_appearance()

    # remove any discontinued FOLLOWS edges
    for removable_edge in removable_edges:
        removable_edge.from_node.edge_list.remove(removable_edge)
        removable_edge.to_node.edge_list.remove(removable_edge)
        trace.edges.remove(removable_edge)
        removable_edge.setParentItem(None)

    # reset appearance
    trace.reset_appearance()

    # edge items changed so reset the scene
    scene.set_scene()

    if verbose():
        _print_totals(trace.nodes, trace.edges)

