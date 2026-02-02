# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from pathlib import Path
from time import localtime, strftime
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QDialog, QComboBox, QAbstractItemView
from PySide6.QtWidgets import QTableView
from search_mp_files_dialog import Ui_SearchMPFilesDialog
from paths_examples import examples_paths
from preferences import preferences
from message_popup import message_popup
from search_mp_code_dialog_wrapper import SearchMPCodeDialogWrapper
from mp_json_io_manager import read_mp_code_file
from mp_file_dialog import get_existing_directory
from verbose import verbose
from mp_logger import log

class FileMetadata():
    """Properties:
       posix_path
       filename - full user path or suffix for preloaded models and snippets
       group - file source group, e.g. Preloaded snippets
       lowercase_text - the file's text

    example posix_path.stat():
        st_mode=33204, st_ino=4198112, st_dev=2051, st_nlink=1,
        st_uid=1000, st_gid=1000, st_size=59587, st_atime=1625766645,
        st_mtime=1612823990, st_ctime=1612823990

    Note: we compare the lefthand part of paths using text from as_posix
    because the prefix and suffix can contain any number of subdirectories.
    """

    columns = ["Group", "Filename", "File size", "File created",
               "File modified"]

    def __init__(self, posix_path):
        # set group and filename
        self.posix_path = posix_path
        posix_text_path = posix_path.as_posix()
        models_text_path = Path(examples_paths["models"]).as_posix()
        snippets_text_path = Path(examples_paths["snippets"]).as_posix()
        personal_collection_text_path = Path(preferences[
                             "preferred_personal_collection_dir"]).as_posix()
        if posix_text_path.startswith(models_text_path):
            self.group = "Preloaded models"
            self.filename = posix_text_path[len(models_text_path)+1:]
        elif posix_text_path.startswith(snippets_text_path):
            self.group = "Preloaded snippets"
            self.filename = posix_text_path[len(snippets_text_path)+1:]
        elif posix_text_path.startswith(personal_collection_text_path):
            self.group = "Personal collection"
            self.filename = posix_text_path[
                                   len(personal_collection_text_path)+1:]
        else:
            print("Unrecognized prefix in file '%s'"%posix_text_path)
            print("Expected one of: '%s', '%s', or '%s'"
                  %(personal_collection_text_path, models_text_path,
                                                      snippets_text_path))
            self.group = "Personal collection"
            self.filename = posix_text_path

        # set lowercase text
        self.lowercase_text = open(posix_path,
                                   encoding='utf-8-sig').read().lower()

    def data(self, column):
        if column == 0:
            return self.group
        elif column == 1:
            return self.filename
        elif column == 2:
            try:
                return self.posix_path.stat().st_size
            except Exception as e:
                return str(e)
        elif column == 3:
            try:
                return strftime('%Y/%m/%d %H:%M:%S', localtime(
                                          self.posix_path.stat().st_ctime))
            except Exception as e:
                return str(e)
        elif column == 4:
            try:
                return strftime('%Y/%m/%d %H:%M:%S', localtime(
                                          self.posix_path.stat().st_mtime))
            except Exception as e:
                return str(e)

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

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self.file_metadata_list)

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
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
        self.file_contains = ""

    def set_file_filter(self, search_models, search_snippets, search_collection,
                        filename_contains, file_contains):
        self.search_models = search_models 
        self.search_snippets = search_snippets 
        self.search_collection = search_collection 
        self.filename_contains = filename_contains
        self.file_contains = file_contains
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
        if not self.file_contains in file_metadata.lowercase_text:
            return False
        return True

class FileMetadataTableView(QTableView):
    def __init__(self, parent, wrapper):
        super().__init__(parent)
        self.wrapper = wrapper
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.setWordWrap(False)

    @Slot(QModelIndex, QModelIndex)
    def currentChanged(self, model_index, _previous_model_index):
        row = self.wrapper.proxy_model.mapToSource(model_index).row()
        self.wrapper.select_row(model_index)


