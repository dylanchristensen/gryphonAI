from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtGui import QCursor
from trace_collapse_helpers import collapse_below, uncollapse_below, \
                                   set_collapsed_edges

class NodeMenu(QObject):

    def __init__(self, node, event):
        super().__init__()

        self.node = node

        # actions
        # align node
        self.action_align_node = QAction("Align")
        self.action_align_node.setToolTip("Align with respect to other nodes")
        self.action_align_node.triggered.connect(self.do_align_node)

        # collapse
        self.action_collapse = QAction("Collapse")
        self.action_collapse.setToolTip("Collapse events under this event")
        self.action_collapse.triggered.connect(self.do_collapse)
        # uncollapse
        self.action_uncollapse = QAction("Expand")
        self.action_uncollapse.setToolTip("Expand events under this event")
        self.action_uncollapse.triggered.connect(self.do_uncollapse)
        # hide
        self.action_hide = QAction("Hide")
        self.action_hide.setToolTip("Hide this event")
        self.action_hide.triggered.connect(self.do_hide)
        # unhide
        self.action_unhide = QAction("Show")
        self.action_unhide.setToolTip("Show this event")
        self.action_unhide.triggered.connect(self.do_unhide)

        self.menu = QMenu()
        self.menu.addAction(self.action_align_node)
        self.menu.addSeparator()
        self.menu.addAction(self.action_collapse)
        self.menu.addAction(self.action_uncollapse)
        self.menu.addAction(self.action_hide)
        self.menu.addAction(self.action_unhide)

        # Root, Composite, Schema, not atomic(A) or say(T)
        can_collapse = node.node_type == "R" or node.node_type == "C" or \
                       node.node_type == "S"
        if can_collapse:
            self.action_collapse.setEnabled(not node.collapse_below)
            self.action_uncollapse.setEnabled(node.collapse_below)
        else:
            self.action_collapse.setEnabled(False)
            self.action_uncollapse.setEnabled(False)
        self.action_hide.setEnabled(not node.hide)
        self.action_unhide.setEnabled(node.hide)

        _action = self.menu.exec(event.screenPos())

    def do_collapse(self):
        collapse_below(self.node)
        set_collapsed_edges(self.node.scene())

    def do_uncollapse(self):
        uncollapse_below(self.node)
        set_collapsed_edges(self.node.scene())

    def do_hide(self):
        self.node.scene().graph_item.trace.hide_node(self.node, True)

    def do_unhide(self):
        self.node.scene().graph_item.trace.hide_node(self.node, False)

    def do_align_node(self):
        self.node.scene().graph_item.trace.align_node(self.node)

