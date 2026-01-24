from os.path import join, split, exists
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox
from mp_logger import log
from message_popup import message_popup
from preferences import preferences
from settings import settings
from mp_file_dialog import get_save_filename, get_existing_directory
from mp_code_parser import mp_code_schema
from export_trace import export_trace

def _image_format():
    return settings["export_image_format"]

class ExportTraceManager(QObject):
    def __init__(self, parent_w, graphs_manager, graph_list_selection_model,
                 application):
        super().__init__()
        self.parent_w = parent_w
        self.graphs_manager = graphs_manager
        self.graph_list_selection_model = graph_list_selection_model
        self.application = application

        # action export trace as image file
        self.action_export_trace = QAction("&Export graph view...")
        self.action_export_trace.setToolTip("Export graph as image file")
        self.action_export_trace.triggered.connect(
                                     self.select_and_export_trace)

        # action export all traces as image files
        self.action_export_all_traces = QAction("&Export all graph views...")
        self.action_export_all_traces.setToolTip(
                                           "Export all graphs as image files")
        self.action_export_all_traces.triggered.connect(
                                     self.select_and_export_all_traces)

    def _log_status(self, status, trace_filename):
        if status:
            # log failure
            log(status)

            # warn of failure
            message_popup(self.parent_w, status)

        else:
            # great, exported.
            log("Exported trace image file %s" % trace_filename)

    # export trace as image file
    @Slot()
    def select_and_export_trace(self):

        graph_index, graph_item \
                   = self.graph_list_selection_model \
                                   .selected_graph_index_and_item()
        if graph_index == -1:
            log("Error exporting graph: No graph selected.")
            return

        # suggested filename
        schema_name = mp_code_schema(self.graphs_manager.mp_code)
        scope = self.graphs_manager.scope
        proposed_filename = join(preferences["preferred_trace_dir"],
                          "%s_%d_%03d%s"%(schema_name, scope,
                                          graph_index, _image_format()))
        filter_text = "MP trace image files (*%s);;All Files (*)" \
                                                        %_image_format()
        filename = get_save_filename(self.parent_w, "Export trace image file",
                                     proposed_filename, filter_text)

        if filename:
            # remember the preferred path
            head, _tail = split(filename)
            preferences["preferred_trace_dir"] = head

            # export the trace as image file
            status = export_trace(filename, graph_item, graph_index, scope,
                                  self.application)
            self._log_status(status, filename)

    def _ask_overwrite_mode(self, filename):
        # overwrite? no, yes, yes_to_all
        mb = QMessageBox(self.parent_w)
        mb.setWindowTitle("Export trace image files")
        mb.setText("File %s already exists."%filename)
        mb.setInformativeText("Do you want to replace it?")
        mb.setStandardButtons(QMessageBox.Yes
                            | QMessageBox.YesToAll
                            | QMessageBox.No
                            | QMessageBox.NoToAll)
        mb.setDefaultButton(QMessageBox.YesToAll)
        response = mb.exec()
        return response

    # export traces as image files under path
    @Slot()
    def select_and_export_all_traces(self):

        if not self.graphs_manager.graphs:
            log("Error exporting graph: There are no graphs to export")
            return

        # use schema name as suggested filename prefix
        schema_name = mp_code_schema(self.graphs_manager.mp_code)

        trace_dir = get_existing_directory(self.parent_w,
          "Select the folder for writing %s graph view files"%schema_name,
          preferences["preferred_trace_dir"])

        if trace_dir:
            preferences["preferred_trace_dir"] = trace_dir

            # export the traces as serialized image files
            scope = self.graphs_manager.scope
            do_overwrite_all = False
            for graph_index, graph in enumerate(self.graphs_manager.graphs):
                if graph_index == 0 and not graph.has_non_trace():
                    # do not render empty global view
                    continue

                # prepare the indexed filename and export its graph
                filename = join(trace_dir, "%s_%d_%03d%s"%(schema_name,
                                       scope, graph_index, _image_format()))

                # maybe do not overwrite
                if not do_overwrite_all and exists(filename):
                    overwrite_mode = self._ask_overwrite_mode(filename)
                    if overwrite_mode == QMessageBox.No:
                        do_write = False
                    elif overwrite_mode == QMessageBox.NoToAll:
                        # no more
                        break
                    elif overwrite_mode == QMessageBox.Yes:
                        do_write = True
                    elif overwrite_mode == QMessageBox.YesToAll:
                        do_write = True
                        do_overwrite_all = True
                    else:
                        raise RuntimeError("bad")
                else:
                    do_write = True
                if not do_write:
                    continue

                # export the graph
                graph_item = self.graphs_manager.graphs[graph_index]
                status = export_trace(filename, graph_item, graph_index, scope,
                                      self.application)
                self._log_status(status, filename)

