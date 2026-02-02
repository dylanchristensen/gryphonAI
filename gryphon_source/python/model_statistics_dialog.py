from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from version_file import VERSION
from preferences import preferences
from model_statistics import model_statistics

_WINDOW_SIZE = QSize(725, 700)

# model statistics are: no_traces, identical_traces, missing_events
# cell properties depend on cell type: header, good, warn, error
# color reference: https://icolorpalette.com/color/green also amber, red
class Cell(QLabel):
    def __init__(self, w, h):
        super().__init__()
        self.setFixedSize(w, h)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_text(self, text, cell_type):
        self.setText(text)
        if preferences["use_dark_mode"]:
            # dark mode css
            border = "border: 0px dark gray; border-radius: 0px"
            header_c = ""
            good_c = "background-color: #00b300" # dark green
            warn_c = "background-color: #a37a00" # dark amber
            error_c = "background-color: #8b0000" # dark red
        else:
            # light mode css
            border = "border: 3px light gray; border-radius: 0px"
            header_c = ""
            good_c = "background-color: #1eff1e" # light green
            good_c = "background-color: #00c000; color: white" # light green
            warn_c = "background-color: #e4ab00; color: white" # light amber
            error_c = "background-color: #ff3737; color: white" # light red

        if cell_type == "header":
            self.setStyleSheet("%s; %s; font-weight: bold"%(
                                              border, header_c))
        elif cell_type == "good":
            self.setStyleSheet("%s; %s"%(border, good_c))
        elif cell_type == "warn":
            self.setStyleSheet("%s; %s"%(border, warn_c))
        elif cell_type == "error":
            self.setStyleSheet("%s; %s"%(border, error_c))

