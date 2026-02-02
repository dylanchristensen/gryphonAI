from os.path import split, join
from PySide6.QtCore import QObject, Slot # for signal/slot support
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from preferences import preferences
from settings import settings
import mp_json_io_manager
from mp_file_dialog import get_open_filename, get_save_filename
from mp_logger import log, begin_timestamps, timestamp, show_timestamps
from mp_code_parser import mp_code_schema
from version_file import VERSION
from message_popup import message_popup

class GryManager(QObject):
    """Wraps responsibilities of saving and restoring .gry state.
       Interfaces with graphs_manager, mp_code_manager, and settings_manager.
    """

    def __init__(self, parent_w, graphs_manager, mp_code_manager,
                 graph_list_selection_model, settings_manager,
                 mp_code_change_tracker):
        super().__init__()
        self.parent_w = parent_w
        self.graphs_manager = graphs_manager
        self.mp_code_manager = mp_code_manager
        self.graph_list_selection_model = graph_list_selection_model
        self.settings_manager = settings_manager
        self.mp_code_change_tracker = mp_code_change_tracker

        # action import JSON .gry file
        self.action_import_gry_file = QAction(QIcon(":/icons/import_gry"),
                                             "&Import .gry...", self)
        self.action_import_gry_file.setToolTip("Import Gryphon .gry file")
        self.action_import_gry_file.triggered.connect(
                                     self.select_and_import_gry_file)

        # action export JSON .gry file
        self.action_export_gry_file = QAction(QIcon(":/icons/export_gry"),
                                             "&Export .gry...", self)
        self.action_export_gry_file.setToolTip("Export Gryphon .gry file")
        self.action_export_gry_file.triggered.connect(
                                     self.select_and_export_gry_file)


    # import Gryphon .gry file
    def import_gry_file(self, gry_file_filename):
        # maybe abort request
        status = self.mp_code_change_tracker.maybe_save_discard_or_cancel()
        if status:
            log(status)
            return

        begin_timestamps("Importing Gryphon file %s..."%gry_file_filename)
        status, gry_data = mp_json_io_manager.import_gry_file(gry_file_filename)

        if status:
            # log failure
            log(status)

        else:
            # accept .gry settings
            self.settings_manager.change_settings(gry_data["settings"])

            # accept import request
            timestamp("Imported Gryphon file %s"%gry_file_filename)

            # allow some backward compatibility
            if "mp_code" in gry_data:
                message_popup(self.parent_w, "Note: %s is old and might not"
                              " be fully compatible with Gryphon %s"%(
                              gry_file_filename, VERSION))
                gry_data["mp_code_current"] = gry_data["mp_code"]
                gry_data["mp_code_runtime"] = gry_data["mp_code"]

            # accept graphs
            self.graphs_manager.set_graphs(
                                           gry_data["mp_code_runtime"],
                                           gry_data["graphs"],
                                           gry_data["scope"],
                                          )
            timestamp("Created graphs from gry")
            show_timestamps()
            self.graph_list_selection_model.select_graph_index(
                                         gry_data["selected_graph_index"])
            self.mp_code_manager.set_text("", gry_data["mp_code_current"])

    # export Gryphon Graph file, return "" or error text
    # graphs, mp_code_runtime, and scope are from the latest run.
    # mp_code_current, selected_graph_index, and settings are current values.
    def export_gry_file(self, gry_file_filename):
        begin_timestamps("Exporting Gryphon Graph file %s..."%gry_file_filename)
        gry_graphs = self.graphs_manager.get_gry_graphs()
        mp_code_runtime = self.graphs_manager.mp_code
        mp_code_current = self.mp_code_manager.text()
        scope = self.graphs_manager.scope
        selected_graph_index = self.graph_list_selection_model \
                                   .selected_graph_index()
        gry_data = {"graphs":gry_graphs,
                    "mp_code_current":mp_code_current,
                    "mp_code_runtime":mp_code_runtime,
                    "scope":scope,
                    "selected_graph_index":selected_graph_index,
                    "settings":settings
                   }

        status = mp_json_io_manager.export_gry_file(gry_file_filename, gry_data)
        if status:
            # log failure
            log(status)
        else:
            timestamp("Done exporting Gryphon Graph file %s"%gry_file_filename)
            show_timestamps()
        return status

    # import Gryphon Graph file
    @Slot()
    def select_and_import_gry_file(self):
        filename = get_open_filename(self.parent_w,
                        "Import Gryphon Graph file",
                        preferences["preferred_gry_file_dir"],
                        "Gryphon graph files (*.gry);;All Files (*)",
                                     )

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
        mp_code_text = self.mp_code_manager.text()
        schema_name = mp_code_schema(mp_code_text)
        scope = self.graphs_manager.scope
        suggested_filename = "%s_scope_%d.gry"%(schema_name, scope)

        filename = get_save_filename(self.parent_w,
                     "Export Gryphon Graph file",
                     join(preferences["preferred_gry_file_dir"],
                                               suggested_filename),
                     "Gryphon graph files (*.gry);;All Files (*)",
                                     )

        if filename:
            # remember the preferred path
            head, _tail = split(filename)
            preferences["preferred_gry_file_dir"] = head

            # export the file
            _status = self.export_gry_file(filename)

