from PySide6.QtCore import Qt # for Vertical
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QSplitter

class MPCodeColumn(QWidget):
    """Container for MP Code editor and log pane.
       Provides split-screen accessors.
    """

    def __init__(self, gui_manager):
        super(MPCodeColumn, self).__init__()

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        vlayout.addWidget(self.splitter)

        # code windows
        self.splitter.addWidget(gui_manager.mp_code_view_1)
        self.splitter.addWidget(gui_manager.mp_code_view_2)

        # logger view
        self.splitter.addWidget(gui_manager.log_pane)

        # now set layout
        self.setLayout(vlayout)

    def set_splitter_sizes(self, sizes):
        self.splitter.setSizes(sizes)

    def splitter_sizes(self):
        return self.splitter.sizes()

    def set_use_code_editor_split_screen(self, use):
        sizes = self.splitter.sizes()
        if use:
            total = sizes[0] + sizes[1]
            a = (sizes[0] + sizes[1]) // 2
            b = total - a
            self.splitter.setSizes((a, b, sizes[2]))
        else:
            a = sizes[0] + sizes[1]
            b = 0
        self.splitter.setSizes((a, b, sizes[2]))

    def is_using_code_editor_split_screen(self):
        return bool(self.splitter.sizes()[1])

