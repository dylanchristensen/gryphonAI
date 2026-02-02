from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import QItemSelection
from PySide6.QtWidgets import QDialog, QAbstractItemView
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QHBoxLayout
from graph_list_table_model import GRAPH_COLUMN

_WINDOW_SIZE = QSize(800, 500)

class GraphListTableDialog(QDialog):

    def __init__(self, parent_window, graph_list_proxy_model,
                 graph_list_selection_model):
        super().__init__(parent_window)

        self.resize(_WINDOW_SIZE)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("Sort Traces by Attribute")

        # layout
        self.layout = QVBoxLayout(self)

        # table
        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.setModel(graph_list_proxy_model)
        self.table.setSelectionModel(graph_list_selection_model)
        self.table.setSelectionBehavior(
                         QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
                         QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table.hideColumn(GRAPH_COLUMN)
        self.layout.addWidget(self.table)

        # close button
        spacing = 10
        self.layout.addSpacing(spacing)
        self.close_pb = QPushButton("Close")
        self.close_pb.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                QSizePolicy.Fixed))
        self.close_pb.clicked.connect(self._close_pb_clicked)
        self.close_layout = QHBoxLayout()
        self.layout.addLayout(self.close_layout)
        self.close_layout.addWidget(self.close_pb)

        # slot
        graph_list_selection_model.selectionChanged.connect(self._select_row)

    @Slot(QItemSelection, QItemSelection)
    def _select_row(self, selected, deselected):
        # get a lsit of the same row index for each column else an empty list
        rows = [index.row() for index in selected.indexes()]
        if rows:
            self.table.selectRow(rows[0])

    # close button
    @Slot()
    def _close_pb_clicked(self):
        self.hide()

    def closeEvent(self, event):
        self.hide()

