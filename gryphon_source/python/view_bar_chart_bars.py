from math import sin, cos, pi
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainterPath, QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import VIEW_BAR_CHART_BARS_TYPE
from font_helper import text_width, text_widths, cell_height, \
                        font_descent, font_height, LEFT_PADDING
from settings import settings, preferred_pen
from view_legend import brush
from color_helper import contrasting_color, highlight_color
from strip_underscore import strip_underscore, strip_underscores
from main_graph_undo_redo import track_undo_press, track_undo_release

TEXT_ANGLE = 60
RADIAN_TEXT_ANGLE = TEXT_ANGLE*2*pi/360
ANGLED_TEXT_X = cos(RADIAN_TEXT_ANGLE)
ANGLED_TEXT_Y = sin(RADIAN_TEXT_ANGLE)

"""
Point (0, 0) is the lower-left corner of the first bar.  The bars stack
upwards and are scaled so the longest bar stack height reaches negative
total bar length.

Tick labels angle below the bars and read upward and to the right with
the lower-left point at negative x, positive y.

The x-axis title is below the tick labels, centered below the bars and labels.

We use terms compatible with vertical bar charts and rotated horizontal
bars which can be used as Gantt charts:
 * bar_length - Length of one bar.
 * bar_thickness - Thickness of one painted bar.
 * bar_gap - Gap between painted bars.
 * bar_spacing - Spacing from one bar to the next, equal to
                 bar_thickness + gar_gap.
 * bar_span - Span across bars consisting of thickness and gaps between.

 * bar_length_scaling - Scale factor to make stacked bar length fit bar_length
"""

class ViewBarChartBars(QGraphicsItem):

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

        # bar scaling to fit widest bar stack into max bar stack width
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
 
        # bar region consists of the bars, labels, and axis title
        # bars
        rectangle = QRectF(0, -self.bar_length, self.bar_span, self.bar_length)

        # tick labels
        kx = self.bar_thickness / 2
        ky = cell_height() / 2
        leftness = max([width * ANGLED_TEXT_X - self.bar_spacing * i - kx \
                        for i, width in enumerate(self.tick_label_widths)])
        lowerness = max(self.tick_label_widths) * ANGLED_TEXT_Y + ky
        rectangle = rectangle.united(QRectF(-leftness, 0,
                                     leftness + self.bar_span, lowerness))

        # bar rectangle tuples for painting
        self._set_bar_rectangles()

        # axis title
        title_width = text_width(self.axis_title)
        center = rectangle.x() + rectangle.width() / 2
        self.axis_title_x = center - title_width / 2
        self.axis_title_y = lowerness + font_height()
        rectangle = rectangle.united(QRectF(self.axis_title_x,
                            self.axis_title_y, title_width, 0))

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
        return VIEW_BAR_CHART_BARS_TYPE

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
        # bars rectangles are calculated on their side from top to
        # bottom and horizontally
        self.bar_rectangles = list()
        x_scale = self.bar_length_scaling
        for i, tick_value_list in enumerate(self.tick_values):
            # bars
            x = 0
            y = -self.bar_spacing * i
            for j, tick_value in enumerate(tick_value_list):
                w = round(tick_value * x_scale)
                self.bar_rectangles.append((QRectF(
                         x, y, w, -self.bar_thickness), tick_value, brush(j)))
                x += w

    def _mouse_transform(self, point):
        return QPointF(-point.y(), point.x() - self.bar_span)

    def paint(self, painter, _option, _widget):

        painter.save()

        if self._is_hovered:
            # highlight
            color = highlight_color(QColor(settings["background_color"]))
            painter.fillRect(self.bounding_rectangle, color)

        # paint the rectangles
        painter.save()
        painter.rotate(-90)
        painter.translate(0, self.bar_span)
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
        painter.restore()

        # tick labels
        painter.setPen(self.preferred_pen)
        widths = self.tick_label_widths
        theta = TEXT_ANGLE
        y = 0
        kx = (self.bar_thickness + font_height()) / 2
        for i, tick_label in enumerate(self.tick_labels):
            x = self.bar_spacing * i + kx
            rotated_x = widths[i] + 2 * LEFT_PADDING
            painter.save()
            painter.translate(x, y)
            painter.rotate(-theta)
            painter.drawText(-rotated_x, 0, tick_label)
            painter.restore()

        # axis title
        painter.drawText(self.axis_title_x, self.axis_title_y, self.axis_title)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.bounding_rectangle)

        # maybe paint hovered text on top
        painter.save()
        painter.rotate(-90)
        painter.translate(0, self.bar_span)
        for rect, tick_value, brush in self.bar_rectangles:
            if rect.contains(self.hover_pos):
                text = "%g"%tick_value
                bounding_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
                painter.setBrush(brush)
                painter.setPen(contrasting_color(brush.color()))
                painter.drawRect(bounding_rect)
                painter.drawText(rect, Qt.AlignCenter | Qt.TextDontClip, text)
        painter.restore()

        painter.restore()

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "bar chart bars", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self._is_hovered = True
        self.hover_pos = self._mouse_transform(event.pos())
        self.update()

    def hoverMoveEvent(self, event):
        self.hover_pos = self._mouse_transform(event.pos())
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.hover_pos = QPointF(-1, -1) # outside of bars
        self.update()

