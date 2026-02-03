from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from settings_manager import settings
from box_types import GRAPH_BOX
from box import Box
from view_text import ViewText
from view_graph_node import ViewGraphNode
from view_graph_edge import ViewGraphEdge
from force_directed_layout import set_initial_layout, run_force_directed_layout

def _upper_left(nodes):
    if nodes:
        x = min([node.x() for node in nodes])
        y = min([node.y() for node in nodes])
        return x, y
    else:
        return 0, 0

class ViewGraph(QObject):

    def align_circular(self):
        scale_x = settings["graph_node_h_spacing"]
        scale_y = settings["graph_node_v_spacing"]
        set_initial_layout(self.nodes, self.edges, scale_x, scale_y)

    def align_force_directed(self):
        scale_x = settings["graph_node_h_spacing"]
        scale_y = settings["graph_node_v_spacing"]
        run_force_directed_layout(self.nodes, self.edges, scale_x, scale_y,
                                  10000)

    def align_force_directed_x10(self):
        scale_x = settings["graph_node_h_spacing"]
        scale_y = settings["graph_node_v_spacing"]
        run_force_directed_layout(self.nodes, self.edges, scale_x, scale_y,
                                  100000)

    def __init__(self, background_box, gry_graph):
        super().__init__()

        self.background_box = background_box
        self.gry_graph = gry_graph

        self.graph_box = Box(self, GRAPH_BOX, gry_graph["box"])

        self.nodes = list()
        self.edges = list()

        # view graph title
        self.title = ViewText(self.graph_box, gry_graph["title"])

        # nodes
        node_lookup = dict()
        for gry_node in gry_graph["nodes"]:
            node = ViewGraphNode(self.graph_box, gry_node)
            self.nodes.append(node)
            node_lookup[node.node_id] = node

        # edges
        for gry_edge in gry_graph["edges"]:
            edge = ViewGraphEdge(self.graph_box, gry_edge, node_lookup)
            self.edges.append(edge)

        # maybe lay out and align the graph
        if not "x" in gry_graph["box"]:
            self.align_circular()
            self.title.align_above(self.nodes)

            # indicate geometry change in any content in order to 
            # immediately correct changed graph_box geometry and box
            self.title.prepareGeometryChange()

            # align box to the right of the upper right edge
            # of the current parent bounds
            self.graph_box.align_to_right(background_box)

        self.graph_box.set_parent_box(background_box)

    def get_gry(self):
        gry_graph = {
                 "box":self.graph_box.get_gry(),
                 "title":self.title.get_gry(),
                 "nodes":[node.get_gry_node() for node in self.nodes],
                 "edges":[edge.get_gry_edge() for edge in self.edges],
                         }
        return gry_graph

    def reset_appearance(self):
        self.title.reset_appearance()
        for node in self.nodes:
            node.reset_appearance()
        for edge in self.edges:
            edge.reset_appearance()
        self.graph_box.reset_appearance()

    def change_item_spacing(self, x_ratio, y_ratio):
        if x_ratio != 1.0:
            self.title.setX(self.title.x() * x_ratio)
            for node in self.nodes:
                node.setX(node.x() * x_ratio)
        if y_ratio != 1.0:
            self.title.setY(self.title.y() * y_ratio)
            for node in self.nodes:
                node.setY(node.y() * y_ratio)

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.graph_box.is_visible:
            return

        painter.save()
        painter.translate(self.graph_box.pos())
        self.graph_box.paint(painter, option, widget)
        for edge in self.edges:
            edge.paint(painter, option, widget)
        for node in self.nodes:
            painter.save()
            painter.translate(node.pos())
            node.paint(painter, option, widget)
            painter.restore()
        painter.save()
        painter.translate(self.title.pos())
        self.title.paint(painter, option, widget)
        painter.restore()
        painter.restore()

