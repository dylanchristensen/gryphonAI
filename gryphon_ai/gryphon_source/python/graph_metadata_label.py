from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel

class GraphMetadataLabel(QObject):
    """Provides the active scope and MP Code schema name in a QLabel."""

    def __init__(self, graphs_manager):
        super(GraphMetadataLabel, self).__init__()

        self.graphs_manager = graphs_manager

        # connect
        graphs_manager.signal_graphs_loaded.connect(self._set_graph_metadata)

        # the status text
        self.status_text = QLabel()

    @Slot(list, str, int)
    def _set_graph_metadata(self, _graphs, schema_name, scope):
        self.status_text.setText("%s   Scope %d"%(schema_name, scope))

