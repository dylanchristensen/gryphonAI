from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QSpinBox

"""A slider that includes a spinner."""
class SettingsSlider(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)

        self.spinner = QSpinBox()
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)

        self.layout.addWidget(self.spinner)
        self.layout.addWidget(self.slider)

        # state
        self._ignore_change = False

    def connect_slider(self, min_val, max_val, settings_manager, setting_name,
                       tooltip):
        self._ignore_change = True
        self.spinner.setRange(min_val, max_val)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self._ignore_change = False
        self.settings_manager = settings_manager
        self.setting_name = setting_name
        self.slider.setToolTip(tooltip)
        self.spinner.valueChanged.connect(self._slider_changed)
        self.slider.valueChanged.connect(self._slider_changed)

    def set_value(self, slider_value):
        # it is unnecessary to signal value change when setting the slider
        self._ignore_change = True
        self.spinner.setValue(slider_value)
        self.slider.setValue(slider_value)
        self._ignore_change = False

    @Slot(int)
    def _slider_changed(self, slider_value):
        if self._ignore_change:
            # responding
            return
        self.set_value(slider_value)
        self.settings_manager.change_one_setting(self.setting_name,
                                                 slider_value)

