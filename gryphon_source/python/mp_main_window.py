import traceback
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot
from preferences import preferences

class MPMainWindow(QMainWindow):
    """This wrapper enables intercepting exit and asking the user if saving
        .mp is desired."""
    def __init__(self, gui_manager):
        super().__init__()
        self.gui_manager = gui_manager
        self.set_w_geometry()

    # main window position and dimensions
    def set_w_geometry(self):
        self.setGeometry(200, 100,
                         preferences["main_window_w"],
                         preferences["main_window_h"])

    def closeEvent(self, close_event):
        # check for mp code change when closing but be forgiving if
        # gui_manager is not yet fully initialized
        try:
            status = self.gui_manager.mp_code_change_tracker \
                     .maybe_save_discard_or_cancel()
        except Exception as e:
            traceback.print_exc()
            print("GUI closed before being fully initialized:", str(e))

