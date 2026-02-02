# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

import math
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QGraphicsView
from settings import settings
from preferences import DEFAULT_GRAPH_PANE_SCALE
from os_compatibility import pure_shifted_left_button_down

class MainGraphView(QGraphicsView):

    def __init__(self, signal_graphs_loaded):
        super().__init__()

        self.viewport_cursor = Qt.CursorShape.ArrowCursor
        self.setViewportUpdateMode(
                       QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(
                           QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # enable user rectangular selection
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.viewport().setCursor(self.viewport_cursor)
        self.setMinimumSize(200, 200)

        # connect to reset viewport to top when graph list is loaded
        signal_graphs_loaded.connect(self._reset_viewport)

    # _rescale by scale factor
    def _rescale(self, scale_factor):
        self.scale(scale_factor, scale_factor)

    def keyPressEvent(self, event):

        # keystroke controls
        key = event.key()
        v = self.verticalScrollBar().value()
        h = self.horizontalScrollBar().value()

        if key == Qt.Key.Key_Up:
            self.verticalScrollBar().setValue(v-20)
        elif key == Qt.Key.Key_Down:
            self.verticalScrollBar().setValue(v+20)
        elif key == Qt.Key.Key_Left:
            self.horizontalScrollBar().setValue(h-20)
        elif key == Qt.Key.Key_Right:
            self.horizontalScrollBar().setValue(h+20)
        elif key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal:
            self.scale_view_in()
        elif key == Qt.Key.Key_Minus or key == Qt.Key.Key_Underscore:
            self.scale_view_out()
        elif key == Qt.Key.Key_Space or key == Qt.Key.Key_Enter:
            pass

        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # view mode
        if pure_shifted_left_button_down(event):
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.viewport().setCursor(self.viewport_cursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(self.viewport_cursor)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # view mode
        super().mouseReleaseEvent(event)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.viewport().setCursor(self.viewport_cursor)

    def wheelEvent(self, event):
        self._rescale_view(1.0/(math.pow(2.0, -event.angleDelta().y() / 240.0)))

    def drawBackground(self, painter, rect):
        scene_rect = self.sceneRect()
        # fill
        gradient = QLinearGradient(scene_rect.topLeft(),
                                   scene_rect.bottomRight())
        c = QColor(settings["background_color"])
        gradient.setColorAt(0, c.lighter(settings["background_color_gradient"]))
        gradient.setColorAt(0.5, c)
        gradient.setColorAt(1, c.darker(settings["background_color_gradient"]))
        painter.fillRect(rect.intersected(scene_rect), QBrush(gradient))

    def _rescale_view(self, scale_factor):
        # cache the scrollbar position
        h_slider = self.horizontalScrollBar().value()
        v_slider = self.verticalScrollBar().value()

        self._rescale(scale_factor)

        # keep the scrollbars at the previous position
        self.horizontalScrollBar().setValue(h_slider)
        self.verticalScrollBar().setValue(v_slider)

    def scale_view_in(self):
        self._rescale_view(1.2)

    def scale_view_out(self):
        self._rescale_view(1 / 1.2)

    def scale_view(self, scale_value):
        self.resetTransform()
        self._rescale_view(scale_value)

    def scale_view_reset(self):
        self.scale_view(DEFAULT_GRAPH_PANE_SCALE)

    # reset viewport view to starting orientation
    @Slot()
    def _reset_viewport(self):
        self.centerOn(0, 0)

