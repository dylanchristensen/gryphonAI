from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from settings import settings
from box_types import GANTT_CHART_BOX
from box import Box
from view_title import ViewTitle
from view_legend import ViewLegend
from view_gantt_chart_bars import ViewGanttChartBars
from font_helper import LEFT_PADDING, font_height

class ViewGanttChart(QObject):

    def __init__(self, background_box, gry_view):
        super().__init__()

        self.background_box = background_box
        self.box = Box(self, GANTT_CHART_BOX, gry_view["box"], background_box)

        # bars
        self.bars = ViewGanttChartBars(self.box, gry_view["plot"])

        # legend
        self.legend = ViewLegend(self.box, gry_view["legend"])

        # title
        self.title = ViewTitle(self.box, gry_view["title"])

        # maybe lay out and align the graph
        if not "x" in gry_view["box"]:
            self.legend.setX(0)
            self.legend.setY(-(self.legend.boundingRect().height()
                               + font_height()))
            self.legend.prepareGeometryChange()
            self.bars.setX(0)
            self.bars.setY(0)
            self.bars.prepareGeometryChange()
            self.title.align_above([self.legend, self.bars])
            self.title.prepareGeometryChange()

        # set box geometry
        self.box.reset_appearance()

    def get_gry(self):
        gry_view = {
                 "box":self.box.get_gry(),
                 "title":self.title.get_gry(),
                 "legend":self.legend.get_gry(),
                 "plot":self.bars.get_gry(),
                   }
        return gry_view

    def reset_appearance(self):
        self.title.reset_appearance()
        self.legend.reset_appearance()
        self.bars.reset_appearance()
        self.box.reset_appearance()

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.box.is_visible:
            return

        painter.save()
        painter.translate(self.box.pos())
        self.box.paint(painter, option, widget)
        for item in [self.title, self.legend, self.bars]:
            painter.save()
            painter.translate(item.pos())
            item.paint(painter, option, widget)
            painter.restore()
        painter.restore()

