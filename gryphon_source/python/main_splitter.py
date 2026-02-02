from PySide6.QtCore import Signal # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QSplitter

class MainSplitter(QSplitter):
    """The main splitter containing the navigation column, main graph,
       and code_column.

    Signals:
      * signal_navigation_column_width_changed(int) - width of
        navigation column changed
    """

    # signals
    signal_navigation_column_width_changed = Signal(int,
                                     name='navigationColumnWidthChanged')

    def __init__(self, navigation_column_width_manager):
        super(MainSplitter, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.navigation_column_width_manager = navigation_column_width_manager
        self.splitterMoved.connect(self.splitter_bar_moved)

    # QSplitter resize
    def resizeEvent(self, e):
        super(MainSplitter, self).resizeEvent(e)
        self.navigation_column_width_manager.set_width(self.sizes()[2])

    # QSplitter splitter bar moved
    @Slot(int, int)
    def splitter_bar_moved(self, _pos, _index):
        self.navigation_column_width_manager.set_width(self.sizes()[2])

