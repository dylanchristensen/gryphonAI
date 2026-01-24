from PySide6.QtCore import Qt, QRect, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QSpinBox

"""A slider that includes a spinner that annotates from 0% to 100%."""
class SettingsSliderPercent(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)

        self.spinner = QSpinBox()
        self.spinner.setRange(0, 100)
        self.spinner.setSuffix('%')

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)

        self.layout.addWidget(self.spinner)
        self.layout.addWidget(self.slider)

        # state
        self._ignore_change = False

    def _setting_to_slider(self, setting):
        min_val = self.min_val
        max_val = self.max_val
        return round((setting - min_val) / (max_val - min_val) * 100)

    def _slider_to_setting(self, slider):
        min_val = self.min_val
        max_val = self.max_val
        return round(slider * (max_val - min_val) / 100) + min_val

    def connect_slider(self, min_val, max_val,
                       settings_manager, setting_name, tooltip):
        self.min_val = min_val
        self.max_val = max_val
        self.settings_manager = settings_manager
        self.setting_name = setting_name
        self.slider.setToolTip(tooltip)
        self.spinner.valueChanged.connect(self._slider_changed)
        self.slider.valueChanged.connect(self._slider_changed)

    # set the slider and spinner to the requested value
    def set_value(self, setting_value):
        slider_value = self._setting_to_slider(setting_value)
        self._quietly_set_value(slider_value)

    def _quietly_set_value(self, slider_value):
        self._ignore_change = True
        self.spinner.setValue(slider_value)
        self.slider.setValue(slider_value)
        self._ignore_change = False

    @Slot(int)
    def _slider_changed(self, slider_value):
        if self._ignore_change:
            # responding
            return

        # make the slider and spinner match the new selected value
        self._quietly_set_value(slider_value)

        # update settings
        setting_value = self._slider_to_setting(slider_value)
        self.settings_manager.change_one_setting(self.setting_name,
                                                 setting_value)

