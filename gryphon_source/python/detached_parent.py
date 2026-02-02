from PySide6.QtWidgets import QGraphicsItem

"""A detached QGraphicsItem for holding box and grip items when they
   are not part of QGraphicsScene.
"""

BOX_PADDING = 20

# DetachedParent provides an unparented container for holding box and
# grip items when we don't want them to be part of QGraphicsView.
# We can't just setVisible(False) because QGraphicsView still reserves
# space for it.

class DetachedParent(QGraphicsItem):
    def __init__(self):
        super().__init__()
    def boundingRect(self):
        raise RuntimeError("bad")
    def paint(self, _painter, _option, _widget):
        raise RuntimeError("bad")

