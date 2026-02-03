from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from settings_manager import settings
from box_types import GANTT_CHART_BOX
from box import Box
from view_text import ViewText
from view_legend import ViewLegend
from view_gantt_chart_bars import ViewGanttChartBars
from font_helper import LEFT_PADDING, font_height

class ViewGanttChart(QObject):

    def __init__(self, background_box, gry_view):
        super().__init__()

        self.background_box = background_box
        self.gry_view = gry_view

        self.gantt_chart_box = Box(self, GANTT_CHART_BOX, gry_view["box"])

        # bars
        self.bars = ViewGanttChartBars(self.gantt_chart_box, gry_view["plot"])

        # legend
        self.legend = ViewLegend(self.gantt_chart_box, gry_view["legend"])

        # title
        self.title = ViewText(self.gantt_chart_box, gry_view["title"])

        # maybe lay out and align the graph
        if not "x" in gry_view["box"]:
            self.legend.setX(0)
            self.legend.setY(-(self.legend.boundingRect().height()
                               + font_height()))
            self.bars.setX(0)
            self.bars.setY(0)
            self.title.align_above([self.legend, self.bars])

            # indicate geometry change in any content in order to 
            # immediately correct changed gantt_chart_box geometry and box
            self.title.prepareGeometryChange()

            # align box to the right of the upper right edge
            # of the current parent bounds
            self.gantt_chart_box.align_to_right(background_box)

        self.gantt_chart_box.set_parent_box(background_box)

    def get_gry(self):
        gry_view = {
                 "box":self.gantt_chart_box.get_gry(),
                 "title":self.title.get_gry(),
                 "legend":self.legend.get_gry(),
                 "plot":self.bars.get_gry(),
                   }
        return gry_view

    def reset_appearance(self):
        self.title.reset_appearance()
        self.legend.reset_appearance()
        self.bars.reset_appearance()
        self.gantt_chart_box.reset_appearance()

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.gantt_chart_box.is_visible:
            return

        painter.save()
        painter.translate(self.gantt_chart_box.pos())
        self.gantt_chart_box.paint(painter, option, widget)
        for item in [self.title, self.legend, self.bars]:
            painter.save()
            painter.translate(item.pos())
            item.paint(painter, option, widget)
            painter.restore()
        painter.restore()

