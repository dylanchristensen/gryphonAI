from os import scandir
from os.path import join
from time import strftime
from PySide6.QtGui import QAction
from paths_gryphon import SNAPSHOTS_PATH
from session_snapshots_dialog_wrapper import SessionSnapshotsDialogWrapper

def schema_filename(schema_name):
    # filename = <schema name>_yy_mm_dd-hh_mm_ss.gry
    current_time = strftime("%Y_%m_%d-%H_%M_%S")
    filename = join(SNAPSHOTS_PATH, "%s_%s.gry"%(schema_name, current_time))
    return filename

class SessionSnapshots():

    """Manage .gry file snapshots.
       Provides action_take_snapshot and action_manage_snapshots.
    """

    def __init__(self, gui_manager):
        self.gui_manager = gui_manager

        # action take snapshot
        self.action_take_snapshot = QAction("&Take a snapshot")
        self.action_take_snapshot.setStatusTip(
                            "Take a .gry snapshot of the current schema")
        self.action_take_snapshot.triggered.connect(
                                     self._create_snapshot)

        # action manage snapshots
        self.action_manage_snapshots = QAction("Open a snapshot...")
        self.action_manage_snapshots.setStatusTip(
                                        "Manage .gry file schema snapshots")
        self.action_manage_snapshots.triggered.connect(
                                     self._manage_snapshots)
        self.action_manage_snapshots.setDisabled(
                                         not any(scandir(SNAPSHOTS_PATH)))

    def _create_snapshot(self):
        schema_name = self.gui_manager.mp_code_manager.schema_name()
        filename = schema_filename(schema_name)
        status = self.gui_manager.gry_manager.export_gry_file(filename)
        if status:
            log(status)
        self.action_manage_snapshots.setDisabled(False)

    # save .gry for future recall
    def _manage_snapshots(self):
        if not any(scandir(SNAPSHOTS_PATH)):
            # this should be designed to never happen
            raise RuntimeError("bad")

        wrapper = SessionSnapshotsDialogWrapper(self.gui_manager)
        wrapper.exec_()
        self.action_manage_snapshots.setDisabled(
                                         not any(scandir(SNAPSHOTS_PATH)))

