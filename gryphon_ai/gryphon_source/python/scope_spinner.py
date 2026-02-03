from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Slot
from PySide6.QtCore import QObject

class ScopeSpinner(QObject):
    """ScopeSpinner provides spinner and scope accessors.
       Set to 1 when mp code is loaded."""

    def __init__(self, signal_mp_code_loaded):
        super().__init__()
        self.spinner = QSpinBox()
        self.spinner.setRange(1, 5)
        self.spinner.setStatusTip("Set scope for MP Code run")
        self.spinner.setToolTip("Scope")
        self.spinner.setSizePolicy(QSizePolicy.Policy.Maximum,
                                   QSizePolicy.Policy.Maximum)

        # connect
        signal_mp_code_loaded.connect(self.reset)

    def scope(self):
        return self.spinner.value()

    @Slot()
    def reset(self):
        self.spinner.setValue(1)

