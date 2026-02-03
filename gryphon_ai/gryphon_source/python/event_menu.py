from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QMenu
import resources_rc
from mp_style import mp_menu_button

class EventMenu(QObject):
    """Provides event_menu for traces."""

    def _connected_opacity_action(self, name, value):
        action = QAction(name)
        @Slot()
        def menu_action_function():
            self.settings_manager.change_one_setting(
                                    "trace_hide_collapse_opacity", value)
        action.triggered.connect(menu_action_function)
        return action

    def __init__(self, scene, settings_manager):
        super(EventMenu, self).__init__()

        self.scene = scene
        self.settings_manager = settings_manager

        # unhide all events
        self.action_unhide = QAction("Show Hidden Events")
        self.action_unhide.setStatusTip("Stop hiding all hidden events")
        self.action_unhide.triggered.connect(self.do_unhide)

        # collapse all root events
        self.action_collapse_roots = QAction("Collapse Root Events")
        self.action_collapse_roots.setStatusTip("Collapse all Root events")
        self.action_collapse_roots.triggered.connect(self.do_collapse_roots)

        # uncollapse all root events
        self.action_uncollapse_roots = QAction("Expand Root Events")
        self.action_uncollapse_roots.setStatusTip(
                                         "Expand all collapsed Root events")
        self.action_uncollapse_roots.triggered.connect(self.do_uncollapse_roots)

        # collapse all composite events
        self.action_collapse_composites = QAction("Collapse Composite Events")
        self.action_collapse_composites.setStatusTip(
                                         "Collapse all Composite events")
        self.action_collapse_composites.triggered.connect(
                                              self.do_collapse_composites)

        # uncollapse all composite events
        self.action_uncollapse_composites = QAction(
                                              "Expand Composite Events")
        self.action_uncollapse_composites.setStatusTip(
                                      "Expand all collapsed Composite events")
        self.action_uncollapse_composites.triggered.connect(
                                              self.do_uncollapse_composites)

        # opacity actions
        self.action_opacity_0 = self._connected_opacity_action(
                                        "0% (completely transparent)", 0)
        self.action_opacity_25 = self._connected_opacity_action("25%", 63)
        self.action_opacity_50 = self._connected_opacity_action("50%", 127)
        self.action_opacity_75 = self._connected_opacity_action("75%", 191)

        # The event_menu suitable for adding under a parent menu
        self.event_menu = QMenu("Events")
        self.event_menu.setIcon(QIcon(":/icons/event_menu"))
        self.event_menu.aboutToShow.connect(self._set_menu_visibility)

        # populate event_menu
        self.event_menu.addAction(self.action_unhide)
        self.event_menu.addSeparator()
        self.event_menu.addAction(self.action_collapse_roots)
        self.event_menu.addAction(self.action_uncollapse_roots)
        self.event_menu.addSeparator()
        self.event_menu.addAction(self.action_collapse_composites)
        self.event_menu.addAction(self.action_uncollapse_composites)
        self.event_menu.addSeparator()
        self.trace_opacity_menu = QMenu("Hidden/collapsed &opacity")
        self.trace_opacity_menu.addAction(self.action_opacity_0)
        self.trace_opacity_menu.addAction(self.action_opacity_25)
        self.trace_opacity_menu.addAction(self.action_opacity_50)
        self.trace_opacity_menu.addAction(self.action_opacity_75)
        self.event_menu.addMenu(self.trace_opacity_menu)

        # the event menu button for embedding into toolbar
        self.event_menu_button = mp_menu_button(self.event_menu,
                             QIcon(":/icons/event_menu"),
                                   "Events ",
                                   "Manage event visibility")

    def _set_menu_visibility(self):
        if self.scene.selected_graph_index == -1 \
                      or not self.scene.graph_item.has_trace():

            # no graph
            self.action_unhide.setEnabled(False)
            self.action_collapse_roots.setEnabled(False)
            self.action_uncollapse_roots.setEnabled(False)
            self.action_collapse_composites.setEnabled(False)
            self.action_uncollapse_composites.setEnabled(False)
            return

        # enable what can be done
        self.selected_trace = self.scene.graph_item.trace
        can_unhide = False
        can_collapse_roots = False
        can_uncollapse_roots = False
        can_collapse_composites = False
        can_uncollapse_composites = False
        for node in self.selected_trace.nodes:
            if node.hide:
                can_unhide = True
            if node.node_type == "R" and node.collapse_below == False:
                can_collapse_roots = True
            if node.node_type == "R" and node.collapse_below:
                can_uncollapse_roots = True
            if node.node_type == "C" and node.collapse_below == False:
                can_collapse_composites = True
            if node.node_type == "C" and node.collapse_below:
                can_uncollapse_composites = True

        # enable visibility based on what can be done
        self.action_unhide.setEnabled(can_unhide)
        self.action_collapse_roots.setEnabled(can_collapse_roots)
        self.action_uncollapse_roots.setEnabled(can_uncollapse_roots)
        self.action_collapse_composites.setEnabled(can_collapse_composites)
        self.action_uncollapse_composites.setEnabled(can_uncollapse_composites)

    @Slot()
    def do_unhide(self):
        self.selected_trace.unhide_all_nodes()

    @Slot()
    def do_collapse_roots(self):
        self.selected_trace.set_collapse_node_type("R")

    @Slot()
    def do_uncollapse_roots(self):
        self.selected_trace.set_uncollapse_node_type("R")

    @Slot()
    def do_collapse_composites(self):
        self.selected_trace.set_collapse_node_type("C")

    @Slot()
    def do_uncollapse_composites(self):
        self.selected_trace.set_uncollapse_node_type("C")

