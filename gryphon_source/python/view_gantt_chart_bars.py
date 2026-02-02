from math import sin, cos, pi
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainterPath, QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import VIEW_GANTT_CHART_BARS_TYPE
from font_helper import text_width, text_widths, cell_height, \
                        font_descent, font_height, LEFT_PADDING
from settings import settings, preferred_pen
from view_legend import brush
from color_helper import contrasting_color, highlight_color
from strip_underscore import strip_underscore, strip_underscores
from main_graph_undo_redo import track_undo_press, track_undo_release

"""
Point (0, 0) is the upper-left corner of the first bar.  Each bar set
aligns horizontally to the right and are scaled so the longest bar length
reaches total bar length.

Tick labels are to the left of the bars and are right-aligned to a padding
value x that is slightly less than zero and y that increases in value
downwards.

The y-axis title is centered to the left of the tick labels and is printed
vertically.

See view_bar_chart_bars.py for bar variable names.
"""

class ViewGanttChartBars(QGraphicsItem):

    def __init__(self, view_box, gry_plot):
        super().__init__()
        self.gry_plot = gry_plot

        self.view_box = view_box
        self.axis_title = strip_underscore(gry_plot["axis_title"])
        self.tick_labels = strip_underscores(gry_plot["tick_labels"])
        self.tick_values = gry_plot["tick_values"]
        if "x" in gry_plot:
            self.setPos(QPointF(gry_plot["x"], gry_plot["y"]))
        self.tick_label_widths = text_widths(self.tick_labels)

        # state
        self._is_hovered = False
        self.hover_pos = QPointF(-1, -1) # outside of bars

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

        self.reset_appearance()
        self.setParentItem(view_box)

    def reset_appearance(self):
        # bar dimensions
        self.bar_length = settings["bar_chart_bar_length"]
        self.bar_thickness = settings["bar_chart_bar_thickness"]
        self.bar_gap = settings["bar_chart_bar_gap"]
        self.bar_spacing = settings["bar_chart_bar_thickness"] \
                         + settings["bar_chart_bar_gap"]
        self.bar_span = self.bar_spacing \
                           * (len(self.tick_label_widths) - 1) \
                           + self.bar_thickness

        # bar scaling to fit widest bar stack into max bar width
        total_unnormalized_bar_length = max([sum(x) for x in self.tick_values])
        if total_unnormalized_bar_length == 0:
            # all bars can have 0 length
            total_unnormalized_bar_length = 1
        self.bar_length_scaling = settings["bar_chart_bar_length"] \
                                            / total_unnormalized_bar_length

        # pen color
        self.preferred_pen = preferred_pen()

        # border bar pen
        if settings["bar_chart_bar_use_border"]:
            self.border_bar_pen = QPen(self.preferred_pen.color(), 0)
        else:
            self.border_bar_pen = QPen(Qt.PenStyle.NoPen)

        # bar region consists of the bars, axis title, and the labels in between
        rectangle = QRectF(0, 0,
                           settings["bar_chart_bar_length"], self.bar_span)

        # bar rectangle tuples for painting
        self._set_bar_rectangles()

        # tick label coverage is not necessary because tick labels fit between
        # axis title and bar region

        # axis title
        axis_title_width = text_width(self.axis_title)
        title_x = -(max(self.tick_label_widths) + 2 * LEFT_PADDING)
        title_y = self.bar_span / 2 - axis_title_width / 2
        rectangle = rectangle.united(QRectF(title_x - cell_height(), title_y,
                                            1, axis_title_width))

        # tick labels in between do not impact bounds
        pass

        # bounds path
        self.bounds_path = QPainterPath()
        self.bounds_path.addRect(rectangle)

        # bounding rectangle
        pen_width = 1
        self.bounding_rectangle = rectangle.adjusted(
                        -pen_width/2, -pen_width/2, pen_width/2, pen_width/2)

        self.prepareGeometryChange()

    def get_gry(self):
        self.gry_plot["x"] = self.x()
        self.gry_plot["y"] = self.y()
        return self.gry_plot

    def type(self):
        return VIEW_GANTT_CHART_BARS_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse hovers when inside this rectangle
    def shape(self):
        return self.bounds_path

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

    def _set_bar_rectangles(self):
        # bars rectangles are calculated from top to bottom and horizontally
        self.bar_rectangles = list()
        x_scale = self.bar_length_scaling
        for i, tick_value_list in enumerate(self.tick_values):
            # bars
            x = 0
            y = self.bar_spacing * i
            for j, tick_value in enumerate(tick_value_list):
                w = round(tick_value * x_scale)
                self.bar_rectangles.append((QRectF(x, y, w, self.bar_thickness),
                                            tick_value, brush(j)))
                x += w

    def paint(self, painter, _option, _widget):

        painter.save()

        if self._is_hovered:
            # highlight
            color = highlight_color(QColor(settings["background_color"]))
            painter.fillRect(self.bounding_rectangle, color)

        # paint the rectangles
        for rect, _tick_value, brush in self.bar_rectangles:
            painter.setBrush(brush)
            painter.drawRect(rect)

        # paint the bar text
        for rect, tick_value, brush in self.bar_rectangles:
            painter.setPen(contrasting_color(brush.color()))
            tick_value_rounded = "%g"%round(tick_value,
                     settings["bar_chart_bar_annotation_decimal_places"])
            if text_width(tick_value_rounded) > rect.width():
                text = ""
            else:
                text = tick_value_rounded
            painter.drawText(rect, Qt.AlignCenter, text)

        # tick labels
        painter.setPen(self.preferred_pen)
        widths = self.tick_label_widths
        ky = self.bar_thickness / 2 + font_descent()
        for i, tick_label in enumerate(self.tick_labels):
            x = -(widths[i] + 2 * LEFT_PADDING)
            y = self.bar_spacing * i + ky
            painter.drawText(x, y, tick_label)

        # axis title
        x = -(2 * LEFT_PADDING + max(self.tick_label_widths) + cell_height())
        axis_title_width = text_width(self.axis_title)
        y = self.bar_span / 2 - axis_title_width / 2
        painter.save()
        painter.translate(x, y)
        painter.rotate(90)
        painter.drawText(0, 0, self.axis_title)
        painter.restore()

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.bounding_rectangle)

        # maybe paint hovered text on top
        for rect, tick_value, brush in self.bar_rectangles:
            if rect.contains(self.hover_pos):
                text = "%g"%tick_value
                bounding_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
                painter.setBrush(brush)
                painter.setPen(contrasting_color(brush.color()))
                painter.drawRect(bounding_rect)
                painter.drawText(rect, Qt.AlignCenter | Qt.TextDontClip, text)

        painter.restore()

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "Gantt chart bars", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self._is_hovered = True
        self.hover_pos = event.pos()
        self.update()

    def hoverMoveEvent(self, event):
        self.hover_pos = event.pos()
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.hover_pos = QPointF(-1, -1) # outside of bars
        self.update()

