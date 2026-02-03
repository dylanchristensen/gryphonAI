from PySide6.QtCore import QObject
from box_types import TRACE_BOX
from box import Box
from node import Node
from edge import Edge
from trace_collapse_helpers import collapse_below, uncollapse_below, \
                                   set_collapsed_edges

# Note: mark and probability are left in gry_trace.  They do not change
# and they are referenced by sort and filter without needing to initialize
# the graph_item.

# one trace
class ViewTrace(QObject):

    def __init__(self, background_box, gry_trace):
        super().__init__()

        self.background_box = background_box
        self.gry_trace = gry_trace

        self.trace_box = Box(self, TRACE_BOX, gry_trace["box"])

        # trace parts
        self.layout = gry_trace["layout"]
        self.nodes = list()
        node_lookup = dict()
        for gry_node in gry_trace["nodes"]:
            node = Node(self.trace_box, gry_node, self)
            self.nodes.append(node)
            node_lookup[node.node_id] = node

        self.edges = [Edge(self.trace_box, gry_edge, node_lookup)
                      for gry_edge in gry_trace["edges"]]

        self.trace_box.set_parent_box(background_box)

    def get_gry(self):
        gry_trace = {
                 "box":self.trace_box.get_gry(),
                 "nodes":[node.get_gry() for node in self.nodes],
                 "edges":[edge.get_gry() for edge in self.edges],
                 "mark": self.gry_trace["mark"],
                 "layout": self.layout,
                 "probability": self.gry_trace["probability"],
                         }
        return gry_trace

    def reset_appearance(self):
        for node in self.nodes:
            node.reset_appearance()
        for edge in self.edges:
            edge.reset_appearance()
        self.trace_box.reset_appearance()

    def change_item_spacing(self, x_ratio, y_ratio):
        if x_ratio != 1.0:
            for node in self.nodes:
                node.setX(node.x() * x_ratio)
        if y_ratio != 1.0:
            for node in self.nodes:
                node.setY(node.y() * y_ratio)

    # paint directly using paint_graph_item rather than through QGraphicsScene
    def paint_items(self, painter, option, _widget):
        if not self.trace_box.is_visible:
            return
        painter.save()
        painter.translate(self.trace_box.pos())
        self.trace_box.paint(painter, option, None)
        for edge in self.edges:
            edge.paint(painter, option, None)
        for node in self.nodes:
            # translate for this node
            painter.save()
            painter.translate(node.pos())
            node.paint(painter, option, None)
            painter.restore()
        painter.restore()

    # select all nodes
    def select_all_nodes(self):
        for node in self.nodes:
            node.setSelected(True)

    # toggle hide/unhide on selected nodes
    def toggle_hide_unhide(self):
        for node in self.nodes:
            if node.isSelected():
                node.hide = not node.hide

                # set appearance on changed node
                node.reset_appearance()

        # simpler to set appearance on all edges
        for edge in self.edges:
            edge.reset_appearance()

    def hide_node(self, node, do_hide):
        node.hide = do_hide
        node.reset_appearance()

        # set appearance on edges
        for edge in node.edge_list:
            edge.reset_appearance()

    def unhide_all_nodes(self):
        for node in self.nodes:
            node.hide = False

            # set appearance on changed node
            node.reset_appearance()

        # simpler to set appearance on all edges
        for edge in self.edges:
            edge.reset_appearance()

    # toggle collapse/uncollapse on selected Root and Composite nodes
    def toggle_collapse_uncollapse(self):
        for node in self.nodes:
            if node.isSelected():
                if node.node_type == "R" or node.node_type == "C":
                    if node.collapse_below:
                        uncollapse_below(node)
                    else:
                        collapse_below(node)
        set_collapsed_edges(self)

    # set collapse or uncollapse for all nodes of specified R or C type
    def set_collapse_node_type(self, node_type):
        if node_type != "R" and node_type != "C":
            raise RuntimeError("bad")
        for node in self.nodes:
            if node.node_type == node_type and not node.collapse_below:
                collapse_below(node)
        set_collapsed_edges(self)

    def set_uncollapse_node_type(self, node_type):
        if node_type != "R" and node_type != "C":
            raise RuntimeError("bad")
        for node in self.nodes:
            if node.node_type == node_type and node.collapse_below:
                uncollapse_below(node)
        set_collapsed_edges(self)

