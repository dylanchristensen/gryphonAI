import os
from glob import glob
import signal
import json
import webbrowser
from PySide6.QtWidgets import QStyle # for PM_ScrollBarExtent
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QDesktopServices
from mp_main_window import MPMainWindow
from version_file import VERSION
import resources_rc
from main_splitter import MainSplitter
from mp_code_column import MPCodeColumn
from navigation_column import NavigationColumn
from graph_list_selection_spinner import GraphListSelectionSpinner
from main_graph_scene import MainGraphScene
from main_graph_view import MainGraphView
from graph_list_view import GraphListView
from graph_list_table_dialog import GraphListTableDialog
from navigation_column_width_manager import NavigationColumnWidthManager
from scope_spinner import ScopeSpinner
from graph_metadata_label import GraphMetadataLabel
from graphs_manager import GraphsManager
from graph_list_table_model import GraphListTableModel
from graph_list_sort_filter_proxy_model import GraphListSortFilterProxyModel
from graph_list_selection_model import GraphListSelectionModel
from mp_code_manager import MPCodeManager
from mp_code_view import MPCodeView
from mp_code_change_tracker import MPCodeChangeTracker
from edit_menu import EditMenu
from code_editor_settings_menu import make_code_editor_settings_menu
from gry_manager import GryManager
from settings_themes_menu import SettingsThemesMenu
from socket_client_endpoint_menu import SocketClientEndpointMenu
from graph_pane_menu import GraphPaneMenu
from export_trace_manager import ExportTraceManager
from mp_logger import set_logger_targets, log, log_to_pane, log_to_statusbar, \
                    clear_log, begin_timestamps, timestamp, show_timestamps
from mp_style import mp_menu_button, MenuBarStatusTipEventRemover
import mp_json_io_manager
from trace_generator_manager import TraceGeneratorManager, \
                                    TraceGeneratorCallback
from preferences import preferences
from preferences_manager import PreferencesManager
from settings import settings
from settings_manager import SettingsManager
from spellcheck_whitelist_manager import SpellcheckWhitelistManager
from spellcheck_whitelist_dialog_wrapper import SpellcheckWhitelistDialogWrapper
from session_persistence import SessionPersistence
from session_snapshots import SessionSnapshots
from session_snapshots_dialog_wrapper import snapshot_files
from keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from about_mp_dialog_wrapper import AboutMPDialogWrapper
from search_mp_files_dialog_wrapper import SearchMPFilesDialogWrapper
from model_statistics_dialog import ModelStatisticsDialog
from tg_to_gry import tg_to_gry_graphs
from empty_gry_graph import empty_gry_graph
from paths_trace_generator import trace_generator_paths
from paths_trace_generator_manager import change_trace_generator_paths
from paths_examples import is_bundled, \
                           examples_paths, \
                           change_examples_paths, \
                           schedule_validate_examples_paths
from paths_gryphon import TRACE_GENERATED_OUTFILE_GRY
from examples_menu import fill_examples_menu
from report_an_issue import report_an_issue
from startup_options import parse_startup_options
from mp_file_dialog import get_open_filename, get_save_filename, \
                           get_existing_directory
from mp_code_parser import mp_code_schema
from mp_code_filename import active_mp_code_filename, \
                             set_active_mp_code_filename
