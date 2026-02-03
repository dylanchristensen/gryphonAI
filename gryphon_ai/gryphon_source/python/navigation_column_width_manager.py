from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Signal # for signal/slot support

class NavigationColumnWidthManager(QObject):
    """Track navigation column width and signal change

    Data:
      * width - width of the navigation column available in the list splitpane

    Signals:
      * signal_navigation_column_width_changed(int) - width of navigation
        column changed
    """

    # signals
    signal_navigation_column_width_changed = Signal(int,
                                      name='navigationColumnWidthChanged')

    def __init__(self, scrollbar_width):
        super(NavigationColumnWidthManager, self).__init__()
        self.scrollbar_width = scrollbar_width
        self.width = None

    # call this to set width
    def set_width(self, width):
        self.width = width
        self.signal_navigation_column_width_changed.emit(width)

