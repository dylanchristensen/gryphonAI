from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from edge_grip import EdgeGrip

"""
Interface
  * highlight_edge(edge) - edge's mouse press event calls this.  The
                           edge must have from_node, to_node, ep1, ep2.
  * maybe_unhighlight_edge() - Scene calls this whenever its selection
                                changes.
  * unhighlight_edge() - call this when scene changes or app exits to avoid
                         RuntimeError: wrapped C/C++ object of type EdgeGrip
                         has been deleted
"""

class EdgeGripManager(QObject):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self._edge = None
        self._grip1 = None
        self._grip2 = None
        self._is_active = False
        self._is_busy_unhighlighting = False # prevent reentrance

        # connect
        scene.selectionChanged.connect(self.maybe_unhighlight_edge)

    # unhighlight any active highlighted edge
    def unhighlight_edge(self):
        if self._is_active:
            self._is_busy_unhighlighting = True # prevent reentrance
            self._edge.set_highlighted(False)
            self._grip1.prepareGeometryChange()
            self._grip1.setParentItem(None)
            del self._grip1
            self._grip2.prepareGeometryChange()
            self._grip2.setParentItem(None)
            del self._grip2
            self._is_active = False
            self._is_busy_unhighlighting = False

    # unhighlight unless exactly one grip is selected and nothing else
    @Slot()
    def maybe_unhighlight_edge(self):
        if self._is_busy_unhighlighting:
            # leave unhighlight_edge alone or it will tangle
            return

        if self._is_active \
               and not (self._grip1.isSelected() != self._grip2.isSelected()
                        and len(self.scene.selectedItems()) == 1):
            self.unhighlight_edge()

    def highlight_edge(self, edge):
        self.unhighlight_edge()
        self._edge = edge
        edge.set_highlighted(True)
        self._grip1 = EdgeGrip(edge, "source")
        self._grip1.setParentItem(edge.parentItem())
        self._grip2 = EdgeGrip(edge, "dest")
        self._grip2.setParentItem(edge.parentItem())
        self.scene.clearSelection()
        self._is_active = True

