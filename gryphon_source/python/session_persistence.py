from os.path import exists
from PySide6.QtCore import QObject, Slot # for signal/slot support
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from paths_gryphon import PREVIOUS_SESSION_FILENAME
from mp_logger import log
from mp_json_io_manager import save_mp_code_file
_SESSION_BACKUP_PERIODICITY = 60 * 1000 # backup every 60 seconds

class SessionPersistence(QObject):

    """Enable session persistence at path PREVIOUS_SESSION_FILENAME
       Services:
         * Action for restoring previous session.
         * Save session on exit.
         * Save session at periodic intervals
    """

    def __init__(self, gui_manager):
        super().__init__()
        self.gui_manager = gui_manager

        # save session at intervals
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self.save_this_session)
        self._timer.start(_SESSION_BACKUP_PERIODICITY) # ms

        # action restore previous session
        self.action_restore_previous_session = QAction(
                                           "&Restore previous session .mp")
        self.action_restore_previous_session.setToolTip(
                         "Restore state to the previously loaded session .mp")
        self.action_restore_previous_session.triggered.connect(
                                     self._load_previous_session)
        self.action_restore_previous_session.setDisabled(not exists(
                                                PREVIOUS_SESSION_FILENAME))


    def _load_previous_session(self):
        if not exists(PREVIOUS_SESSION_FILENAME):
            # this should be designed to never happen
            raise RuntimeError("bad")

        self.gui_manager.open_mp_code(PREVIOUS_SESSION_FILENAME)

    # save .mp for future recall
    @Slot()
    def save_this_session(self):
        status = save_mp_code_file(
                               self.gui_manager.mp_code_manager.text(),
                               PREVIOUS_SESSION_FILENAME)
        if status:
            log(status)
        else:
            # enable restore even if not disabled
            self.action_restore_previous_session.setDisabled(False)

