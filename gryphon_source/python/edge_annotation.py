from PySide6.QtCore import QRectF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import EDGE_ANNOTATION_TYPE
from font_helper import bound_text_width_and_height
from color_helper import highlight_color

"""
Interfaces:
  * reset_appearance
"""
class EdgeAnnotation(QGraphicsItem):

    def __init__(self, label):
        super().__init__()
        # Putting parent in __init__ crashes with "pure virtual method called"
        # so we use setParentItem later.

        # put annotation above nodes and edges
        self.setZValue(3)

        self.label = label

        # allow superclass calls by defining values in reset_apearance
        self.reset_appearance("", "", 0, 0, QPointF(0,0), False, False)

    def type(self):
        return EDGE_ANNOTATION_TYPE

    def reset_appearance(self, background_color, edge_color, width, opacity,
                         position, is_highlighted, is_hovered):

        # label background
        self.label_background = QColor(background_color)
        self.label_background.setAlpha(opacity)

        # label foreground
        if is_highlighted:
            self.label_foreground = QColor(Qt.GlobalColor.red)
        else:
            self.label_foreground = QColor(edge_color)
        if is_hovered:
            self.label_foreground = highlight_color(self.label_foreground)

        # bounding rectangle
        w, h = bound_text_width_and_height(self.label, width)
        self.bounding_rect = QRectF(-w / 2, -h / 2, w, h)
        self.prepareGeometryChange()

        self.setPos(position)

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        return QPainterPath()

    def paint(self, painter, _option, _widget):
        if not self.label:
           # do not paint a small background around nothing
           return

        painter.save()

        # background
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(self.label_background))
        s = 2
        r = 4
        rect = self.bounding_rect.adjusted(-s, 0, s, 0)
        painter.drawRoundedRect(rect, r, r)

        # simulate fading opacity
        d =1
        rect = rect.adjusted(-d, -d, d, d)
        painter.drawRoundedRect(rect, r, r)

        # foreground
        painter.setPen(self.label_foreground)
        painter.drawText(self.bounding_rect, Qt.AlignmentFlag.AlignCenter
                   | Qt.TextFlag.TextWordWrap, self.label)

        painter.restore()

