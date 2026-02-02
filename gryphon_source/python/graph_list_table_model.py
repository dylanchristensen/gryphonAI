from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from mp_code_parser import mp_code_say_headers, say_info
from message_popup import message_popup

# graph list model column constants
GRAPH_COLUMN = 0 # the graph item
TRACE_INDEX_COLUMN = 1 # values start at 1
MARK_COLUMN = 2 # "M" or ""
PROBABILITY_COLUMN = 3 # float 0.0 to 1.0
SIZE_COLUMN = 4 # int, see implementation

_HARDCODED_HEADERS = ["Graph", "index", "Mark", "Type 1 P", "Size"]

class GraphListTableModel(QAbstractTableModel):
    """Provides the graph list model for graph list accessors, consisting of
    column constants and implementations of headerData, rowCount, columnCount,
    and data.

    graphs_manager maintains the original of graphs and calls set_graph_list
    here to set the list change in motion.  graphs_manager also issues
    signal_graphs_loaded after calling set_graph_list.

    We use a table model instead of a list so we can define various columns
    for sorting or filtering.  The first row in the graph list is the global
    view.  The remaining rows hold the trace views.  Sort and filter
    operations are required to keep the global view, if present, visible and
    on the top.

    Socket:
      * dataChanged - call this to reflect change into views
    """

    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.headers = list()
        super().__init__()

        self.graphs = list()
        self.headers = list()

    def set_graph_list(self, graphs, mp_code):

        # calculate headers from SAY statements
        say_headers, warnings = mp_code_say_headers(mp_code)

        # change the model's data and header titles
        self.beginResetModel()
        self.graphs = graphs
        self.headers = _HARDCODED_HEADERS.copy()
        self.headers.extend(say_headers)
        self.endResetModel()

        # maybe show warnings
        if warnings:
            message = "SAY statements containing both variables and text " \
                      "with embedded numbers " \
                      "cannot be used when sorting traces by attribute.  " \
                      "Columns will not be provided for SAY events " \
                      "generated from the following SAY text:\n\n%s" \
                      %("\n\n".join(warnings))
            message_popup(self.parent_window, message)

    def headerData(self, section, orientation,
                                   role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        else:
            return None # QVariant()

    # number of rows
    def rowCount(self, parent=QModelIndex()):
        return len(self.graphs)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, model_index, role=Qt.ItemDataRole.DisplayRole):

        # data model is compatible with uninitialized graph items
        if role == Qt.ItemDataRole.DisplayRole:
            row = model_index.row()
            column = model_index.column()
            gry_graph = self.graphs[row].gry_graph

            # provide values for hardcoded columns
            if column == GRAPH_COLUMN:
                # graph_list_view_delegate renders this
                return None # QVariant()
            if column == TRACE_INDEX_COLUMN:
                return row
            if row == 0:
                # these columns are for traces only
                return "NA"
            if column == MARK_COLUMN:
                return gry_graph["trace"]["mark"]
            if column == PROBABILITY_COLUMN:
                return gry_graph["trace"]["probability"]
            if column == SIZE_COLUMN:
                gry_trace = gry_graph["trace"]
                return len(gry_trace["nodes"]) + len(gry_trace["edges"])
            if column >= len(self.headers):
                # column number out of range
                raise RuntimeError("bad %d"%column)

            # get the column value based on SAY text in the gry_graph
            return say_info(gry_graph, self.headers[column])

            # provide values for columns dynamically created from SAY nodes
            header = self.headers[column]
            says = say_info(gry_graph)
            if header in says:
                # good, says matches a header so return its numeric value
                return says[header]
            else:
                # return warning when say node text does not match a header
                return "Unexpected: %s"%"; ".join(says.keys())

        else:
            # ignore this ItemDataRole
            return None # QVariant()

