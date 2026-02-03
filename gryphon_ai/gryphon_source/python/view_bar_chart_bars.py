from math import sin, cos, pi
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import VIEW_BAR_CHART_BARS_TYPE
from font_helper import text_width, text_widths, cell_height, \
                        font_descent, font_height, LEFT_PADDING
from settings_manager import settings, preferred_pen
from view_legend import brush
from color_helper import text_color_name

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

        self.view_box = view_box
        self.axis_title = gry_plot["axis_title"]
        self.tick_labels = gry_plot["tick_labels"]

        self.tick_values = gry_plot["tick_values"]
        if "x" in gry_plot:
            self.setPos(QPointF(gry_plot["x"], gry_plot["y"]))
        self.tick_label_widths = text_widths(self.tick_labels)

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
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
        self.bounding_rectangle = rectangle.adjusted(-1, -1, 1, 1)

        self.prepareGeometryChange()

    def get_gry(self):
        gry_plot = {"axis_title":self.axis_title,
                    "tick_labels":self.tick_labels,
                    "tick_values":self.tick_values,
                    "x":self.x(),
                    "y":self.y(),
                   }
        return gry_plot

    def type(self):
        return VIEW_BAR_CHART_TYPE

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

    def paint(self, painter, _option, _widget):

        painter.save()

        # bars go from left to right painting rectangles from bottom up
        painter.setPen(self.border_bar_pen)
        y_scale = self.bar_length_scaling
        kx = (self.bar_thickness + font_height()) / 2
        for i, tick_value_list in enumerate(self.tick_values):
            # bars
            x = self.bar_spacing * i
            y = 0
            for j, tick_value in enumerate(tick_value_list):
                # bar
                painter.save()
                painter.translate(x, y)
                painter.rotate(-90)
                painter.setBrush(brush(j))

                h = round(tick_value * y_scale)

                painter.drawRect(0, 0, h, self.bar_thickness)
                painter.setPen(QColor(text_color_name(brush(j).color())))
                text = "%g"%tick_value
                if text_width(text) > h:
                    alignment_flag = Qt.AlignmentFlag.AlignLeft
                else:
                    alignment_flag = Qt.AlignmentFlag.AlignCenter
                painter.drawText(0, 0, h, self.bar_thickness,
                                            alignment_flag, text)
                painter.restore()

                y -= h

        # tick labels
        painter.setPen(self.preferred_pen)
        widths = self.tick_label_widths
        theta = TEXT_ANGLE
        y = 0
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
        painter.restore()

