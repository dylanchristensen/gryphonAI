from os.path import join, split
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QSize, QRect
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtGui import QPainter
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QStyleOption
from PySide6.QtWidgets import QFileDialog
from paint_graph_item import paint_graph_item
from font_helper import cell_height
from mp_logger import log
from preferences_manager import preferences

BOX_PADDING = 20

# export trace as image file.  Return (status)
def _export_trace(trace_filename, graph_item, graph_index, scope):
    """export_trace_manager manages export of trace image files."""
    # painting is much like GraphListItemDelegate.paint().

    if graph_item == None:
        return "Error: graph not available"

    # create the painter with its target pixel map to paint in
    w = graph_item.bounding_rect().width() + 2 * BOX_PADDING
    if graph_index == 0 and w < 200: # force empty global view wider
        w = 200
    h = graph_item.bounding_rect().height() + 2 * BOX_PADDING + cell_height()
    svg_generator = QSvgGenerator()
    svg_generator.setFileName(trace_filename)
    svg_generator.setSize(QSize(int(w), int(h)))
    svg_generator.setViewBox(QRect(0, 0, int(w), int(h)))

    painter = QPainter()
    painter.begin(svg_generator)

    # blank option object for painter
    option = QStyleOption()

    # paint the trace given the default option
    paint_graph_item(painter, graph_item, graph_index, scope, option)
    no_longer_active = painter.end()
    if no_longer_active:
        return ""
    else:
        return "Error: Export failed"

def _suffixed_filename(prefix, scope, graph_index):
    return "%s_%d_%03d.svg" % (prefix, scope, graph_index)

def _log_status(status, trace_filename):
    if status:
        # log failure
        log(status)

    else:
        # great, exported.
        log("Exported trace image file %s" % trace_filename)

class ExportTraceManager(QObject):
    def __init__(self, parent_w, graphs_manager):
        super().__init__()
        self.parent_w = parent_w
        self.graphs_manager = graphs_manager

        # action export trace as image file
        self.action_export_trace = QAction("&Export Graph...")
        self.action_export_trace.setStatusTip("Export graph as image file")
        self.action_export_trace.triggered.connect(
                                     self.select_and_export_trace)

        # action export all traces as image files
        self.action_export_all_traces = QAction("&Export All Graphs...")
        self.action_export_all_traces.setStatusTip(
                                           "Export all traces as image files")
        self.action_export_all_traces.triggered.connect(
                                     self.select_and_export_all_traces)

    # export trace as image file
    @Slot()
    def select_and_export_trace(self):

        graph_index = self.graphs_manager.selected_graph_index
        if graph_index == -1:
            log("Error exporting graph: No graph selected.")
            return

        # suggested filename
        schema_name = self.graphs_manager.schema_name
        scope = self.graphs_manager.scope
        filename, _ = QFileDialog.getSaveFileName(self.parent_w,
                      "Export trace image file",
                      join(preferences["preferred_trace_dir"],
                           _suffixed_filename(schema_name, scope,
                                              graph_index)),
                      "MP trace image files (*.svg);;All Files (*)",
                      options = QFileDialog.Option.DontUseNativeDialog)

        if filename:
            # remember the preferred path
            head, _tail = split(filename)
            preferences["preferred_trace_dir"] = head

            # export the trace as image file
            graph_item = self.graphs_manager.graphs[graph_index]
            status = _export_trace(filename, graph_item, graph_index, scope)
            _log_status(status, filename)

    # export traces as image files under path
    @Slot()
    def select_and_export_all_traces(self):

        if not self.graphs_manager.graphs:
            log("Error exporting graph: There are no graphs")
            return

        # use schema name as suggested filename prefix
        schema_name = self.graphs_manager.schema_name

        filename_prefix, _ = QFileDialog.getSaveFileName(self.parent_w,
          "Export serialized <File name suffix>_trace_nnn.svg "
          "trace image files",
          join(preferences["preferred_trace_dir"], schema_name),
          "MP trace image files (*.svg);;All Files (*)",
          options = QFileDialog.Option.DontUseNativeDialog)

        if filename_prefix:
            # remember the preferred path
            head, _tail = split(filename_prefix)
            preferences["preferred_trace_dir"] = head

            # export the traces as serialized image files
            scope = self.graphs_manager.scope
            for graph_index, graph in enumerate(self.graphs_manager.graphs):
                filename = _suffixed_filename(filename_prefix, scope,
                                              graph_index)
                graph_item = self.graphs_manager.graphs[graph_index]
                status = _export_trace(filename, graph_item, graph_index, scope)
                _log_status(status, filename)

