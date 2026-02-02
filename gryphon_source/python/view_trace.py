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

        self.gry_trace = gry_trace
        self.background_box = background_box
        self.box = Box(self, TRACE_BOX, gry_trace["box"], background_box)

        # trace parts
        self.nodes = list()
        node_lookup = dict()
        for gry_node in gry_trace["nodes"]:
            node = Node(self.box, gry_node, self)
            self.nodes.append(node)
            node_lookup[node.node_id] = node

        self.edges = [Edge(self.box, gry_edge, node_lookup)
                      for gry_edge in gry_trace["edges"]]

    def get_gry(self):
        gry_trace = {
                 "box":self.box.get_gry(),
                 "nodes":[node.get_gry() for node in self.nodes],
                 "edges":[edge.get_gry() for edge in self.edges],
                 "mark": self.gry_trace["mark"],
                 "probability": self.gry_trace["probability"],
                         }
        return gry_trace

    def reset_appearance(self):
        for node in self.nodes:
            node.reset_appearance()
        for edge in self.edges:
            edge.reset_appearance()
        self.box.reset_appearance()

    def change_item_spacing(self, x_ratio, y_ratio):
        if x_ratio != 1.0:
            for node in self.nodes:
                node.setX(node.x() * x_ratio)
        if y_ratio != 1.0:
            for node in self.nodes:
                node.setY(node.y() * y_ratio)

    def align_node(self, node_to_align):
        node_x = node_to_align.x()
        node_y = node_to_align.y()
        max_align = 15
        new_node_dx = max_align
        new_node_x = None
        new_node_dy = max_align
        new_node_y = None
        for node in self.nodes:
            if node is node_to_align:
                continue
            # nearby x
            node_dx = abs(node.x() - node_x)
            if node_dx < new_node_dx:
                new_node_dx = node_dx
                new_node_x = node.x()

            # nearby y
            node_dy = abs(node.y() - node_y)
            if node_dy < new_node_dy:
                new_node_dy = node_dy
                new_node_y = node.y()

        # maybe align node
        if new_node_x != None:
           node_to_align.setX(new_node_x)
        if new_node_y != None:
           node_to_align.setY(new_node_y)

    # paint directly onto graph list rather than through QGraphicsScene
    def paint_items(self, painter, option, _widget):
        if not self.box.is_visible:
            return
        painter.save()
        painter.translate(self.box.pos())
        self.box.paint(painter, option, None)
        for node in self.nodes: # layer 0: node shadows
            painter.save()
            painter.translate(node.pos())
            node.node_shadow.paint(painter, option, None)
            painter.restore()
        for edge in self.edges: # layer 1: edges
            edge.paint(painter, option, None)
        for node in self.nodes: # layer 2: nodes
            # translate for this node
            painter.save()
            painter.translate(node.pos())
            node.paint(painter, option, None)
            painter.restore()
        for edge in self.edges: # layer 3: edge annotation
            painter.save()
            painter.translate(edge.center())
            edge.edge_annotation.paint(painter, option, None)
            painter.restore()
        painter.restore()

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
        set_collapsed_edges(self.background_box.scene())

    # set collapse or uncollapse for all nodes of specified R or C type
    def set_collapse_node_type(self, node_type):
        if node_type != "R" and node_type != "C":
            raise RuntimeError("bad")
        for node in self.nodes:
            if node.node_type == node_type and not node.collapse_below:
                collapse_below(node)
        set_collapsed_edges(self.background_box.scene())

    def set_uncollapse_node_type(self, node_type):
        if node_type != "R" and node_type != "C":
            raise RuntimeError("bad")
        for node in self.nodes:
            if node.node_type == node_type and node.collapse_below:
                uncollapse_below(node)
        set_collapsed_edges(self.background_box.scene())

