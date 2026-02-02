# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from os import remove
from os.path import join, basename
from glob import glob
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal, Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, \
                           QSortFilterProxyModel
from PySide6.QtGui import QTextDocument, QTextCursor
from PySide6.QtWidgets import QDialog, QComboBox, QAbstractItemView
from find_and_replace_dialog import Ui_FindAndReplaceDialog
from paths_gryphon import SNAPSHOTS_PATH

class FindAndReplaceDialogWrapper(QDialog):
    """
    Signals:
      signal_find_and_replace_dialog_showing()
    """

    # use this to signal when the find and replace dialog has opened
    signal_find_and_replace_dialog_showing = Signal(
                            name='signalFindAndReplaceDialogShowing')

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
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.ui.find_cb.setEditable(True)
        self.ui.find_cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # connect find input to the _next_clicked function
        self.ui.find_cb.set_enter_listener_function(self._next_clicked)

        # connect to know view change
        mp_code_view.cursorPositionChanged.connect(self._maybe_set_ui_state)
        mp_code_view.textChanged.connect(self._maybe_set_ui_state)

        # connect to know UI change
        self.ui.find_cb.currentTextChanged.connect(
                                         self._set_ui_state_ui_text_changed)
        self.ui.replace_with_le.textEdited.connect(
                                         self._set_ui_state_ui_text_changed)
        self.ui.replace_pb.clicked.connect(self._replace_clicked)
        self.ui.previous_tb.clicked.connect(self._previous_clicked)
        self.ui.next_tb.clicked.connect(self._next_clicked)
        self.ui.close_pb.clicked.connect(self._close_clicked)

    def closeEvent(self, event):
        self._close_clicked()

    # refresh word list on show
    @Slot()
    def show(self):

        # check
        if FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible:
            raise RuntimeError("bad")

        # list of words in document
        self.ui.find_cb.clear()
        self.ui.find_cb.addItems(self.mp_code_view.word_list())

        # suggest to find word at selected text
        self.ui.find_cb.setEditText(
                            self.mp_code_view.textCursor().selectedText())

        # suggest blank replacement text
        self.ui.replace_with_le.setText("")

        self._set_ui_state()

        # show 
        super(FindAndReplaceDialogWrapper, self).show()
        FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible = True

        # signal that this dialog is now showing
        self.signal_find_and_replace_dialog_showing.emit()

    def _text_is_at_cursor(self, text_to_find):
        if not text_to_find:
            return False
        cursor = self.mp_code_view.textCursor()
        cursor.setPosition(cursor.selectionStart(), mode=QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
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
        has_match_backward = text_to_find and self.document.find(text_to_find,
                     cursor, QTextDocument.FindBackward) != QTextCursor()
        self.ui.previous_tb.setDisabled(not self._has_match())

        # next button
        cursor = self.mp_code_view.textCursor()
        has_match_forward = text_to_find and self.document.find(text_to_find,
                                                              cursor)
        self.ui.next_tb.setDisabled(not self._has_match())

    def _has_match(self):
        text_to_find = self.ui.find_cb.currentText()
        next_cursor = self.mp_code_view.mp_code_manager.document.find(
                                         text_to_find)
        return bool(next_cursor)

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
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                            n=len(text_to_find))
        replacement_text = self.ui.replace_with_le.text()
        # replace policy: https://doc.qt.io/qt-5/qtextcursor.html insertText
        cursor.insertText(replacement_text)

    # previous
    @Slot()
    def _previous_clicked(self):
        text_to_find = self.ui.find_cb.currentText()
        success = self.mp_code_view.find(text_to_find,
                                         QTextDocument.FindBackward)
        if not success:

            # maybe start over from the end
            cursor = QTextCursor(self.mp_code_view.mp_code_manager.document)
            cursor.movePosition(QTextCursor.End)
            previous_cursor = self.mp_code_view.mp_code_manager.document.find(
                          text_to_find, cursor, QTextDocument.FindBackward)

            if previous_cursor:
                self.mp_code_view.setTextCursor(previous_cursor)
            else:
                print("Error in find_and_replace previous: "
                      " '%s' not found"%text_to_find)

    # next
    @Slot()
    def _next_clicked(self):
        text_to_find = self.ui.find_cb.currentText()
        success = self.mp_code_view.find(text_to_find)
        if not success:

            # maybe start over from the beginning
            next_cursor = self.mp_code_view.mp_code_manager.document.find(
                                                              text_to_find)
            if next_cursor:
                self.mp_code_view.setTextCursor(next_cursor)
            else:
                print("Error in find_and_replace next: "
                      " '%s' not found"%text_to_find)

    # close
    @Slot()
    def _close_clicked(self):
        FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible = False
        self.ui.find_cb.clearEditText()
        self.hide()

