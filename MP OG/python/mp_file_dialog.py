from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
'''
The QFileDialog "convenience" functions do not allow control over window
attributes so we do this by hand.  Otherwise, the file dialog will have
modal focus but will be hidden behind other windows, which appears as a hang.
'''

def get_open_filename(parent, caption, directory, filter_text):
    file_dialog = QFileDialog(parent, caption, directory, filter_text)
    file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    file_dialog.setWindowFlags(file_dialog.windowFlags() | Qt.Tool)
    file_dialog.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    if file_dialog.exec():
        return file_dialog.selectedFiles()[0]
    else:
        return ""

def get_save_filename(parent, caption, directory, filter_text):
    file_dialog = QFileDialog(parent, caption, directory, filter_text)
    file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    file_dialog.setWindowFlags(file_dialog.windowFlags() | Qt.Tool)
    file_dialog.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
    file_dialog.setFileMode(QFileDialog.AnyFile)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    if file_dialog.exec():
        return file_dialog.selectedFiles()[0]
    else:
        return ""

def get_existing_directory(parent, caption, directory):
    file_dialog = QFileDialog(parent, caption, directory)
    file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    file_dialog.setWindowFlags(file_dialog.windowFlags() | Qt.Tool)
    file_dialog.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
    file_dialog.setFileMode(QFileDialog.Directory)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    if file_dialog.exec():
        return file_dialog.selectedFiles()[0]
    else:
        return ""

