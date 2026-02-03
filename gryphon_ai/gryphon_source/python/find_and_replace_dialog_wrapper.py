# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from os import remove
from os.path import join, basename
from glob import glob
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, \
                           QSortFilterProxyModel
from PySide6.QtGui import QTextDocument, QTextCursor
from PySide6.QtWidgets import QDialog, QComboBox, QAbstractItemView
from find_and_replace_dialog import Ui_FindAndReplaceDialog
from paths_gryphon import SNAPSHOTS_PATH
from mp_code_dynamic_tokens import dynamic_token_names

def _find_flags(is_backward, is_match_case):
    options = QTextDocument.FindFlags()
    if is_backward:
        options |= QTextDocument.FindBackward
    if is_match_case:
        options |= QTextDocument.FindCaseSensitively
    return options

class FindAndReplaceDialogWrapper(QDialog):

    # use this singleton class variable to enable action in code view menu
    a_wrapper_instance_is_visible = False

    # This dialog wrapper serves this code view.  We maybe could switch the
    # parent, which contains the common document and the maybe not common
    # cursor and event handlers, but too messy.
    def __init__(self, mp_code_view):
        super(FindAndReplaceDialogWrapper, self).__init__(mp_code_view)
        self.mp_code_view = mp_code_view
        self.document = mp_code_view.document()
        self.ui = Ui_FindAndReplaceDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Find and replace (screen %d)"
                                            %mp_code_view.instance_number)
        self.setFixedSize(self.width(), self.height())
        self.ui.find_cb.setEditable(True)
        self.ui.find_cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.ui.find_cb.completer().setCaseSensitivity(
                                        Qt.CaseSensitivity.CaseSensitive)

        # connect to know view change
        mp_code_view.cursorPositionChanged.connect(self._maybe_set_ui_state)
        mp_code_view.textChanged.connect(self._maybe_set_ui_state)

        # connect to know UI change
        self.ui.find_cb.currentTextChanged.connect(
                                         self._set_ui_state_ui_text_changed)
        self.ui.replace_with_le.textEdited.connect(
                                         self._set_ui_state_ui_text_changed)
        self.ui.match_case_cb.stateChanged.connect(
                                         self._set_ui_state)
        self.ui.replace_pb.clicked.connect(self._replace_clicked)
        self.ui.previous_pb.clicked.connect(self._previous_clicked)
        self.ui.next_pb.clicked.connect(self._next_clicked)
        self.ui.close_pb.clicked.connect(self._close_clicked)

        # start empty
        self.words = list()

    def closeEvent(self, event):
        self._close_clicked()

    # refresh token list on show
    @Slot()
    def show(self):

        # check
        if FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible:
            raise RuntimeError("bad")

        # list of words in document
        self.words = dynamic_token_names(self.document)
        self.ui.find_cb.clear()
        self.ui.find_cb.addItems(self.words)

        # suggest to find word at selected text
        self.ui.find_cb.setEditText(
                            self.mp_code_view.textCursor().selectedText())

        # suggest blank replacement text
        self.ui.replace_with_le.setText("")

        self._set_ui_state()

        # show 
        super(FindAndReplaceDialogWrapper, self).show()
        FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible = True

    def _text_is_at_cursor(self, text_to_find):
        if not text_to_find:
            return False
        cursor = self.mp_code_view.textCursor()
        cursor.setPosition(cursor.selectionStart(), mode=QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.Right, mode=QTextCursor.KeepAnchor,
                            n=len(text_to_find))
        cursor_text = cursor.selectedText()
        return text_to_find.lower() == cursor_text.lower()

    @Slot()
    def _set_ui_state(self):
        text_to_find = self.ui.find_cb.currentText()

        # replace button
        replacement_text = self.ui.replace_with_le.text()
        self.ui.replace_pb.setDisabled(not replacement_text
                              or not self._text_is_at_cursor(text_to_find))

        # previous button
        cursor = self.mp_code_view.textCursor()
        options = _find_flags(True, self.ui.match_case_cb.isChecked())
        has_match_backward = text_to_find and self.document.find(text_to_find,
                     cursor, options) != QTextCursor()
        self.ui.previous_pb.setDisabled(not has_match_backward)

        # next button
        cursor = self.mp_code_view.textCursor()
        options = _find_flags(False, self.ui.match_case_cb.isChecked())
        has_match_forward = text_to_find and self.document.find(text_to_find,
                                     cursor, options) != QTextCursor()
        self.ui.next_pb.setDisabled(not has_match_forward)

    @Slot(str)
    def _set_ui_state_ui_text_changed(self, _text):
        self._set_ui_state()

    @Slot()
    def _maybe_set_ui_state(self):
        if self.isVisible():
            self._set_ui_state()

    @Slot()
    def _replace_clicked(self):
        cursor = self.mp_code_view.textCursor()
        cursor.setPosition(cursor.selectionStart(), mode=QTextCursor.MoveAnchor)
        text_to_find = self.ui.find_cb.currentText()
        cursor.movePosition(QTextCursor.Right, mode=QTextCursor.KeepAnchor,
                            n=len(text_to_find))
        replacement_text = self.ui.replace_with_le.text()
        # replace policy: https://doc.qt.io/qt-5/qtextcursor.html insertText
        cursor.insertText(replacement_text)

    # previous
    @Slot()
    def _previous_clicked(self):
        text_to_find = self.ui.find_cb.currentText()
        options = _find_flags(True, self.ui.match_case_cb.isChecked())
        success = self.mp_code_view.find(text_to_find, options)
        if not success:
            print("Error in find_and_replace _previous_clicked")
            raise RuntimeError("bad")

    # next
    @Slot()
    def _next_clicked(self):
        text_to_find = self.ui.find_cb.currentText()
        options = _find_flags(False, self.ui.match_case_cb.isChecked())
        success = self.mp_code_view.find(text_to_find, options)
        if not success:
            print("Error in find_and_replace _next_clicked")
            raise RuntimeError("bad")


    # close
    @Slot()
    def _close_clicked(self):
        FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible = False
        self.hide()