def _append_library(library_path, file_metadata_list):
    p = Path(library_path)
    posix_paths = sorted(p.rglob("*.mp"), key=lambda x: x.name.casefold())
    if verbose():
        print("Reading library %s count %d"%(library_path, len(posix_paths)))
    for posix_path in posix_paths:
        if posix_path.is_file():
            file_metadata_list.append(FileMetadata(posix_path))

class SearchMPFilesDialogWrapper(QDialog):

    def __init__(self, parent_window,
                 signal_preferences_changed, signal_settings_changed,
                 signal_spellcheck_changed,
                 open_mp_code_function):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.signal_preferences_changed = signal_preferences_changed
        self.signal_settings_changed = signal_settings_changed
        self.signal_spellcheck_changed = signal_spellcheck_changed
        self.open_mp_code_function = open_mp_code_function
        self.ui = Ui_SearchMPFilesDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.selected_posix_path = None
        self.set_disabled_buttons(True)

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
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 350)
        self.table_view.setColumnWidth(2, 70)
        self.table_view.setColumnWidth(3, 150)
        self.table_view.setColumnWidth(4, 150)

        # the personal collection path initial value
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

        # connect buttons
        self.ui.view_pb.clicked.connect(self._view_clicked)
        self.ui.copy_pb.clicked.connect(self._copy_clicked)
        self.ui.replace_pb.clicked.connect(self._replace_clicked)
        self.ui.close_pb.clicked.connect(self._close_clicked)

        # activation action
        self.action_search_mp_files = QAction(
                  QIcon(":/icons/search_mp_files"), "&Search .mp files...")
        self.action_search_mp_files.setToolTip("Search for text in .mp files")
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

    def set_disabled_buttons(self, is_disabled):
        self.ui.view_pb.setDisabled(is_disabled)
        self.ui.copy_pb.setDisabled(is_disabled)
        self.ui.replace_pb.setDisabled(is_disabled)

    def select_row(self, model_index):
        row = self.proxy_model.mapToSource(model_index).row()
        if row == -1:
            self.selected_posix_path = ""
            self.set_disabled_buttons(True)
        else:
            self.selected_posix_path = self.file_metadata_table_model \
                                       .file_metadata_list[row].posix_path
            self.set_disabled_buttons(False)

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
        file_contains = self.ui.file_contains_le.text().lower()
        self.proxy_model.set_file_filter(search_preloaded_models,
                                         search_preloaded_snippets,
                                         search_personal_collection,
                                         filename_contains, 
                                         file_contains)

    @Slot()
    def _set_personal_collection_path(self):
        filename = get_existing_directory(self,
                      "Personal collection path",
                      preferences["preferred_personal_collection_dir"])

        if filename:
            preferences["preferred_personal_collection_dir"] = filename
            self.ui.personal_collection_path_le.setText(filename)
            self._load_table()

    # view file in new window
    @Slot()
    def _view_clicked(self):

        # the text
        status, mp_code_text = read_mp_code_file(self.selected_posix_path)
        if status:
            message_popup(self, status)
        else:
            wrapper = SearchMPCodeDialogWrapper(self.parent_window,
                                                self.signal_preferences_changed,
                                                self.signal_settings_changed,
                                                self.signal_spellcheck_changed,
                                                self.selected_posix_path,
                                                mp_code_text)
            wrapper.show()

    # copy file to clipboard
    @Slot()
    def _copy_clicked(self):

        # the text
        status, mp_code_text = read_mp_code_file(self.selected_posix_path)
        if status:
            message_popup(self, status)
        else:
            # copy to clipboard
            clipboard = QClipboard()
            clipboard.setText(mp_code_text)
            log('File "%s" copied to system clipboard'%self.selected_posix_path)

    # replace file
    @Slot()
    def _replace_clicked(self):
        self.open_mp_code_function(self.selected_posix_path)

    # close
    @Slot()
    def _close_clicked(self):
        self.hide()

