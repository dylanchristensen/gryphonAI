import os
from glob import glob
import signal
import json
import webbrowser
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QStyle # for PM_ScrollBarExtent
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from version_file import VERSION
from main_splitter import MainSplitter
from mp_code_column import MPCodeColumn
from navigation_column import NavigationColumn
from graph_list_selection_spinner import GraphListSelectionSpinner
from graph_main_widget import GraphMainWidget
from graph_list_table import GraphListTable
from navigation_column_width_manager import NavigationColumnWidthManager
from scope_spinner import ScopeSpinner
from graph_metadata_label import GraphMetadataLabel
from graphs_manager import GraphsManager
from mp_code_manager import MPCodeManager
from mp_code_view import MPCodeView
from code_editor_menu import make_code_editor_menu
from gry_manager import GryManager
from settings_appearance_menu import SettingsAppearanceMenu
from graph_pane_menu import make_graph_pane_menu
from export_trace_manager import ExportTraceManager
from mp_logger import set_logger_targets, log, clear_log
from mp_style import mp_menu_button
import resources_rc
import mp_json_io_manager
from trace_generator_manager import TraceGeneratorManager, \
                                    TraceGeneratorCallback
from preferences_manager import PreferencesManager, preferences
from settings_manager import SettingsManager, set_default_settings, settings
from session_persistence import SessionPersistence
from session_snapshots import SessionSnapshots
from keyboard_dialog_wrapper import KeyboardDialogWrapper
from about_mp_dialog_wrapper import AboutMPDialogWrapper
from search_mp_files_dialog_wrapper import SearchMPFilesDialogWrapper
from tg_to_gry import tg_to_gry_graphs
from paths_trace_generator import trace_generator_paths, \
                                  change_trace_generator_paths, \
                                  schedule_validate_trace_generator_paths
from paths_examples import examples_paths, \
                           change_examples_paths, \
                           schedule_validate_examples_paths
from paths_gryphon import TRACE_GENERATED_OUTFILE_TG, \
                          TRACE_GENERATED_OUTFILE_GRY
from examples_menu import fill_examples_menu
from message_popup import message_popup
from startup_options import set_startup_options
from raw_schema_name import raw_schema_name
from gryphon_ai.gryphon_ai_manager import GryphonAIManager

