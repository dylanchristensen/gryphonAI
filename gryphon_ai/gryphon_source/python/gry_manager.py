from os.path import split, join
from PySide6.QtCore import QObject, Slot # for signal/slot support
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog
from graph_item import GraphItem
from preferences_manager import preferences
from settings_manager import settings
import mp_json_io_manager
from mp_logger import log, clear_log

class GryManager(QObject):
    """Wraps responsibilities of saving and restoring .gry state.
       Uses signals from graphs_manager and mp_code_manager to make
       state current.
    """

    def __init__(self, parent_w, graphs_manager, mp_code_manager,
                                                    settings_manager):
        super().__init__()
        self.parent_w = parent_w
        self.graphs_manager = graphs_manager
        self.mp_code_manager = mp_code_manager
        self.settings_manager = settings_manager

        # action import JSON .gry file
        self.action_import_gry_file = QAction(QIcon(":/icons/import_gry"),
                                             "&Import .gry...", self)
        self.action_import_gry_file.setStatusTip("Import Gryphon Graph file")
        self.action_import_gry_file.triggered.connect(
                                     self.select_and_import_gry_file)

        # action export JSON .gry file
        self.action_export_gry_file = QAction(QIcon(":/icons/export_gry"),
                                             "&Export .gry...", self)
        self.action_export_gry_file.setStatusTip("Export Gryphon Graph file")
        self.action_export_gry_file.triggered.connect(
                                     self.select_and_export_gry_file)


    # import Gryphon graph file
    def import_gry_file(self, gry_file_filename):
        log("Importing Gryphon Graph file %s..."%gry_file_filename)
        status, gry_data = mp_json_io_manager.import_gry_file(gry_file_filename)

        if status:
            # log failure
            log(status)

        else:
            # accept import request
            clear_log()

            # accept graphs
            self.graphs_manager.set_graphs(gry_data["graphs"],
                                           gry_data["schema_name"],
                                           gry_data["scope"],
                                           gry_data["selected_graph_index"])
            self.mp_code_manager.set_text(gry_data["mp_code"])
            self.settings_manager.change_settings(gry_data["settings"])

    # export Gryphon Graph file, return "" or error text
    def export_gry_file(self, gry_file_filename):
        gry_graphs = self.graphs_manager.get_gry_graphs()
        mp_code = self.mp_code_manager.text()
        schema_name = self.mp_code_manager.schema_name()
        scope = self.graphs_manager.scope
        selected_graph_index = self.graphs_manager.selected_graph_index
        gry_data = {"graphs":gry_graphs,
                    "mp_code":mp_code,
                    "schema_name":schema_name,
                    "scope":scope,
                    "selected_graph_index":selected_graph_index,
                    "settings":settings
                   }

        status = mp_json_io_manager.export_gry_file(gry_file_filename, gry_data)
        return status

    # import Gryphon Graph file
    @Slot()
    def select_and_import_gry_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.parent_w,
                        "Import Gryphon Graph file",
                        preferences["preferred_gry_file_dir"],
                        "Gryphon graph files (*.gry);;All Files (*)",
                        options = QFileDialog.Option.DontUseNativeDialog)

        if filename:
            # remember the preferred path
            head, _tail = split(filename)
            preferences["preferred_gry_file_dir"] = head

            # import the file
            self.import_gry_file(filename)

    # export Gryphon Graph file
    @Slot()
    def select_and_export_gry_file(self):

        # suggested filename
        schema_name = self.graphs_manager.schema_name
        scope = self.graphs_manager.scope
        suggested_filename = "%s_scope_%d.gry"%(schema_name, scope)

        filename, _ = QFileDialog.getSaveFileName(self.parent_w,
                     "Export Gryphon Graph file",
                     join(preferences["preferred_gry_file_dir"],
                     suggested_filename),
                     "Gryphon graph files (*.gry);;All Files (*)",
                     options = QFileDialog.Option.DontUseNativeDialog)

        if filename:
            # remember the preferred path
            head, _tail = split(filename)
            preferences["preferred_gry_file_dir"] = head

            # export the file
            status = self.export_gry_file(filename)

            if status:
                # log failure
                log(status)

            else:
                # great, exported.
                log("Exported Gryphon Graph file %s" % filename)


