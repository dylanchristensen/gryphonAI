# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from pathlib import Path
from time import localtime, strftime
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QAction
from PySide6.QtGui import QTextDocument, QTextCursor, QIcon
from PySide6.QtWidgets import QDialog, QFileDialog, QComboBox, QAbstractItemView
from PySide6.QtWidgets import QTableView
from search_mp_files_dialog import Ui_SearchMPFilesDialog
from paths_examples import examples_paths
from preferences_manager import preferences
from mp_code_dynamic_tokens import dynamic_token_names
from search_mp_code_dialog_wrapper import SearchMPCodeDialogWrapper
from verbose import verbose

class FileMetadata():
    """Properties:
       posix_path
       filename - full user path or suffix for preloaded models and snippets
       group
       words<set>

    example posix_path.stat():
        st_mode=33204, st_ino=4198112, st_dev=2051, st_nlink=1,
        st_uid=1000, st_gid=1000, st_size=59587, st_atime=1625766645,
        st_mtime=1612823990, st_ctime=1612823990
    """

    columns = ["Group", "Filename", "File size", "File created",
               "File modified"]

    def __init__(self, posix_path):
        self.posix_path = posix_path
        full_path = posix_path.as_posix()
        if full_path.startswith(examples_paths["models"]):
            self.group = "Preloaded models"
            self.filename = full_path[len(examples_paths["models"])+1:]
        elif posix_path.as_posix().startswith(examples_paths["snippets"]):
            self.group = "Preloaded snippets"
            self.filename = full_path[len(examples_paths["snippets"])+1:]
        else:
            self.group = "Personal collection"
            self.filename = full_path[len(
                   preferences["preferred_personal_collection_dir"])+1:]
        self.words = set(open(posix_path).read().lower().split())

    def data(self, column):
        if column == 0:
            return self.group
        elif column == 1:
            return self.filename
        elif column == 2:
            return self.posix_path.stat().st_size
        elif column == 3:
            return strftime('%Y:%m:%d-%H:%M:%S', localtime(
                                          self.posix_path.stat().st_ctime))
        elif column == 4:
            return strftime('%Y:%m:%d-%H:%M:%S', localtime(
                                          self.posix_path.stat().st_mtime))

class FileMetadataTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        # the file metadata list
        self.file_metadata_list = list()

    def set_data(self, file_metadata_list):
        self.beginResetModel()
        self.file_metadata_list = file_metadata_list
        self.endResetModel()

    def headerData(self, section, orientation,
                                      role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return FileMetadata.columns[section]
        else:
            return None # QVariant()

    def rowCount(self, parent=QModelIndex()):
        return len(self.file_metadata_list)

    def columnCount(self, parent=QModelIndex()):
        return len(FileMetadata.columns)

    def data(self, model_index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            row = model_index.row()
            column = model_index.column()
            return self.file_metadata_list[row].data(column)
        else:
            return None # QVariant()

class FileMetadataSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model):
        super().__init__()
        self.source_model = source_model
        self.search_models = True
        self.search_snippets = True
        self.search_collection = True
        self.filename_contains = ""
        self.file_contains_set = set()

    def set_filter(self, search_models, search_snippets, search_collection,
                   filename_contains, file_contains_set):
        self.search_models = search_models 
        self.search_snippets = search_snippets 
        self.search_collection = search_collection 
        self.filename_contains = filename_contains
        self.file_contains_set = file_contains_set 
        self.invalidateFilter()

    # fully control custom filtering
    def filterAcceptsRow(self, row, source_parent):
        source_model_index0 = self.source_model.index(row, 0, source_parent)
        source_model_row = source_model_index0.row()
        file_metadata = self.source_model.file_metadata_list[source_model_row]
        if self.search_models == False \
                        and file_metadata.group == "Preloaded models":
            return False
        if self.search_snippets == False \
                        and file_metadata.group == "Preloaded snippets":
            return False
        if self.search_collection == False \
                        and file_metadata.group == "Personal collection":
            return False
        if not self.filename_contains in file_metadata.filename.lower():
            return False
        if not self.file_contains_set.issubset(file_metadata.words):
            return False
        return True

class FileMetadataTableView(QTableView):
    def __init__(self, parent, wrapper):
        super().__init__(parent)
        self.wrapper = wrapper
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.setWordWrap(False)

def _append_library(library_path, file_metadata_list):
    p = Path(library_path)
    posix_paths = sorted(p.rglob("*.mp"))
    if verbose():
        print("Reading library %s count %d"%(library_path, len(posix_paths)))
    for posix_path in posix_paths:
        if posix_path.is_file():
            file_metadata_list.append(FileMetadata(posix_path))

class SearchMPFilesDialogWrapper(QDialog):

    def __init__(self, parent, preferences_manager, settings_manager):
        super().__init__(parent)
        self.parent = parent
        self.preferences_manager = preferences_manager
        self.settings_manager = settings_manager
        self.ui = Ui_SearchMPFilesDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())

        # the file metadata data and data proxy models
        self.file_metadata_table_model = FileMetadataTableModel()
        self.proxy_model = FileMetadataSortFilterProxyModel(
                                         self.file_metadata_table_model)
        self.proxy_model.setSourceModel(self.file_metadata_table_model)

        # the file metadata table view
        _layout = self.ui.file_metadata_table_layout
        # verticalLayoutWidget is created along with file_metadata_table_layout
        self.table_view = FileMetadataTableView(
                                        self.ui.verticalLayoutWidget, self)
        _layout.addWidget(self.table_view)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(
                             QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(
                             QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.clicked.connect(self._select_index)
        self.table_view.activated.connect(self._select_index)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 350)
        self.table_view.setColumnWidth(2, 70)
        self.table_view.setColumnWidth(3, 150)
        self.table_view.setColumnWidth(4, 150)

        # the path initial value
        self.ui.personal_collection_path_le.setText(
                     preferences["preferred_personal_collection_dir"])
 
        # connect to know search filter parameters changed
        self.ui.preloaded_models_cb.clicked.connect(self._filter_table)
        self.ui.preloaded_snippets_cb.clicked.connect(self._filter_table)
        self.ui.personal_collection_cb.clicked.connect(self._filter_table)
        self.ui.collection_path_pb.clicked.connect(
                                      self._set_personal_collection_path)
        self.ui.refresh_table_pb.clicked.connect(self._load_table)
        self.ui.filename_contains_le.textEdited.connect(self._filter_table)
        self.ui.file_contains_le.textEdited.connect(self._filter_table)
        self.ui.close_pb.clicked.connect(self._close_clicked)

        # activation action
        self.action_search_mp_files = QAction(
                  QIcon(":/icons/search_mp_files"), "&Search .mp files...")
        self.action_search_mp_files.setStatusTip(
                                  "Search for words in .mp files")
        self.action_search_mp_files.triggered.connect(self.show)

        # do not populate this until required
        self.table_loaded = False

    def show(self):
        if not self.table_loaded:
            self._load_table()
            self.table_loaded = True
        super().show()

    def closeEvent(self, event):
        self._close_clicked()

    @Slot()
    def _load_table(self):
        file_metadata_list = list()
        _append_library(examples_paths["models"], file_metadata_list)
        _append_library(examples_paths["snippets"], file_metadata_list)
        _append_library(preferences["preferred_personal_collection_dir"],
                        file_metadata_list)
        self.file_metadata_table_model.set_data(file_metadata_list)

    @Slot()
    def _filter_table(self):
        search_preloaded_models = self.ui.preloaded_models_cb.isChecked()
        search_preloaded_snippets = self.ui.preloaded_snippets_cb.isChecked()
        search_personal_collection = self.ui.personal_collection_cb.isChecked()
        filename_contains = self.ui.filename_contains_le.text().lower()
        file_contains_set = set(self.ui.file_contains_le.text().lower().split())
        self.proxy_model.set_filter(search_preloaded_models,
                                    search_preloaded_snippets,
                                    search_personal_collection,
                                    filename_contains, 
                                    file_contains_set)

    @Slot()
    def _set_personal_collection_path(self):
        filename = QFileDialog.getExistingDirectory(self.parent,
                      "Personal collection path",
                      preferences["preferred_personal_collection_dir"],
                      options = QFileDialog.Option.DontUseNativeDialog \
                      | QFileDialog.Option.ShowDirsOnly)


        if filename:
            preferences["preferred_personal_collection_dir"] = filename
            self.ui.personal_collection_path_le.setText(filename)
            self._load_table()

    @Slot(QModelIndex)
    def _select_index(self, model_index):
        row = self.proxy_model.mapToSource(model_index).row()
        posix_path = self.file_metadata_table_model.file_metadata_list[row]\
                                                             .posix_path
        print("Open search", posix_path)
        wrapper = SearchMPCodeDialogWrapper(self.parent,
                                            self.preferences_manager,
                                            self.settings_manager,
                                            posix_path)
        wrapper.show()

    # close
    @Slot()
    def _close_clicked(self):
        SearchMPFilesDialogWrapper.a_wrapper_instance_is_visible = False
        self.hide()

