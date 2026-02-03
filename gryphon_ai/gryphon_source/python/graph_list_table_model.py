from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex

# configuration values for this table model
GRAPH_COLUMN = 0 # the graph item
TRACE_INDEX_COLUMN = 1 # values start at 1
MARK_COLUMN = 2 # "M" or ""
PROBABILITY_COLUMN = 3 # float 0.0 to 1.0
SIZE_COLUMN = 4 # int, see implementation
COLUMN_COUNT = 5 # number of columns

# GraphListTableModel
class GraphListTableModel(QAbstractTableModel):
    """Provides a graph list table data model for displaying the graph views.
    We use a table model instead of a list so we can define various columns
    for sorting or filtering.

    The first row displayed in the graph list is the global view.  The
    remaining rows show the trace views.  This model provides both views
    as though they are homogeneous types.  Sort and filter operations
    keep the global view, if present, visible and on the top.
    """

    def __init__(self, signal_graphs_loaded):
        super(GraphListTableModel, self).__init__()

        # the starting graph
        self.graphs = list()

        # connect
        signal_graphs_loaded.connect(self.set_graph_list_table)

    @Slot(list, str, int)
    def set_graph_list_table(self, graphs, _schema_name, _scope):
        self.beginResetModel()
        self.graphs = graphs
        self.endResetModel()

    def headerData(self, _section, _orientation,
                                   role=Qt.ItemDataRole.DisplayRole):
        # we do not use headers
        return None # QVariant()

    # number of rows
    def rowCount(self, parent=QModelIndex()):
        return len(self.graphs)

    def columnCount(self, parent=QModelIndex()):
        return COLUMN_COUNT

    # not used for views
    def data(self, model_index, role=Qt.ItemDataRole.DisplayRole):

        # data model is compatible with uninitialized graph items
        if role == Qt.ItemDataRole.DisplayRole:
            row = model_index.row()
            column = model_index.column()
            if column == GRAPH_COLUMN:
                # graph_list_table_view_delegate renders this
                return None # QVariant()
            if column == TRACE_INDEX_COLUMN:
                return row
            if column == MARK_COLUMN:
                if "trace" in self.graphs[row].gry_graph:
                    return self.graphs[row].gry_graph["trace"]["mark"]
                else:
                    return "U"
            if column == PROBABILITY_COLUMN:
                if "trace" in self.graphs[row].gry_graph:
                    return self.graphs[row].gry_graph["trace"]["probability"]
                else:
                    return 0
            if column == SIZE_COLUMN:
                if "trace" in self.graphs[row].gry_graph:
                    gry_trace = self.graphs[row].gry_graph["trace"]
                    return len(gry_trace["nodes"]) + len(gry_trace["edges"])
                else:
                    return 0
            raise RuntimeError("bad %d"%column)
        else:
            return None # QVariant()

    # reset list
    @Slot()
    def reset_list(self):
        self.beginResetModel()
        self.endResetModel()

