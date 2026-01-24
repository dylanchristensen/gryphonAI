from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QDialog, QAbstractItemView
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

_WINDOW_SIZE = QSize(1150, 700)

_HEADERS = "Action|Windows / Linux Command|Mac Command"
_CODE_EDITOR_TITLE = "Code editor (when focused)"
_CODE_EDITOR = [
"Show hints for events and keywords|Ctrl + Space|Ctrl + Space",
"Undo|Ctrl + Z|Cmd + Z",
"Redo|Ctrl + Y|Cmd + Y",
"Copy|Ctrl + C|Cmd + C",
"Cut |Ctrl + X|Cmd + X",
"Paste|Ctrl + V|Cmd + V",
"Select all|Ctrl + A|Cmd + A",
"Open code editor menu|Right click|Ctrl + click",
"Open Find and Replace|Ctrl + F|Cmd + F",
"Open auto-complete shortcut|Ctr + Space|Ctrl + Space"
]
_GRAPH_PANE_TITLE = "Graph pane (when focused)"
_GRAPH_PANE = [
"Undo|Ctrl + Z|Cmd + Z",
"Redo|Ctrl + Y|Cmd + Y",
"Select an event|Click on event|Click on event",
"Select multiple events|Ctrl or Shift while clicking on event|CMD while clicking on event",
"Select events in rectangular area|Shift + click empty space and drag|Shift + click empty space and drag",
"Select event and all events below|Shift + click on event|Shift + click on event",
"Select all events|Ctrl + A|Cmd + A",
"Toggle event selection|Ctrl while clicking on events|Cmd while clicking on events",
"Unselect all events|Click in empty space|Click in empty space",
"Open an event’s event menu|Left-click event menu icon or right-click event|Left-click event menu icon or Ctrl + click event",
"Move events|Drag event(s)|Drag event(s)",
"Move connections|Click to select then drag grips to move|Click to select then drag grips to move",
"Toggle hide/unhide selected event(s)|H|H",
"Show all hidden event(s)|Ctrl + H|Ctrl + H",
"Toggle collapse/uncollapse selected root and composite events|C|C",
"Pan the view|Arrow keys or click empty space and drag|Arrow keys or click empty space and drag",
"Zoom the view|+ and - keystroke or roll Mouse wheel|+ and - keystroke or roll mouse wheel",
]
_NAVIGATION_PANE_TITLE = "Navigation pane (when focused)"
_NAVIGATION_PANE = [
"Select a trace or select global view, if available|Click item|Click item",
"Select next in list|Arrow keys|Arrow keys",
]

def _configure_table(table, widths):
    table.setSelectionMode(QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.resize(sum(widths), len(table.model().rows)*table.rowHeight(0))
    w = sum(widths) + 25
    h = len(table.model().rows) * table.rowHeight(0) \
        + table.horizontalHeader().height() + 4
    table.setMinimumSize(w, h)
    table.setMaximumSize(w, h)
    table.horizontalHeader().setStretchLastSection(True)
    for i, width in enumerate(widths):
        table.setColumnWidth(i, width)

class ShortcutsTableModel(QAbstractTableModel):
    def __init__(self, headers, rows):
        super().__init__()
        self.headers = headers.split('|')
        self.rows = [row.split('|') for row in rows]

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self.rows)

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self.headers)

    def headerData(self, section, orientation,
                                         role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        else:
            return None # QVariant()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            if column in {0, 1, 2}:
                return self.rows[row][column]
            raise RuntimeError("bad")
        else:
            return None # QVariant()

class KeyboardShortcutsDialog(QDialog):

    def __init__(self, parent_window):
        super().__init__(parent_window)

        self.resize(_WINDOW_SIZE)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("Gryphon keyboard shortcuts")

        self.scroll_area = QScrollArea(self)
        self.scroll_area.resize(_WINDOW_SIZE)
        self.contents = QWidget()
        self.layout = QVBoxLayout(self.contents)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.scroll_area.setWidget(self.contents)

        # code editor table
        self.code_editor_table_view = QTableView()
        self.code_editor_table_model = ShortcutsTableModel(
                                             _HEADERS, _CODE_EDITOR)
        self.code_editor_table_view.setModel(self.code_editor_table_model)
        _configure_table(self.code_editor_table_view, [260, 190, 190])
        self.layout.addWidget(QLabel(_CODE_EDITOR_TITLE))
        self.layout.addWidget(self.code_editor_table_view)
        self.layout.addSpacing(20)

        # graph pane table
        self.graph_pane_table_view = QTableView()
        self.graph_pane_table_model = ShortcutsTableModel(
                                             _HEADERS, _GRAPH_PANE)
        self.graph_pane_table_view.setModel(self.graph_pane_table_model)
        _configure_table(self.graph_pane_table_view, [460, 310, 310])
        self.layout.addWidget(QLabel(_GRAPH_PANE_TITLE))
        self.layout.addWidget(self.graph_pane_table_view)
        self.layout.addSpacing(20)

        # navigation pane table
        self.navigation_pane_table_view = QTableView()
        self.navigation_pane_table_model = ShortcutsTableModel(
                                             _HEADERS, _NAVIGATION_PANE)
        self.navigation_pane_table_view.setModel(
                                          self.navigation_pane_table_model)
        _configure_table(self.navigation_pane_table_view, [360, 190, 190])
        self.layout.addWidget(QLabel(_NAVIGATION_PANE_TITLE))
        self.layout.addWidget(self.navigation_pane_table_view)

