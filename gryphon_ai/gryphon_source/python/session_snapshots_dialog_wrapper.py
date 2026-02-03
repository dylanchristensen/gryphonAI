# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from os import remove
from os.path import join, basename
from glob import glob
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtWidgets import QDialog, QAbstractItemView
from session_snapshots_dialog import Ui_SessionSnapshotsDialog
from paths_gryphon import SNAPSHOTS_PATH
from message_popup import message_popup

class SnapshotsTableModel(QAbstractTableModel):

    def __init__(self):
        super(SnapshotsTableModel, self).__init__()
        self.column_titles = ["Schema", "Timestamp"]
        self.sessions = sorted([basename(path) for path in 
                                glob("%s/*.gry"%SNAPSHOTS_PATH)])

    def headerData(self, section, orientation,
                                         role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return self.column_titles[section]
        else:
            return None # QVariant()

    def rowCount(self, parent=QModelIndex()):
        return len(self.sessions)

    def columnCount(self, parent=QModelIndex()):
        return len(self.column_titles)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()

            if column == 0:
                return self.sessions[row][:-24]
            if column == 1:
                raw_timestamp = self.sessions[row][-23:-4]
                return raw_timestamp.replace('_',':')
            raise RuntimeError("bad")
        else:
            return None # QVariant()

    def removeRows(self, row, count, parent=QModelIndex()):
        files = self.sessions[row:row+count]
        try:
            for filename in files:
                absolute_filename = join(SNAPSHOTS_PATH, filename)
                remove(absolute_filename)
        except Exception as e:
            message_popup(None, "Failure deleting session snapshots "
                                "at file %s: %s"%(absolute_filename, str(e)))
        self.beginRemoveRows(parent, row, count)
        del self.sessions[row:row+count]
        self.endRemoveRows()

class SessionSnapshotsDialogWrapper(QDialog):

    def __init__(self, gui_manager):
        super(SessionSnapshotsDialogWrapper, self).__init__(gui_manager.w)
        self.gui_manager = gui_manager
        self.ui = Ui_SessionSnapshotsDialog()
        self.ui.setupUi(self) # we refine this further below
        self.setFixedSize(self.width(), self.height())

        self.snapshots_table_model = SnapshotsTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.snapshots_table_model)

        table_view = self.ui.snapshots_table_view
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(
                         QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setSelectionMode(
                         QAbstractItemView.SelectionMode.SingleSelection)
        table_view.setModel(self.proxy_model)
        table_view.setColumnWidth(0, table_view.width()-5-175)
        table_view.setColumnWidth(1, 175)
        table_view.activated.connect(self._open_snapshot_file)
        self.table_view = table_view

        # connect the buttons
        self.ui.open_pb.clicked.connect(self._open_snapshot_file)
        self.ui.delete_pb.clicked.connect(self._delete_pb_clicked)
        self.ui.delete_all_pb.clicked.connect(self._delete_all_pb_clicked)
        self.ui.close_pb.clicked.connect(self._close_pb_clicked)

    # get index and filename else -1 and ""
    def _current_selection(self):
        proxy_model_index = self.table_view.currentIndex()
        model_index = self.proxy_model.mapToSource(proxy_model_index).row()
        if model_index == -1:
            return model_index, ""
        else:
            return model_index, self.snapshots_table_model.sessions[model_index]

    # open the selected file
    @Slot()
    def _open_snapshot_file(self):
        model_index, filename = self._current_selection()
        if model_index == -1:
            message_popup(self.gui_manager.w, "Snapshot file not selected")
        else:
            absolute_filename = join(SNAPSHOTS_PATH, filename)
            self.gui_manager.gry_manager.import_gry_file(absolute_filename)
            self.hide()

    # delete
    @Slot()
    def _delete_pb_clicked(self):
        model_index, filename = self._current_selection()
        if model_index == -1:
            message_popup(self.gui_manager.w, "Snapshot file not selected")
        else:
            self.snapshots_table_model.removeRows(model_index, 1)
        self.proxy_model.invalidate()

    # delete all
    @Slot()
    def _delete_all_pb_clicked(self):
        if not self.snapshots_table_model.rowCount():
            message_popup(self.gui_manager.w,
                          "There are no snapshot files to delete")
        self.snapshots_table_model.removeRows(0,
                                   self.snapshots_table_model.rowCount())
        self.proxy_model.invalidate()

    # close
    @Slot()
    def _close_pb_clicked(self):
        self.hide()