class ModelStatisticsDialog(QDialog):
    """
    Always set statistics content and maybe show the window when graphs
    are loaded.
    Turn off user's preference to ignore statistics warnings when new code
    is loaded.
    Always reset statistics content when preferences change to respond
    to a dark or light mode transition.
    """
    def __init__(self, parent_window, graphs_manager, signal_mp_code_loaded,
                 signal_preferences_changed):
        super().__init__(parent_window)
        self.graphs_manager = graphs_manager
        self._ignore_model_statistics_warnings = False

        # action
        self.action_ignore_model_statistics_warnings = QAction(
                                      "Ignore model statistics warnings")
        self.action_ignore_model_statistics_warnings.setToolTip(
                    "Ignore model statistics warnings generated during run")
        self.action_ignore_model_statistics_warnings.setCheckable(True)
        self.action_ignore_model_statistics_warnings.setChecked(
                                   self._ignore_model_statistics_warnings)

        self.action_ignore_model_statistics_warnings.triggered.connect(
                              self._set_ignore_model_statistics_warnings)

        # connect
        graphs_manager.signal_graphs_loaded.connect(
                         self._set_statistics_content_and_maybe_set_visible)
        signal_mp_code_loaded.connect(self._mp_code_loaded)
        signal_preferences_changed.connect(self._set_statistics_content)

        # state
        self.resize(_WINDOW_SIZE)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("Model Statistics")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        spacing = 10
        w0 = 130
        w1 = 220
        w2 = 350
        h = 70

        # header
        self.header_layout = QHBoxLayout()
        self.header_0 = Cell(w0, h)
        self.header_1 = Cell(w1 + w2, h)
        self.header_2 = Cell(0, 0)
        self._add_row(self.header_layout,
                      self.header_0, self.header_1, self.header_2)

        self.layout.addSpacing(spacing)

        # no traces
        self.no_traces_layout = QHBoxLayout()
        self.no_traces_0 = Cell(w0, h)
        self.no_traces_1 = Cell(w1, h)
        self.no_traces_2 = Cell(w2, h)
        self._add_row(self.no_traces_layout,
                      self.no_traces_0, self.no_traces_1, self.no_traces_2)
        self.no_traces_0.set_text("Traces", "header")

        # identical traces
        self.identical_traces_layout = QHBoxLayout()
        self.identical_traces_0 = Cell(w0, h)
        self.identical_traces_1 = Cell(w1, h)
        self.identical_traces_2 = Cell(w2, h)
        self._add_row(self.identical_traces_layout, self.identical_traces_0,
                      self.identical_traces_1, self.identical_traces_2)

        self.layout.addSpacing(spacing)

        # missing events
        self.missing_events_layout = QHBoxLayout()
        self.missing_events_0 = Cell(w0, h)
        self.missing_events_1 = Cell(w1, h)
        self.missing_events_2 = Cell(w2, h)
        self._add_row(self.missing_events_layout, self.missing_events_0,
                      self.missing_events_1, self.missing_events_2)
        self.missing_events_0.set_text("Events", "header")

        self.layout.addSpacing(spacing)

        # details
        self.details_layout = QHBoxLayout()
        self.details_0 = QPlainTextEdit()
        self.details_0.setReadOnly(True)
        self._add_single(self.details_layout, self.details_0)

        self.layout.addSpacing(spacing)

        # close
        self.close_layout = QHBoxLayout()
        self.close_pb = QPushButton("Close")
        self.close_pb.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                QSizePolicy.Fixed))
        self.close_pb.clicked.connect(self._close_pb_clicked)
        self._add_single(self.close_layout, self.close_pb)

    def _add_row(self, layout, cell_0, cell_1, cell_2):
        self.layout.addLayout(layout)
        layout.addWidget(cell_0)
        layout.addWidget(cell_1)
        layout.addWidget(cell_2)
        layout.addStretch()

    def _add_single(self, layout, single):
        self.layout.addLayout(layout)
        layout.addWidget(single)

    def _set_statistics_content(self):

        # model statistics
        self.schema, scope, self.warnings, statistics_text \
                               = model_statistics(self.graphs_manager)

        if self.schema == "Schema not defined":
            # no active schema
            self.header_1.set_text("Schema:\n%s\n\n"%self.schema, "header")
            self.no_traces_1.set_text("", "warn")
            self.no_traces_2.set_text("", "warn")
            self.identical_traces_1.set_text("", "warn")
            self.identical_traces_2.set_text("", "warn")
            self.missing_events_1.set_text("", "warn")
            self.missing_events_2.set_text("", "warn")
            self.details_0.setPlainText("")
            return

        # header
        self.header_0.set_text("MP Gryphon\n%s"%(VERSION), "header")
        self.header_1.set_text("Schema:\n%s\n\nScope: %s"%(self.schema, scope),
                                                           "header")
        # traces
        if "no_traces" in self.warnings:
            self.no_traces_1.set_text("X  There are no traces", "error")
            self.no_traces_2.set_text(
                            "Constraint(s) may be too restrictive to"
                            " produce any traces at the current scope."
                            "  Try relaxing a constraint.",
                            "error")
        else:
            self.no_traces_1.set_text("\u2713  Traces generated", "good")
            self.no_traces_2.set_text("", "good")

        if "identical_traces" in self.warnings:
            self.identical_traces_1.set_text("X  There are identical traces",
                                             "warn")
            self.identical_traces_2.set_text(
                            "More than one instance of the same trace" \
                            " can be generated if the schema logic" \
                            " permits. If you did not intend this, look" \
                            " for redundancy in the schema logic.", "warn")

        else:
            self.identical_traces_1.set_text(
                            "\u2713  There are no identical traces", "good")
            self.identical_traces_2.set_text("", "good")

        # events
        if "missing_events" in self.warnings:
            self.missing_events_1.set_text(
                            "X  There are missing events", "error")
            self.missing_events_2.set_text(
                            "Entire branches of events may be missing." \
                            "  Inspect your schema for overloading" \
                            " constraints or forced branch rejection" \
                            " due to certain events being compulsory" \
                            " instead of optional.", "error")
        else:
            self.missing_events_1.set_text(
                            "\u2713  There are no missing events", "good")
            self.missing_events_2.set_text("", "good")

        # statistics details
        self.details_0.setPlainText(statistics_text)

    def _set_statistics_content_and_maybe_set_visible(self):
        self._set_statistics_content()
        self._maybe_set_visible()

    def _maybe_set_visible(self):
        if self.warnings and not self._ignore_model_statistics_warnings \
                         and not self.schema == "Schema not defined":
            super().show()

    @Slot()
    def _mp_code_loaded(self):
        self._ignore_model_statistics_warnings = False
        self.action_ignore_model_statistics_warnings.setChecked(False)

    @Slot(bool)
    def _set_ignore_model_statistics_warnings(self, do_ignore):
        self._ignore_model_statistics_warnings = do_ignore
        if do_ignore:
            super().hide()
        else:
            self._maybe_set_visible()

    def closeEvent(self, event):
        self.hide()

    # close button
    @Slot()
    def _close_pb_clicked(self):
        self.hide()