from verbose import verbose
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
        self.w = MPMainWindow(self)
        self.w.setWindowTitle("Monterey Phoenix v4 - Gryphon GUI %s"%VERSION)
        self.w.setWindowIcon(QIcon(":/icons/mp_logo"))

        # user preferences manager
        self.preferences_manager = PreferencesManager(self)

        # graph settings manager
        self.settings_manager = SettingsManager(self.w,
                         self.preferences_manager.signal_preferences_changed)

        # session persistence
        self.session_persistence = SessionPersistence(self)

        # session snapshots
        self.session_snapshots = SessionSnapshots(self)

        # spellcheck manager
        self.spellcheck_whitelist_manager = SpellcheckWhitelistManager()

        # spellcheck whitelist dialog wrapper
        self.spellcheck_whitelist_dialog_wrapper = \
              SpellcheckWhitelistDialogWrapper(self.w,
                                         self.spellcheck_whitelist_manager)

        # the graph list table model
        self.graph_list_table_model = GraphListTableModel(self.w)

        # the graphs manager
        self.graphs_manager = GraphsManager(self.graph_list_table_model,
                                            self.settings_manager)

        # the graph list width manager
        self.navigation_column_width_manager = NavigationColumnWidthManager(
                  self.w.style().pixelMetric(
                                   QStyle.PixelMetric.PM_ScrollBarExtent))

        # the main splitter which emits size_changed
        self.main_splitter = MainSplitter(self.navigation_column_width_manager)

        # the graph list proxy model
        self.graph_list_proxy_model = GraphListSortFilterProxyModel(
                       self.graph_list_table_model,
                       self.preferences_manager.signal_preferences_changed,
                       self.settings_manager.signal_settings_changed)

        # the graph list selection model
        self.graph_list_selection_model = GraphListSelectionModel(
                                        self.graph_list_table_model,
                                        self.graph_list_proxy_model)

        # the graph list view
        self.graph_list_view = GraphListView(
                         self.main_splitter,
                         self.graphs_manager,
                         self.graph_list_proxy_model,
                         self.graph_list_selection_model,
                         self.navigation_column_width_manager,
                         self.preferences_manager.signal_preferences_changed)

        # the graph list table dialog
        self.graph_list_table_dialog = GraphListTableDialog(self.w,
                                            self.graph_list_proxy_model,
                                            self.graph_list_selection_model)

        # the main graph scene and view
        self.main_graph_view = MainGraphView(
                                   self.graphs_manager.signal_graphs_loaded)
        self.graph_pane_menu = GraphPaneMenu(self)
        self.main_graph_scene = MainGraphScene(self.graph_list_table_model,
                                               self.graph_list_selection_model,
                                               self.settings_manager,
                                               self.graph_pane_menu)
        self.main_graph_view.setScene(self.main_graph_scene)
        self.main_graph_view.scale_view(preferences["graph_pane_scale"])

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
        # the MP Code manager
        self.mp_code_manager = MPCodeManager(
                  self.preferences_manager.signal_preferences_changed,
                  self.settings_manager.signal_settings_changed,
                  self.spellcheck_whitelist_manager.signal_spellcheck_changed,
                  self.statusbar)

        # the MP Code change tracker
        self.mp_code_change_tracker = MPCodeChangeTracker(self)

        # persistent dialogs
        self.search_mp_files_dialog_wrapper = SearchMPFilesDialogWrapper(
                  self.w,
                  self.preferences_manager.signal_preferences_changed,
                  self.settings_manager.signal_settings_changed,
                  self.spellcheck_whitelist_manager.signal_spellcheck_changed,
                  self.open_mp_code)
        self.model_statistics_dialog = ModelStatisticsDialog(
                         self.w, self.graphs_manager,
                         self.mp_code_manager.signal_mp_code_loaded,
                         self.preferences_manager.signal_preferences_changed)

        # the two MP Code editor view windows
        self.mp_code_view_1 = MPCodeView(self.mp_code_manager,
                   self.preferences_manager,
                   self.spellcheck_whitelist_manager,
                   self.spellcheck_whitelist_dialog_wrapper,
                   self.search_mp_files_dialog_wrapper.action_search_mp_files,
                   self.application,
                   1)
        self.mp_code_view_2 = MPCodeView(self.mp_code_manager,
                   self.preferences_manager,
                   self.spellcheck_whitelist_manager,
                   self.spellcheck_whitelist_dialog_wrapper,
                   self.search_mp_files_dialog_wrapper.action_search_mp_files,
                   self.application,
                   2)

        # .gry manager
        self.gry_manager = GryManager(self.w, self.graphs_manager,
                                      self.mp_code_manager,
                                      self.graph_list_selection_model,
                                      self.settings_manager,
                                      self.mp_code_change_tracker)

        # AI Manager
        try:
            self.gryphon_ai_manager = GryphonAIManager(self)
        except Exception as e:
            # Don't crash Gryphon if AI initialization fails
            import traceback
            print(f"Warning: Failed to initialize Gryphon AI: {e}")
            traceback.print_exc()
            self.gryphon_ai_manager = None

        # the scope spinner containing spinner=QSpinBox
        self.scope_spinner = ScopeSpinner(
                                  self.mp_code_manager.signal_mp_code_loaded)

        # export trace manager
        self.export_trace_manager = ExportTraceManager(self.w,
                                          self.graphs_manager,
                                          self.graph_list_selection_model,
                                          application)

        # graph list selection spinner
        self.graph_list_selection_spinner = GraphListSelectionSpinner(
                                self.graph_list_proxy_model,
                                self.graph_list_selection_model)

        # the central widget containing the main split pane
        self.mp_code_column = MPCodeColumn(self)
        self.mp_code_column.set_splitter_sizes(
                  preferences["code_column_splitter_sizes"])
        self.navigation_column = NavigationColumn(self)
        self.main_splitter.addWidget(self.mp_code_column)
        self.main_splitter.addWidget(self.main_graph_view)
        self.main_splitter.addWidget(self.navigation_column)
        self.main_splitter.setSizes(preferences["main_splitter_sizes"])
        self.w.setCentralWidget(self.main_splitter)

        # actions and menus
        self.define_actions()
        self.define_menus()

        # the toolbar
        self.add_toolbar()

        # current compile state for buttons
        self.set_is_compiling(False)

        # state for preference actions
        self.preferences_manager.set_action_states()

        # do these before shutdown
        application.aboutToQuit.connect(
                      self.trace_generator_manager.mp_clean_shutdown)
        application.aboutToQuit.connect(
                      self.preferences_manager.save_preferences)
        application.aboutToQuit.connect(
                      self.session_persistence.save_this_session)
        application.aboutToQuit.connect(self._clear_clipboard)

        # get command line options
        parse_startup_options(self)

        # enqueue actions to start on Qt event loop
        if not is_bundled():
            schedule_validate_examples_paths(self.w)

        self.w.show()

        # accept Ctrl C
        signal.signal(signal.SIGINT, self.make_ctrl_c_closure_function())

    @Slot()
    def _clear_clipboard(self):
        # Qt crashes with:
        # QFontDatabase: Must construct a QGuiApplication before accessing
        # QFontDatabase
        # Aborted (core dumped)
        # so we clear it when Gryphon closes to avoid this crash.
        QGuiApplication.clipboard().clear()

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
        self.action_exit.setToolTip("Exit MP")
        self.action_exit.triggered.connect(self.w.close)

        # action keyboard_shortcuts
        self.action_keyboard_shortcuts = QAction("&Keyboard Shortcuts", self.w)
        self.action_keyboard_shortcuts.setToolTip(
                                        "Keyboard shorcuts for MP controls")
        self.action_keyboard_shortcuts.triggered.connect(
                                        self.keyboard_shortcuts)

        # action about
        self.action_about = QAction(QIcon(":/icons/about_mp"),
                                   "&About MP", self)
        self.action_about.setToolTip("about MP")
        self.action_about.triggered.connect(self.about_mp)

        # action online documentation
        self.action_online_documentation = QAction(QIcon(
                   ":/icons/documentation"), "Online &documentation", self)
        self.action_online_documentation.setToolTip(
                                     "Online documentation for Gryphon")
        self.action_online_documentation.triggered.connect(
                                              self.online_documentation)

        # action report an issue
        self.action_report_an_issue = QAction("&Report an issue...", self)
        self.action_report_an_issue.setToolTip("Report an issue about MP")
        self.action_report_an_issue.triggered.connect(self._report_an_issue)

        # action run/cancel
        self.action_run_cancel = QAction(self)
        self.action_run_cancel.setToolTip("Generate traces from MP Code")
        self.action_run_cancel.triggered.connect(
                                        self._run_cancel_compile_mp_code)

        # action show model statistics
        self.action_show_model_statistics = QAction(
                             QIcon(":/icons/show_model_statistics"),
                             "&Show model statistics...", self)
        self.action_show_model_statistics.setToolTip(
                                           "Show statistics about models")
        self.action_show_model_statistics.triggered.connect(
                                          self._show_model_statistics)

        # action clear log
        self.action_clear_log = QAction(QIcon(":/icons/clear_log"),
                                       "&Clear status log", self)
        self.action_clear_log.setToolTip("Clear the status log pane")
        self.action_clear_log.triggered.connect(clear_log)

        # action open MP Code file
        self.action_open_mp_code_file = QAction(QIcon(":/icons/open"),
                                                "&Open .mp...", self)
        self.action_open_mp_code_file.setToolTip("Open MP Code File")
        self.action_open_mp_code_file.triggered.connect(
                                           self.select_and_open_mp_code_file)

        # action close MP Code file
        self.action_close_mp_code_file = QAction(QIcon(":/icons/close"),
                                                 "Close .mp", self)
        self.action_close_mp_code_file.setToolTip("Close MP Code File")
        self.action_close_mp_code_file.triggered.connect(self.close_mp_code)

        # action save MP Code file
        self.action_save_mp_code_file = QAction(QIcon(":/icons/save"),
                                                "&Save .mp", self)
        self.action_save_mp_code_file.setShortcut('Ctrl+S')
        self.action_save_mp_code_file.setToolTip("Save MP Code file")
        self.action_save_mp_code_file.triggered.connect(
                                           self.save_mp_code_file)

        # action save MP Code file as
        self.action_save_mp_code_file_as = QAction(QIcon(":/icons/save"),
                                                "Save .mp &as...", self)
        self.action_save_mp_code_file_as.setToolTip("Save MP Code file")
        self.action_save_mp_code_file_as.triggered.connect(
                                           self.save_mp_code_file_as)

        # action settings trace generator path...
        self.action_trace_generator_path = QAction(
                                     "Trace Generator Path...", self)
        self.action_trace_generator_path.setToolTip(
                                     "Set the path to the trace-generator")
        self.action_trace_generator_path.triggered.connect(
                                     self.select_trace_generator_path)

        # action settings preloaded examples path...
        self.action_examples_path = QAction(
                                     "Preloaded Examples Path...", self)
        self.action_examples_path.setToolTip(
                                     "Set the path to preloaded examples")
        self.action_examples_path.triggered.connect(
                                     self.select_examples_path)
        self.action_examples_path.setDisabled(is_bundled())

    def _configure_file_menu(self):
        # disable save when there is no active filename
        self.action_save_mp_code_file.setEnabled(bool(
                                                 active_mp_code_filename()))

        # disable actions when compiling
        is_compiling = self._is_compiling
        self.action_open_mp_code_file.setDisabled(is_compiling)
        self.action_close_mp_code_file.setDisabled(is_compiling)
        self.open_examples_menu.setDisabled(is_compiling)
        self.gry_manager.action_import_gry_file.setDisabled(is_compiling)
        self.gry_manager.action_export_gry_file.setDisabled(is_compiling)
        self.export_trace_manager.action_export_trace.setDisabled(is_compiling)
        self.export_trace_manager.action_export_all_traces.setDisabled(
                                                                  is_compiling)
        self.session_persistence.action_restore_previous_session.setDisabled(
                                                                  is_compiling)

        # disable managing snapshots when there are no snapshots
        has_snapshots = bool(len(snapshot_files()))
        self.session_snapshots.action_manage_snapshots.setDisabled(
                                                         not has_snapshots)

    def _configure_settings_menu(self):
        self.settings_manager.action_show_type_1_probability.setChecked(
                               settings["trace_show_type_1_probability"])

    def _fill_examples_menu(self):
        if os.path.exists(examples_paths["models"]):
            fill_examples_menu(self.open_examples_menu,
                               examples_paths["models"],
                               self.open_mp_code)
        else:
            print("Examples path is not configured.")

    def _configure_save_menu(self):
        # disable save in toolbar's save menu
        self.action_save_mp_code_file.setEnabled(bool(
                                                active_mp_code_filename()))

    def _enable_manage_snapshots(self):
        has_snapshots = bool(len(snapshot_files()))
        self.session_snapshots.action_manage_snapshots.setDisabled(
                                                         not has_snapshots)
    # menus
    def define_menus(self):
        menubar = self.w.menuBar()
        menubar.setNativeMenuBar(False)
        menubar.installEventFilter(MenuBarStatusTipEventRemover(self.w))

        # menu | file
        self.file_menu = QMenu("&File")
        menubar.addMenu(self.file_menu)
        self.file_menu.aboutToShow.connect(self._configure_file_menu)

        # menu | file | open
        self.file_menu.addAction(self.action_open_mp_code_file)

        # menu | file | open examples
        self.open_examples_menu = QMenu("Open Example")
        self.open_examples_menu.setToolTip("Open MP Code Example")
        self.open_examples_menu.aboutToShow.connect(
                                    self._fill_examples_menu)

        # menu | file | save MP Code
        self.file_menu.addAction(self.action_save_mp_code_file)

        # menu | file | save MP Code as
        self.file_menu.addAction(self.action_save_mp_code_file_as)

        # menu | file | close
        self.file_menu.addAction(self.action_close_mp_code_file)

        # menu | file | separator
        self.file_menu.addSeparator()

        # menu | file | open examples
        self.file_menu.addMenu(self.open_examples_menu)

        # menu | file | search .mp files
        self.file_menu.addAction(
                   self.search_mp_files_dialog_wrapper.action_search_mp_files)

        # menu | file | separator
        self.file_menu.addSeparator()

        # menu | file | Save snapshot
        self.file_menu.addAction(self.session_snapshots.action_take_snapshot)

        # menu | file | Manage snapshots
        self.file_menu.addAction(self.session_snapshots.action_manage_snapshots)

        # menu | file | session persistence
        self.file_menu.addAction(
                     self.session_persistence.action_restore_previous_session)

        # menu | file | separator
        self.file_menu.addSeparator()

        # menu | file | import Gryphon Graph file
        self.file_menu.addAction(self.gry_manager.action_import_gry_file)

        # menu | file | export Gryphon Graph file
        self.file_menu.addAction(self.gry_manager.action_export_gry_file)

        # menu | file | separator
        self.file_menu.addSeparator()

        # menu | file | export trace
        self.file_menu.addAction(self.export_trace_manager.action_export_trace)

        # menu | file | export all traces
        self.file_menu.addAction(
                       self.export_trace_manager.action_export_all_traces)

        # menu | file | separator
        self.file_menu.addSeparator()

        # menu | file | exit
        self.file_menu.addAction(self.action_exit)

        # menu | edit
        self.edit_menu = menubar.addMenu(EditMenu(self))

        # menu | actions
        actions_menu = menubar.addMenu('&Actions')

        # menu | actions | run
        actions_menu.addAction(self.action_run_cancel)

        # menu | actions | show model statistics
        actions_menu.addAction(self.action_show_model_statistics)

        # menu | actions | clear log
        actions_menu.addAction(self.action_clear_log)

        # menu | settings
        self.settings_menu = menubar.addMenu('&Settings')
        self.settings_menu.aboutToShow.connect(self._configure_settings_menu)

        # menu | settings | use dark mode
        self.settings_menu.addAction(
                            self.preferences_manager.action_use_dark_mode)

        # menu | settings | show type 1 probability
        self.settings_menu.addAction(
                    self.settings_manager.action_show_type_1_probability)

        # menu | settings | separator
        self.settings_menu.addSeparator()

        # menu | settings | themes
        self.settings_themes_menu = SettingsThemesMenu(self.w,
                                                   self.settings_manager)
        self.settings_menu.addMenu(self.settings_themes_menu)

        # menu | settings | code editor preferences
        self._code_editor_settings_menu = make_code_editor_settings_menu(self)
        self.settings_menu.addMenu(self._code_editor_settings_menu)

        # menu | settings | graph pane preferences
        self.settings_menu.addMenu(self.graph_pane_menu)

        # menu | settings | graph list navigation pane preferences
        self.settings_menu.addMenu(self.preferences_manager.graph_list_menu)

        # menu | settings | reset GUI preferences
        self.settings_menu.addAction(
                         self.preferences_manager.action_reset_preferences)

        # menu | settings | separator
        self.settings_menu.addSeparator()

        # menu | settings | ignore model statistics warnings
        self.settings_menu.addAction(self.model_statistics_dialog
                                  .action_ignore_model_statistics_warnings)

        # menu | settings | separator
        self.settings_menu.addSeparator()

        # menu | settings | Gryphon configuration
        gryphon_configuration_menu = self.settings_menu.addMenu(
                                                 'Gryphon configuration')
        gryphon_configuration_menu.addAction(self.action_trace_generator_path)
        gryphon_configuration_menu.addAction(self.action_examples_path)
        self.socket_client_endpoint_menu = SocketClientEndpointMenu()
        gryphon_configuration_menu.addMenu(self.socket_client_endpoint_menu)

        # menu | AI
        if self.gryphon_ai_manager:
            ai_menu = menubar.addMenu('&AI')
            ai_menu.addAction(self.gryphon_ai_manager.action_refine_model)
            ai_menu.addAction(self.gryphon_ai_manager.action_analyze_trace)

        # menu | help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.action_about)
        help_menu.addAction(self.action_keyboard_shortcuts)
        help_menu.addAction(self.action_online_documentation)
        help_menu.addAction(self.action_report_an_issue)

    # the toolbar
    def add_toolbar(self):
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
        self.save_menu = QMenu()
        self.save_menu.aboutToShow.connect(self._configure_save_menu)
        self.save_menu.addAction(self.action_save_mp_code_file)
        self.save_menu.addAction(self.action_save_mp_code_file_as)
        self.save_menu_button = mp_menu_button(self.save_menu,
                                               QIcon(":/icons/save"),
                                               "Save",
                                               "SaveMP schema file")
        toolbar.addWidget(self.save_menu_button)
        toolbar.addSeparator()
        toolbar.addAction(self.action_run_cancel)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Scope"))
        toolbar.addWidget(self.scope_spinner.spinner)
        toolbar.addSeparator()
        toolbar.addWidget(self.main_graph_scene.trace_event_menu \
                                             .trace_event_menu_button)
        toolbar.addSeparator()
        toolbar.addAction(self.graph_pane_menu.action_zoom_in)
        toolbar.addAction(self.graph_pane_menu.action_zoom_out)
        toolbar.addAction(self.graph_pane_menu.action_zoom_reset)

        # far right side
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        toolbar.addAction(self.preferences_manager.action_use_dark_mode)

    ############################################################
    # action handlers
    ############################################################

    # Keyboard Shortcuts...
    @Slot()
    def keyboard_shortcuts(self):
        dialog = KeyboardShortcutsDialog(self.w)
        dialog.show()

    # About MP...
    @Slot()
    def about_mp(self):
        wrapper = AboutMPDialogWrapper(self.w)
        wrapper.show()

    # Online documentation
    @Slot()
    def online_documentation(self):
        QDesktopServices.openUrl(QUrl("https://gitlab.nps.edu/"
                   "monterey-phoenix/user-interfaces/gryphon/-/wikis/home"))

    # Report an issue...
    @Slot()
    def _report_an_issue(self):
        report_an_issue(self.w)

    # Open MP Code file
    @Slot()
    def select_and_open_mp_code_file(self):
        filename = get_open_filename(self.w,
                        "Open MP Code file",
                        preferences["preferred_mp_code_dir"],
                        "MP Code files (*.mp);;All Files (*)")

        if filename:
            # remember the preferred path
            head, _tail = os.path.split(filename)
            preferences["preferred_mp_code_dir"] = head

            # open the file
            self.open_mp_code(filename)

        else:
            status = "Open filename not selected."
            log(status)

    # Save MP Code file
    @Slot()
    def save_mp_code_file(self):

        mp_code_text = self.mp_code_manager.text()

        # suggested filename
        filename = active_mp_code_filename()
        if not filename:
            raise RuntimeError("bad")

        # The full path is the preferred directory plus the suggested filename.
        # This allows us to use the user's folder for opened examples.
        full_mp_code_filename = os.path.join(
                              preferences["preferred_mp_code_dir"], filename)

        # save the file
        status = mp_json_io_manager.save_mp_code_file(
                         mp_code_text, full_mp_code_filename)
        if status:
            # log failure
            log(status)
        else:
            # great, exported.
            log("Saved to file %s" % full_mp_code_filename)

            # unset mp code change flag
            self.mp_code_change_tracker.unset_is_modified()

    # Save MP Code file as
    @Slot()
    def save_mp_code_file_as(self):

        mp_code_text = self.mp_code_manager.text()

        # suggested filename
        currently_active_filename = active_mp_code_filename()
        if currently_active_filename:
            # use the actively opened filename
            suggested_filename = currently_active_filename
        else:
            # use the schema name with .mp added
            schema_name = mp_code_schema(mp_code_text)
            suggested_filename = "%s.mp" % schema_name

        # The full path is the preferred directory plus the suggested filename.
        # This allows us to use the user's folder for opened examples.
        full_suggested_filename = os.path.join(
                   preferences["preferred_mp_code_dir"], suggested_filename)

        full_mp_code_filename = get_save_filename(self.w,
                   "Save MP Code file", full_suggested_filename,
                   "MP Code files (*.mp);;All Files (*)")

        if full_mp_code_filename:
            # save the file
            status = mp_json_io_manager.save_mp_code_file(
                         mp_code_text, full_mp_code_filename)
            if status:
                # log failure
                log(status)
            else:
                # great, exported.
                log("Saved to file %s" % full_mp_code_filename)

                # remember the preferred path and the active filename
                head, _tail = os.path.split(full_mp_code_filename)
                preferences["preferred_mp_code_dir"] = head
                set_active_mp_code_filename(full_mp_code_filename)

                # unset mp code change flag
                self.mp_code_change_tracker.unset_is_modified()

            # callers don't usually care about status
            return status

        else:
            status = "Save filename not selected."
            log(status)
            return status

    # Find MP code file
    @Slot()
    def find_mp_code_file(self):
        wrapper = FindMPFileDialogWrapper(self.w)
        wrapper.show()

    @Slot()
    def select_trace_generator_path(self):
        path = get_existing_directory(self.w,
                   "Select the path to the MP trace-generator",
                   trace_generator_paths["trace_generator_root"])

        if path:
            change_trace_generator_paths(self.w, path)

    @Slot()
    def select_examples_path(self):
        path = get_existing_directory(self.w,
                   "Select the path to the preloaded examples",
                   examples_paths["examples_root"])

        if path:
            change_examples_paths(self.w, path)

    ############################################################
    # primary interfaces
    ############################################################
    # open MP Code file
    def open_mp_code(self, mp_code_filename):
        # maybe abort request
        status = self.mp_code_change_tracker.maybe_save_discard_or_cancel()
        if status:
            log(status)
            return

        status, mp_code_text = mp_json_io_manager.read_mp_code_file(
                                                         mp_code_filename)

        if status:
            # log failure
            log(status)
        else:
            # accept request
            log("Opened MP Code file %s" % mp_code_filename)

            # set mp code
            self.mp_code_manager.set_text(mp_code_filename, mp_code_text)

            # clear the selection
            self.graph_list_selection_model.select_graph_index(-1)

            # clear the graph
            self.graphs_manager.clear_graphs()

    # Close MP Code file
    @Slot()
    def close_mp_code(self):
        # maybe abort request
        status = self.mp_code_change_tracker.maybe_save_discard_or_cancel()
        if status:
            log(status)
            return

        # set mp code
        self.mp_code_manager.set_text("", "")

        # clear the selection
        self.graph_list_selection_model.select_graph_index(-1)

        # clear the graph
        self.graphs_manager.clear_graphs()

    # compile MP Code
    def _request_compile_mp_code(self):
        # state at start of compilation
        self._proposed_mp_code = self.mp_code_manager.text()
        self._proposed_scope = self.scope_spinner.scope()
        self._proposed_schema_name = mp_code_schema(self._proposed_mp_code)
        self._proposed_settings = settings.copy()
        self._existing_mp_code = self.graphs_manager.mp_code
        self._existing_graphs = self.graphs_manager.graphs
        self._existing_scope = self.graphs_manager.scope
        self._existing_selected_graph_index \
                   = self.graph_list_selection_model.selected_graph_index()

        # set visual state
        self.set_is_compiling(True)

        # begin compilation
        action = "Compiling %s scope %d..."%(self._proposed_schema_name,
                                             self._proposed_scope)
        log_to_statusbar(action)
        begin_timestamps(action)
        self.trace_generator_manager.mp_compile(
                           self._proposed_schema_name,
                           self._proposed_scope,
                           self._proposed_mp_code)

        # clear the selected graph and the graphs
        self.graph_list_selection_model.select_graph_index(-1)
        self.graphs_manager.clear_graphs()

    # receive trace-generated json from the compiled MP Code
    @Slot(str, dict, str)
    def response_compile_mp_code(self, status, tg_data, _log):

        # restore visual state
        self.set_is_compiling(False)

        # disable run button while initializing response
        self.action_run_cancel.setDisabled(True)

        # log the compilation log
        log_to_pane(_log)
        timestamp("Received compilation response")

        # compensate for invalid empty JSON that the trace generator
        # returns when no traces are generated
        if status == "Error running trace-generator: Expecting" \
                     " value: line 1 column 1 (char 0)":
            if verbose():
                log(status)
            status = ""

        if status:
            # log failure
            log(status)

        else:

            # Capture trace data for AI
            if self.gryphon_ai_manager:
                self.gryphon_ai_manager.set_trace_data(tg_data)

            # accept graphs
            gry_graphs = tg_to_gry_graphs(tg_data)
            timestamp("Created gry from tg")
            log("Compiled %s"%self._proposed_schema_name)

            # gry data
            self.graphs_manager.set_graphs(
                                           self._proposed_mp_code,
                                           gry_graphs,
                                           self._proposed_scope,
                                          )
            timestamp("Created graphs from gry")

            # the default selected graph index is 1 else 0
            if "traces" in tg_data and len(tg_data["traces"]) > 0:
                selected_graph_index = 1
            else:
                selected_graph_index = 0
            self.graph_list_selection_model.select_graph_index(
                                                   selected_graph_index)

            # for diagnostics only, and only if it is not large,
            # maybe write the generated .gry JSON, indented with sorted keys
            with open(TRACE_GENERATED_OUTFILE_GRY, "w", encoding='utf-8') as f:
                if len(gry_graphs) < 1000:
                    # prepare the generated .gry JSON, indented with sorted keys
                    gry_data = {
                           "mp_code_current":self.mp_code_manager.text(),
                           "mp_code_runtime":self._proposed_mp_code,
                           "graphs":gry_graphs,
                           "scope":self._proposed_scope,
                           "selected_graph_index":selected_graph_index,
                           "settings":self._proposed_settings,
                               }
                else:
                    # too many graphs so prepare .gry without graphs
                    print("Note: Large graph size %d, graphs not written"
                                                    %len(gry_graphs))
                    gry_data = {
                           "mp_code_current":self.mp_code_manager.text(),
                           "mp_code_runtime":self._proposed_mp_code,
                           "graphs":[empty_gry_graph()],
                           "scope":self._proposed_scope,
                           "selected_graph_index":-1,
                           "settings":self._proposed_settings,
                               }

                json.dump(gry_data, f, indent=4, sort_keys=True)

        # reenable run button after initializing response
        self.action_run_cancel.setDisabled(False)

        # set visual state
        self.set_is_compiling(False)
        show_timestamps()

    # cancel compile MP Code
    def _cancel_compile_mp_code(self):
        # cancel compilation
        log("Canceling compiling %s" % self._proposed_schema_name)
        self.trace_generator_manager.mp_cancel_compile()

        # restore graph data and the selected graph
        self.graphs_manager.restore_graphs(self._existing_mp_code,
                                           self._existing_graphs,
                                           self._existing_scope)
        self.graph_list_selection_model.select_graph_index(
                                   self._existing_selected_graph_index)

    def _run_cancel_compile_mp_code(self):
        if self._is_compiling:
            self._cancel_compile_mp_code()
        else:
            self._request_compile_mp_code()

    def _show_model_statistics(self):
        self.model_statistics_dialog.show()

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

        # run/cancel button
        self._set_run_cancel_button_state()

        # disable some toolbar buttons since they are always visible
        self.open_menu_button.setDisabled(is_compiling)
        self.main_graph_scene.trace_event_menu.trace_event_menu_button \
                                                  .setDisabled(is_compiling)
        self.scope_spinner.spinner.setDisabled(is_compiling)

