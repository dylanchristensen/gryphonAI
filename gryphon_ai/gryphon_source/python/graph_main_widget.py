# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtCore import QObject
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter
from PySide6.QtGui import QTransform
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from PySide6.QtWidgets import QMenu
from settings_manager import settings
from edge_grip_manager import EdgeGripManager
from reset_scene_singleton import set_reset_scene_function
from event_menu import EventMenu
from os_compatibility import control_modifier

# GraphicsView
class GraphMainView(QGraphicsView):

    def __init__(self, signal_graphs_loaded):
        super(GraphMainView, self).__init__()

        self.viewport_cursor = Qt.CursorShape.ArrowCursor
        self.setViewportUpdateMode(
                       QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(
                           QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # enable user rectangular selection
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
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
            super(GraphMainView, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        # view mode
        if event.button() == Qt.MouseButton.LeftButton \
                   and event.modifiers() & Qt.KeyboardModifier.ShiftModifier \
                              == Qt.KeyboardModifier.ShiftModifier:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.viewport().setCursor(self.viewport_cursor)

        super(GraphMainView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # view mode
        super(GraphMainView, self).mouseReleaseEvent(event)

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

    # reset viewport view to starting orientation
    @Slot(list, str, int)
    def _reset_viewport(self, _graphs, _schema_name, _scope):
        self.centerOn(0, 0)

class GraphMainScene(QGraphicsScene):

    # signals
    signal_graph_index_view_changed = Signal(int,
                                                name='graphIndexViewChanged')

    # reset bounding rectangle, possibly centering the graph
    def _set_scene_rect(self):
        scene_rect = self.itemsBoundingRect()
        self.setSceneRect(scene_rect)

    # call this to emit indication that the main view geometry changed somehow
    @Slot('QList<QRectF>')
    def changed_main_view(self, _region):
        if self.graph_item:
            self.signal_graph_index_view_changed.emit(
                                  self.selected_graph_index)

    def __init__(self, graphs_manager, settings_manager):
        super(GraphMainScene, self).__init__()
        set_reset_scene_function(self.reset_scene)
        self.graphs_manager = graphs_manager
        self.settings_manager = settings_manager
        self.selected_graph_index = -1
        self._in_set_scene_rect = False

        # the event menu which applies to any selected graph_item
        self.event_menu = EventMenu(self, settings_manager)

        # the scene's edge grip manager
        self.edge_grip_manager = EdgeGripManager(self)

        # connect to set main scene
        graphs_manager.signal_graph_selection_changed.connect(self.set_scene)

        # connect to know when graph_item geometry changes in order to
        # emit need to repaint
        self.changed.connect(self.changed_main_view)

        # connect to realign bounding rect
        settings_manager.signal_settings_changed.connect(self._set_scene_rect)

        self.graph_item = None

    # populate scene with QGraphicsItem items
    @Slot(int)
    def set_scene(self, selected_graph_index):
        self.selected_graph_index = selected_graph_index
        self.clear_scene()

        if selected_graph_index == -1:
            return

        # keep for access
        self.graph_item = self.graphs_manager.graphs[selected_graph_index]

        # optimization: just-in-time for display, see graph_item.py
        self.graph_item.initialize_items()

        # add top level parent graph item to this scene
        self.addItem(self.graph_item.background_box)

        # set initial size
        self._set_scene_rect()

    # reset scene on collapse/expand or main view geometry change
    def reset_scene(self):
        self.set_scene(self.selected_graph_index)

    # clear_scene
    def clear_scene(self):

        # remove any edge selection
        self.edge_grip_manager.unhighlight_edge()

        # remove the top level parent graph item from this scene
        if self.graph_item:
            self.removeItem(self.graph_item.background_box)

        # clear graph_item pointer
        self.graph_item = None

        # set initial size
        self._set_scene_rect()

    def keyPressEvent(self, event):

        # keystroke controls
        key = event.key()

        if key == Qt.Key.Key_A and event.modifiers() \
                             == Qt.KeyboardModifier.ControlModifier:
            self.graph_item.trace.select_all_nodes()
        elif key == Qt.Key.Key_H and event.modifiers() == control_modifier():
            self.graph_item.trace.unhide_all_nodes()
        elif key == Qt.Key.Key_H:
            self.graph_item.trace.toggle_hide_unhide()
        elif key == Qt.Key.Key_C:
            self.graph_item.trace.toggle_collapse_uncollapse()

        else:
            super(GraphMainScene, self).keyPressEvent(event)

    def mousePressEvent(self, event):

        # do this so QGraphicsScene size can shrink back
        self._set_scene_rect()

        super(GraphMainScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, _event):
        # do this so QGraphicsScene size can shrink back

        if self._in_set_scene_rect:
            # Avoid possible recursion that has been observed when
            # overly zoomed in.
            print("GraphMainScene._set_scene_rect comment: skipping "
                  "to avoid recursion")
            super(GraphMainScene, self).mouseMoveEvent(_event)
        else:
            self._in_set_scene_rect = True
            self._set_scene_rect()
            super(GraphMainScene, self).mouseMoveEvent(_event)
            self._in_set_scene_rect = False

    def _show_scene_menu(self):
        menu = QMenu()
        menu.addAction(self.graphs_manager.action_show_hidden_components)
        menu.addAction(
            self.graphs_manager.action_show_hidden_components_all_graphs)
        _action = menu.exec(QCursor.pos())

    def contextMenuEvent(self, event):

        item_under_cursor = self.itemAt(event.scenePos(), QTransform())
        if item_under_cursor:
            # forward event to item
            item_under_cursor.contextMenuEvent(event)
        else:
            self._show_scene_menu()

# GraphMainWidget
class GraphMainWidget(QObject):
    """GraphMainWidget provides the main QGraphicsView.  It manages signals
    and wraps these:
      * GraphMainView
      * GraphMainScene
    """

    def __init__(self, graphs_manager, settings_manager):
        super(GraphMainWidget, self).__init__()

        # GraphMainWidget's scene and view objects
        self.scene = GraphMainScene(graphs_manager, settings_manager)
        self.view = GraphMainView(graphs_manager.signal_graphs_loaded)
        self.view.setScene(self.scene)

        # graph manager
        self.graphs_manager = graphs_manager

