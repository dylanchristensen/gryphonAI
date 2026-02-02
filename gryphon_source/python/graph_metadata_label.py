from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel
from mp_code_parser import mp_code_schema

class GraphMetadataLabel(QObject):
    """Provides the active scope and MP Code schema name in a QLabel."""

    def __init__(self, graphs_manager):
        super(GraphMetadataLabel, self).__init__()

        self.graphs_manager = graphs_manager

        # connect
        graphs_manager.signal_graphs_loaded.connect(self._set_graph_metadata)

        # the status text
        self.status_text = QLabel()

    @Slot()
    def _set_graph_metadata(self):
        if self.graphs_manager.mp_code:
            # show metadata text
            self.status_text.setText("%s   Scope %d"%(
                            mp_code_schema(self.graphs_manager.mp_code),
                            self.graphs_manager.scope))
        else:
            # no code
            self.status_text.setText("")

