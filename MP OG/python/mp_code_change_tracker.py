from PySide6.QtWidgets import QMessageBox
from preferences import preferences
from mp_code_filename import active_mp_code_filename

class MPCodeChangeTracker():
    """Track mp code changes to allow asking to save when changes are made
       and attempting to close or save the existing mp code.
    """
    def __init__(self, gui_manager):
        self.gui_manager = gui_manager

    def _is_modified(self):
        return self.gui_manager.mp_code_manager.document.isModified()

    # unset the modified flag
    def unset_is_modified(self):
        self.gui_manager.mp_code_manager.document.setModified(False)

    # return "" on save or discard, return text on cancel or failed save
    def _save_discard_or_cancel(self):

        # see what the user wants: save, discard, or cancel
        filename = active_mp_code_filename()
        mb = QMessageBox(self.gui_manager.w)
        mb.setWindowTitle("Question")
        mb.setText("Save changes to existing .mp code before proceeding?")
        if filename:
            mb.setInformativeText("Changes to %s will be lost if not saved."
                                  %filename)
        else:
            mb.setInformativeText(
                            "Changes to .mp code will be lost if not saved.")
        mb.setStandardButtons(QMessageBox.Save
                            | QMessageBox.Discard
                            | QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Save)
        response = mb.exec()

        if response == QMessageBox.Save:
            # save first
            # do not disturb the selected mp code directory when saving
            # previous work
            preferred_mp_code_dir = preferences["preferred_mp_code_dir"]
            status = self.gui_manager.save_mp_code_file_as()
            preferences["preferred_mp_code_dir"] = preferred_mp_code_dir
            return status
 
        if response == QMessageBox.Discard:
            # discard without saving
            return ""

        if response == QMessageBox.Cancel:
            # user requested Cancel
            return "Action cancelled"

        raise RuntimeError("bad")

    # Call this before closing .mp code or loading other .mp code to avoid
    # losing existing work.
    # returns "" on no change else return "" or message if not saved
    def maybe_save_discard_or_cancel(self):
        if self._is_modified():
            return self._save_discard_or_cancel()
        else:
            return ""
