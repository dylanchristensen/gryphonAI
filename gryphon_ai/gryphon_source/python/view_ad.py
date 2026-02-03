from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from settings_manager import settings
from box_types import AD_BOX
from box import Box
from view_text import ViewText
from view_ad_node import ViewADNode
from view_ad_edge import ViewADEdge
from edge_angular_placer import place_edges

class ViewAD(QObject):

    def __init__(self, background_box, gry_ad):
        super().__init__()

        self.background_box = background_box
        self.gry_ad = gry_ad

        self.ad_box = Box(self, AD_BOX, gry_ad["box"])

        self.nodes = list()
        self.edges = list()

        # view graph title
        self.title = ViewText(self.ad_box, gry_ad["title"])

        # nodes
        node_lookup = dict()
        for gry_node in gry_ad["nodes"]:
            node = ViewADNode(self.ad_box, gry_node)
            self.nodes.append(node)
            node_lookup[node.node_id] = node

        # edges
        for gry_edge in gry_ad["edges"]:
            edge = ViewADEdge(self.ad_box, gry_edge, node_lookup)
            self.edges.append(edge)

        # maybe set all the edge coordinates
        if not "x" in gry_ad["box"]:
            place_edges(self.nodes, self.edges)
            self.title.align_above(self.nodes)

            # indicate geometry change in any content in order to 
            # immediately correct changed ad_box geometry and box
            self.title.prepareGeometryChange()

            # align box to the right of the upper right edge
            # of the current parent bounds
            self.ad_box.align_to_right(background_box)

        self.ad_box.set_parent_box(background_box)

    def get_gry(self):
        gry_ad = {
                 "box":self.ad_box.get_gry(),
                 "title":self.title.get_gry(),
                 "nodes":[node.get_gry_node() for node in self.nodes],
                 "edges":[edge.get_gry_edge() for edge in self.edges],
                         }
        return gry_ad

    def reset_appearance(self):
        self.title.reset_appearance()
        for node in self.nodes:
            node.reset_appearance()
        for edge in self.edges:
            edge.reset_appearance()
        self.ad_box.reset_appearance()

    def change_item_spacing(self, x_ratio, y_ratio):
        if x_ratio != 1.0:
            self.title.setX(self.title.x() * x_ratio)
            # set edges first and let node call edge reset_appearance
            for edge in self.edges:
                edge.ep1.setX(edge.ep1.x() * x_ratio)
                edge.ep2.setX(edge.ep2.x() * x_ratio)
            for node in self.nodes:
                node.setX(node.x() * x_ratio)
        if y_ratio != 1.0:
            self.title.setY(self.title.y() * y_ratio)
            for edge in self.edges:
                edge.ep1.setY(edge.ep1.y() * y_ratio)
                edge.ep2.setY(edge.ep2.y() * y_ratio)
            for node in self.nodes:
                node.setY(node.y() * y_ratio)

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.ad_box.is_visible:
            return

        painter.save()
        painter.translate(self.ad_box.pos())
        self.ad_box.paint(painter, option, widget)
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