class GUIManager(QObject):

    """MP main window containing menu, toolbar, statusbar, and central widget.
    Central widget contains split pane areas, ref. http://firebird.nps.edu/:
      code_area
      console_area
      graph_area
      navigation_column
    """

    def __init__(self, application):
        super(GUIManager, self).__init__()
        self.application = application

        # the main window
        self.w = QMainWindow()

        # graph settings manager
        self.settings_manager = SettingsManager(self.w)

        # user preferences manager
        self.preferences_manager = PreferencesManager(self)

        # default settings includes referencing dark mode preference
        set_default_settings()

        # session persistence
        self.session_persistence = SessionPersistence(self)

        # session snapshots
        self.session_snapshots = SessionSnapshots(self)

        # the graphs manager
        self.graphs_manager = GraphsManager(self.settings_manager)

        # the graph list width manager
        self.navigation_column_width_manager = NavigationColumnWidthManager(
                  self.w.style().pixelMetric(
                                   QStyle.PixelMetric.PM_ScrollBarExtent))

        # main window decoration
        self.preferences_manager.set_w_geometry()
        self.w.setWindowTitle("Monterey Phoenix v4 - Gryphon GUI %s"%VERSION)
        self.w.setWindowIcon(QIcon(":/icons/mp_logo"))

        # the main splitter which emits size_changed
        self.main_splitter = MainSplitter(self.navigation_column_width_manager)

        # the graph list table which responds to events
        self.graph_list_table = GraphListTable(
                                self.main_splitter,
                                self.graphs_manager,
                                self.navigation_column_width_manager,
                                self.settings_manager.signal_settings_changed,
                                self.preferences_manager)

        # the graph main widget
        self.graph_main_widget = GraphMainWidget(self.graphs_manager,
                                                 self.settings_manager)
        self.graph_main_widget.view.scale_view(preferences["graph_pane_scale"])

        # graph list table signal
        self.graph_main_widget.scene.signal_graph_index_view_changed.connect(
                           self.graph_list_table.graph_index_view_changed)

        # the schema name and scope metadata label
        self.graph_metadata_label = GraphMetadataLabel(self.graphs_manager)

        # the statusbar
        self.statusbar = self.w.statusBar()
        self.statusbar.addPermanentWidget(self.graph_metadata_label.status_text)
        self.statusbar.showMessage("Open, Import, or Compose MP Code to begin.")

        # the log pane and the logger
        self.log_pane = QPlainTextEdit()
        self.log_pane.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_pane.setReadOnly(True)
        set_logger_targets(self.statusbar, self.log_pane)

        # the trace generator manager which runs the compiler asynchronously
        self.trace_generator_callback = TraceGeneratorCallback()
        self.trace_generator_manager = TraceGeneratorManager(
                                self.trace_generator_callback.send_signal)
        self.trace_generator_callback.signal_compile_response.connect(
                                        self.response_compile_mp_code)

        # AI Manager
        try:
            self.gryphon_ai_manager = GryphonAIManager(self)
        except Exception as e:
            import traceback
            print(f"Warning: Failed to initialize Gryphon AI: {e}")
            traceback.print_exc()
            self.gryphon_ai_manager = None

        # the MP Code manager
        self.mp_code_manager = MPCodeManager(
                           self.settings_manager.signal_settings_changed,
                           self.statusbar)

        # persistent dialog
        self.search_mp_files_dialog_wrapper = SearchMPFilesDialogWrapper(
                     self.w, self.preferences_manager, self.settings_manager)

        # the two MP Code editor view windows
        self.mp_code_view_1 = MPCodeView(self.mp_code_manager,
                   self.preferences_manager,
                   self.search_mp_files_dialog_wrapper.action_search_mp_files,
                   1)
        self.mp_code_view_2 = MPCodeView(self.mp_code_manager,
                   self.preferences_manager,
                   self.search_mp_files_dialog_wrapper.action_search_mp_files,
                   2)

        # .gry manager
        self.gry_manager = GryManager(self.w, self.graphs_manager,
                                      self.mp_code_manager,
                                      self.settings_manager)

        # the scope spinner containing spinner=QSpinBox
        self.scope_spinner = ScopeSpinner(
                                  self.mp_code_manager.signal_mp_code_loaded)

        # export trace manager
        self.export_trace_manager = ExportTraceManager(self.w,
                                                       self.graphs_manager)

        # setup
        self.define_actions()
        self.define_menus()
        self.define_toolbar()

        # graph list selection spinner
        self.graph_list_selection_spinner = GraphListSelectionSpinner(
                              self.graphs_manager, self.graph_list_table)

        # the central widget containing the main split pane
        self.mp_code_column = MPCodeColumn(self)
        self.mp_code_column.set_splitter_sizes(
                  preferences["code_column_splitter_sizes"])
        self.navigation_column = NavigationColumn(self)
        self.main_splitter.addWidget(self.mp_code_column)
        self.main_splitter.addWidget(self.graph_main_widget.view)
        self.main_splitter.addWidget(self.navigation_column)
        self.main_splitter.setSizes(preferences["main_splitter_sizes"])
        self.w.setCentralWidget(self.main_splitter)

        # current compile state for buttons
        self.set_is_compiling(False)

        # do these before shutdown
        application.aboutToQuit.connect(
                      self.graph_main_widget.scene.edge_grip_manager\
                      .unhighlight_edge) # avoid RuntimeError:
                      # wrapped C/C++ object of type EdgeGrip has been deleted

        application.aboutToQuit.connect(
                      self.trace_generator_manager.mp_clean_shutdown)
        application.aboutToQuit.connect(
                      self.preferences_manager.save)
        application.aboutToQuit.connect(
                      self.session_persistence.save_this_session)

        # enqueue actions to start on Qt event loop
        schedule_validate_trace_generator_paths(self.w)
        schedule_validate_examples_paths(self.w)
        set_startup_options(self)

        self.w.show()

        # accept Ctrl C
        signal.signal(signal.SIGINT, self.make_ctrl_c_closure_function())

    # enable graceful exit by Ctrl C
    def make_ctrl_c_closure_function(self):
        # signal handler for signal.signal
        def ctrl_c_closure_function(_signal, _frame):
            print("Ctrl C exit")
            self.w.close()
        return ctrl_c_closure_function

    # actions
    def define_actions(self):
        # action exit
        self.action_exit = QAction(QIcon(":/icons/exit"), "&Exit", self.w)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.setStatusTip("Exit MP")
        self.action_exit.triggered.connect(self.w.close)

        # action help
        self.action_help = QAction(QIcon(":/icons/help"),
                                  "&Users manual", self.w)
        self.action_help.setStatusTip("Help using MP Gryphon")
        self.action_help.triggered.connect(self.help_mp_py_um)

        # action keyboard_shortcuts
        self.action_keyboard_shortcuts = QAction("&Keyboard Shortcuts", self.w)
        self.action_keyboard_shortcuts.setStatusTip(
                                        "Keyboard shorcuts for MP controls")
        self.action_keyboard_shortcuts.triggered.connect(
                                        self.keyboard_shortcuts)

        # action about
        self.action_about = QAction(QIcon(":/icons/about_mp"),
                                   "&About MP", self)
        self.action_about.setStatusTip("about MP")
        self.action_about.triggered.connect(self.about_mp)

        # action report an issue
        self.action_report_an_issue = QAction("Report an issue...", self)
        self.action_report_an_issue.setStatusTip("Report an issue about MP")
        self.action_report_an_issue.triggered.connect(self.report_an_issue)

        # action run/cancel
        self.action_run_cancel = QAction(self)
        self.action_run_cancel.setStatusTip("Generate traces from MP Code")
        self.action_run_cancel.triggered.connect(
                                        self._run_cancel_compile_mp_code)

        # action clear log
        self.action_clear_log = QAction(QIcon(":/icons/clear_log"),
                                       "&Clear MP Code Log", self)
        self.action_clear_log.setStatusTip("Clear MP Code log")
        self.action_clear_log.triggered.connect(clear_log)

        # action open MP Code file
        self.action_open_mp_code_file = QAction(QIcon(":/icons/open"),
                                                "&Open .mp...", self)
        self.action_open_mp_code_file.setStatusTip("Open MP Code File")
        self.action_open_mp_code_file.triggered.connect(
                                           self.select_and_open_mp_code_file)

        # action close MP Code file
        self.action_close_mp_code_file = QAction(QIcon(":/icons/close"),
                                                 "Close", self)
        self.action_close_mp_code_file.setStatusTip("Close MP Code File")
        self.action_close_mp_code_file.triggered.connect(self.close_mp_code)

        # action save MP Code file
        self.action_save_mp_code_file = QAction(QIcon(":/icons/save"),
                                                "&Save .mp...", self)
        self.action_save_mp_code_file.setShortcut('Ctrl+S')
        self.action_save_mp_code_file.setStatusTip("Save MP Code file")
        self.action_save_mp_code_file.triggered.connect(
                                           self.save_mp_code_file)

        # action settings trace generator path...
        self.action_trace_generator_path = QAction(
                                     "Trace Generator Path...", self)
        self.action_trace_generator_path.setStatusTip(
                                     "Set the path to the trace-generator")
        self.action_trace_generator_path.triggered.connect(
                                     self.select_trace_generator_path)

        # action settings preloaded examples path...
        self.action_examples_path = QAction(
                                     "Preloaded Examples Path...", self)
        self.action_examples_path.setStatusTip(
                                     "Set the path to preloaded examples")
        self.action_examples_path.triggered.connect(
                                     self.select_examples_path)

        # action zoom the graph pane in
        self.action_zoom_in = QAction(QIcon(":/icons/zoom_in"),
                                      "Zoom in", self)
        self.action_zoom_in.setStatusTip("Zoom the graph pane in")
        self.action_zoom_in.triggered.connect(
                                self.graph_main_widget.view.scale_view_in)

        # action zoom the graph pane out
        self.action_zoom_out = QAction(QIcon(":/icons/zoom_out"),
                                      "Zoom out", self)
        self.action_zoom_out.setStatusTip("Zoom the graph pane out")
        self.action_zoom_out.triggered.connect(
                              self.graph_main_widget.view.scale_view_out)

    def _fill_examples_menu(self):
        if os.path.exists(examples_paths["models"]):
            fill_examples_menu(self.open_examples_menu,
                               examples_paths["models"],
                               self.open_mp_code)
        else:
            print("Examples path is not configured.")

    # menus
    def define_menus(self):
        menubar = self.w.menuBar()
        menubar.setNativeMenuBar(False)

        # menu | file
        file_menu = QMenu("&File")
        menubar.addMenu(file_menu)

        # menu | file | open
        file_menu.addAction(self.action_open_mp_code_file)

        # menu | file | open examples
        self.open_examples_menu = QMenu("Open Example")
        self.open_examples_menu.addMenu(self.open_examples_menu)
        self.open_examples_menu.setStatusTip("Open MP Code Example")
        self.open_examples_menu.aboutToShow.connect(
                                    self._fill_examples_menu)

        # menu | file | save MP Code
        file_menu.addAction(self.action_save_mp_code_file)

        # menu | file | close
        file_menu.addAction(self.action_close_mp_code_file)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | open examples
        file_menu.addMenu(self.open_examples_menu)

        # menu | file | search .mp files
        file_menu.addAction(
                   self.search_mp_files_dialog_wrapper.action_search_mp_files)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | Save snapshot
        file_menu.addAction(self.session_snapshots.action_take_snapshot)

        # menu | file | Manage snapshots
        file_menu.addAction(self.session_snapshots.action_manage_snapshots)

        # menu | file | session persistence
        file_menu.addAction(
                     self.session_persistence.action_restore_previous_session)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | import Gryphon Graph file
        file_menu.addAction(self.gry_manager.action_import_gry_file)

        # menu | file | export Gryphon Graph file
        file_menu.addAction(self.gry_manager.action_export_gry_file)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | export trace
        file_menu.addAction(self.export_trace_manager.action_export_trace)

        # menu | file | export all traces
        file_menu.addAction(self.export_trace_manager.action_export_all_traces)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | exit
        file_menu.addAction(self.action_exit)

        # menu | actions
        actions_menu = menubar.addMenu('&Actions')

        # menu | actions | run
        actions_menu.addAction(self.action_run_cancel)

        # menu | actions | separator
        file_menu.addSeparator()

        # menu | actions | clear log
        actions_menu.addAction(self.action_clear_log)

        # menu | settings
        self.settings_menu = menubar.addMenu('&Settings')

        # menu | settings | dark mode
        self.settings_menu.addAction(
                            self.preferences_manager.action_use_dark_mode)

        # menu | settings | appearance
        self.settings_appearance_menu = SettingsAppearanceMenu(self.w, 
                              self.settings_manager, self.graphs_manager)
        self.settings_menu.addMenu(self.settings_appearance_menu)

        # menu | settings | reset GUI preferences
        self.settings_menu.addAction(
                         self.preferences_manager.action_reset_preferences)

        # menu | settings | separator
        self.settings_menu.addSeparator()

        # menu | settings | code editor preferences
        self._code_editor_menu = make_code_editor_menu(self.preferences_manager,
                               self.mp_code_view_1, self.mp_code_view_2)
        self.settings_menu.addMenu(self._code_editor_menu)

        # menu | settings | graph pane preferences
        self.graph_pane_menu = make_graph_pane_menu(self)
        self.settings_menu.addMenu(self.graph_pane_menu)

        # menu | settings | graph list navigation pane preferences
        self.settings_menu.addMenu(self.preferences_manager.graph_list_menu)

        # menu | settings | separator
        self.settings_menu.addSeparator()

        # menu | settings | trace generator path
        self.settings_menu.addAction(self.action_trace_generator_path)

        # menu | settings | preloaded examples path
        self.settings_menu.addAction(self.action_examples_path)

        # menu | AI
        if self.gryphon_ai_manager:
            ai_menu = menubar.addMenu('&AI')
            ai_menu.addAction(self.gryphon_ai_manager.action_refine_model)
            ai_menu.addAction(self.gryphon_ai_manager.action_analyze_trace)
            ai_menu.addSeparator()
            ai_menu.addAction(self.gryphon_ai_manager.action_ai_chat)
            ai_menu.addAction(self.gryphon_ai_manager.action_open_traces)

        # menu | help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.action_about)
        help_menu.addAction(self.action_keyboard_shortcuts)
        help_menu.addAction(self.action_report_an_issue)

    # toolbar items
    def define_toolbar(self):
        toolbar = self.w.addToolBar("MP_Py Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.open_menu = QMenu()
        self.open_menu.addAction(self.action_open_mp_code_file)
        self.open_menu.addMenu(self.open_examples_menu)
        self.open_menu.addAction(
                   self.search_mp_files_dialog_wrapper.action_search_mp_files)
        self.open_menu_button = mp_menu_button(self.open_menu,
                                               QIcon(":/icons/open"),
                                               "Open",
                                               "Open MP schema file")
        toolbar.addWidget(self.open_menu_button)
        toolbar.addSeparator()
        toolbar.addAction(self.action_run_cancel)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Scope"))
        toolbar.addWidget(self.scope_spinner.spinner)
        toolbar.addSeparator()
        toolbar.addWidget(self.graph_main_widget.scene.event_menu \
                                                    .event_menu_button)
        toolbar.addSeparator()
        toolbar.addAction(self.action_zoom_in)
        toolbar.addAction(self.action_zoom_out)

    ############################################################
    # action handlers
    ############################################################

    # help...
    @Slot()
    def help_mp_py_um(self):
        path = os.path.abspath("../doc/mp_py_um/mp_py_um.pdf")
        if not os.path.exists(path):
            path = os.path.abspath("pdf/mp_py_um.pdf")
        if os.path.exists(path):
            webbrowser.open("file://%s"%path)
        else:
            log("Error: Missing help file.")

    # Keyboard Shortcuts...
    @Slot()
    def keyboard_shortcuts(self):
        wrapper = KeyboardDialogWrapper(self.w)
        wrapper.show()

    # About MP...
    @Slot()
    def about_mp(self):
        wrapper = AboutMPDialogWrapper(self.w)
        wrapper.show()

    # Report an issue...
    @Slot()
    def report_an_issue(self):
        text = "To report an issue please open the Monterey Phoenix Gryphon " \
               "issue tracker at " \
               "https://gitlab.nps.edu/monterey-phoenix/user-interfaces" \
               '/gryphon/-/issues and click the "New issue" button.\n\n' \
               "Please include the version of the Operating System you are " \
               "using and that you are using Gryphon %s.  " \
               "If possible, please include a screen capture.\n\n" \
               "Please de-identify screen capture and other " \
               "submitted information as issues and related comments are " \
               "public."%VERSION
        message_popup(None, text)

    # Open MP Code file
    @Slot()
    def select_and_open_mp_code_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.w,
                        "Open MP Code file",
                        preferences["preferred_mp_code_dir"],
                        "MP Code files (*.mp);;All Files (*)",
                        options = QFileDialog.Option.DontUseNativeDialog)

        if filename:
            # remember the preferred path
            head, _tail = os.path.split(filename)
            preferences["preferred_mp_code_dir"] = head

            # open the file
            self.open_mp_code(filename)

    # Save MP Code file
    @Slot()
    def save_mp_code_file(self):

        # suggested filename
        schema_name = self.mp_code_manager.schema_name()
        suggested_filename = "%s.mp" % schema_name

        mp_code_filename, _ = QFileDialog.getSaveFileName(self.w,
        "Save MP Code file",
        os.path.join(preferences["preferred_mp_code_dir"],
                     suggested_filename),
                     "MP Code files (*.mp);;All Files (*)",
                     options = QFileDialog.Option.DontUseNativeDialog)

        if mp_code_filename:
            # remember the preferred path
            head, _tail = os.path.split(mp_code_filename)
            preferences["preferred_mp_code_dir"] = head

            # save the file
            status = mp_json_io_manager.save_mp_code_file(
                              self.mp_code_manager.text(), mp_code_filename)
            if status:
                # log failure
                log(status)
            else:
                # great, exported.
                log("Saved to file %s" % mp_code_filename)

    # Find MP code file
    @Slot()
    def find_mp_code_file(self):
        wrapper = FindMPFileDialogWrapper(self.w)
        wrapper.show()

    @Slot()
    def select_trace_generator_path(self):
        path = QFileDialog.getExistingDirectory(self.w,
        "Select the path to the MP trace-generator",
        trace_generator_paths["trace_generator_root"],
        options = QFileDialog.Option.DontUseNativeDialog \
                          | QFileDialog.Option.ShowDirsOnly)

        if path:
            change_trace_generator_paths(path)

    @Slot()
    def select_examples_path(self):
        path = QFileDialog.getExistingDirectory(self.w,
        "Select the path to the preloaded examples",
        examples_paths["examples_root"],
        options = QFileDialog.Option.DontUseNativeDialog \
                          | QFileDialog.Option.ShowDirsOnly)

        if path:
            change_examples_paths(path)

    ############################################################
    # primary interfaces
    ############################################################
    # open MP Code file
    def open_mp_code(self, mp_code_filename):
        status, mp_code_text = mp_json_io_manager.read_mp_code_file(
                                                         mp_code_filename)

        if status:
            # log failure
            log(status)
        else:
            # accept request
            clear_log()
            log("Opened MP Code file %s" % mp_code_filename)

            # set mp code
            self.mp_code_manager.set_text(mp_code_text)

            # clear the graph
            self.graphs_manager.clear_graphs()

    # Close MP Code file
    @Slot()
    def close_mp_code(self):

        clear_log()
        # set mp code
        self.mp_code_manager.set_text("")

        # clear the graph
        self.graphs_manager.clear_graphs()
    

    # compile MP Code
    def _request_compile_mp_code(self):
        # compile
        self._compiled_mp_code = self.mp_code_manager.text()
        self._compiled_scope = self.scope_spinner.scope()
        self._compiled_schema_name = self.mp_code_manager.schema_name()
        self._compiled_settings = settings.copy()

        # set visual state
        self.set_is_compiling(True)

        log("Compiling %s..." % self._compiled_schema_name)
        self.trace_generator_manager.mp_compile(
                           self._compiled_schema_name,
                           self._compiled_scope,
                           self._compiled_mp_code)

    # receive trace-generated json from the compiled MP Code
    @Slot(str, dict, str)
    def response_compile_mp_code(self, status, tg_data, _log):

        # log the compilation log
        log(_log)

        if status:
            # log failure
            log(status)

        else:

            # accept graphs
            gry_graphs = tg_to_gry_graphs(tg_data)
            mp_code = self.mp_code_manager.text()
            scope = self.scope_spinner.scope()

            # zz currently, manage scalability issue by limiting the number
            # of graphs to accept
            max_global_plus_traces = 10001
            num_global_plus_traces = len(gry_graphs)
            if num_global_plus_traces > max_global_plus_traces:
                message_popup(None, "Too many traces were generated: %d.  "
                                    " keeping only the first %d."%(
                                               num_global_plus_traces - 1,
                                               max_global_plus_traces - 1))
                gry_graphs = gry_graphs[:max_global_plus_traces]

            # the default selected graph index is 1 else 0
            if "traces" in tg_data and len(tg_data["traces"]) > 0:
                selected_graph_index = 1
            else:
                selected_graph_index = 0

            # gry data
            self.graphs_manager.set_graphs(gry_graphs,
                                           self._compiled_schema_name,
                                           self._compiled_scope,
                                           selected_graph_index)
            log("Compiled %s"%self._compiled_schema_name)

            # Capture trace data for AI
            if self.gryphon_ai_manager:
                self.gryphon_ai_manager.set_trace_data(
                    tg_data,
                    schema_name=self._compiled_schema_name,
                    mp_code=self._compiled_mp_code,
                    scope=self._compiled_scope
                )

            # write .tg generated .gry JSON, indented with sorted keys
            gry_data = {
                   "graphs":gry_graphs,
                   "mp_code":self._compiled_mp_code,
                   "schema_name":self._compiled_schema_name,
                   "scope":self._compiled_scope,
                   "selected_graph_index":selected_graph_index,
                   "settings":self._compiled_settings,
                       }
            with open(TRACE_GENERATED_OUTFILE_GRY, "w") as f:
                json.dump(gry_data, f, indent=4, sort_keys=True)

        # set visual state
        self.set_is_compiling(False)

    # cancel compile MP Code
    def _cancel_compile_mp_code(self):
        # cancel
        schema_name = self.mp_code_manager.schema_name()
        log("Canceling compiling %s" % schema_name)
        self.trace_generator_manager.mp_cancel_compile()

    def _run_cancel_compile_mp_code(self):
        if self._is_compiling:
            self._cancel_compile_mp_code()
        else:
            self._request_compile_mp_code()

    def _set_run_cancel_button_state(self):
        if self._is_compiling:
            self.action_run_cancel.setIcon(QIcon(":/icons/cancel"))
            self.action_run_cancel.setText("Stop")
        else:
            self.action_run_cancel.setIcon(QIcon(":/icons/run"))
            self.action_run_cancel.setText("Run")

    # run and cancel widget state
    def set_is_compiling(self, is_compiling):

        self._is_compiling = is_compiling

        # run/cancel
        self._set_run_cancel_button_state()

        # navigation column
        self.navigation_column.setDisabled(is_compiling)

        # other actions and menus
        self.action_open_mp_code_file.setDisabled(is_compiling)
        self.action_close_mp_code_file.setDisabled(is_compiling)
        self.open_examples_menu.setDisabled(is_compiling)
        self.gry_manager.action_import_gry_file.setDisabled(is_compiling)
        self.gry_manager.action_export_gry_file.setDisabled(is_compiling)
        self.export_trace_manager.action_export_trace.setDisabled(is_compiling)
        self.export_trace_manager.action_export_all_traces.setDisabled(
                                                                  is_compiling)
        self.open_menu_button.setDisabled(is_compiling)
        self.graph_main_widget.scene.event_menu.event_menu_button \
                                                  .setDisabled(is_compiling)
        self.scope_spinner.spinner.setDisabled(is_compiling)

        # note: these two are disabled when compiling because the
        # local trace generator changes the local directory, which
        # makes these fail.
        self.action_help.setDisabled(is_compiling)
        self.action_about.setDisabled(is_compiling)

