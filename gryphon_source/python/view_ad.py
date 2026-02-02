from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from settings import settings
from box_types import AD_BOX
from box import Box
from view_title import ViewTitle
from view_ad_node import ViewADNode
from view_ad_edge import ViewADEdge
from view_ad_place_edges import place_edges

class ViewAD(QObject):

    def __init__(self, background_box, gry_ad):
        super().__init__()

        self.background_box = background_box
        self.box = Box(self, AD_BOX, gry_ad["box"], background_box)

        self.nodes = list()
        self.edges = list()

        # view graph title
        self.title = ViewTitle(self.box, gry_ad["title"])

        # nodes
        node_lookup = dict()
        for gry_node in gry_ad["nodes"]:
            node = ViewADNode(self.box, gry_node)
            self.nodes.append(node)
            node_lookup[node.node_id] = node

        # edges
        for gry_edge in gry_ad["edges"]:
            edge = ViewADEdge(self.box, gry_edge, node_lookup)
            self.edges.append(edge)

        # maybe set all the edge coordinates
        if not "x" in gry_ad["box"]:
            place_edges(self.nodes, self.edges)
            self.title.align_above(self.nodes)
            self.title.prepareGeometryChange()

        # set box geometry
        self.box.reset_appearance()

    def get_gry(self):
        gry_ad = {
                 "box":self.box.get_gry(),
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
        self.box.reset_appearance()

    def change_ad_item_spacing(self, x_ratio, y_ratio):
        if x_ratio != 1.0 or y_ratio != 1.0:
            for node in self.nodes:
                node.setX(node.x() * x_ratio)
                node.setY(node.y() * y_ratio)

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.box.is_visible:
            return

        painter.save()
        painter.translate(self.box.pos())
        self.box.paint(painter, option, widget)
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

