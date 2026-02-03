# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import os
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QColorDialog
from PySide6.QtGui import QColor
from settings_dialog import Ui_SettingsDialog
from settings_manager import settings, save_settings, DEFAULT_SETTINGS
from paths_gryphon import DEFAULT_SETTINGS_FILENAME
from color_helper import text_color_name
from message_popup import message_popup

# background is background color, text is #ffffff in contrasting white or black
def _set_button_face(button, background_color_name):
    text_color = text_color_name(QColor(background_color_name))
    button.setStyleSheet("QPushButton {background-color: %s; color: %s;}"%(
                         background_color_name, text_color))
    button.setText(background_color_name)

class SettingsDialogWrapper(QDialog):
    def __init__(self, parent_w, settings_manager):
        super().__init__(parent_w)
        self.settings_manager = settings_manager
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        ui = self.ui
        self.setFixedSize(self.width(), self.height())

        # connect close
        ui.button_box.button(QDialogButtonBox.StandardButton.Close) \
                         .clicked.connect(self.accept)

        self._set_settings()
        self._connect_controls()

        # connect to change colors when multiple settings change
        self.settings_manager.signal_multiple_settings_changed.connect(
                                                      self._set_settings)

    def _set_settings(self):
        s = settings
        ui = self.ui
        # background
        ui.background_color_gradient_slider.setValue(
                                           s["background_color_gradient"])
        _set_button_face(ui.background_color_pb, s["background_color"])

        # generation
        ui.generation_background_use_border_cb.setChecked(
                                         s["generation_background_use_border"])
        ui.generation_traces_use_border_cb.setChecked(
                                         s["generation_traces_use_border"])
        ui.generation_graphs_use_border_cb.setChecked(
                                         s["generation_graphs_use_border"])
        ui.generation_reports_use_border_cb.setChecked(
                                         s["generation_reports_use_border"])
        ui.generation_tables_use_border_cb.setChecked(
                                         s["generation_tables_use_border"])
        ui.generation_charts_use_border_cb.setChecked(
                                         s["generation_charts_use_border"])
        ui.generation_ad_use_border_cb.setChecked(
                                         s["generation_ad_use_border"])

        # traces
        ui.trace_hide_collapse_opacity_slider.setValue(
                                           s["trace_hide_collapse_opacity"])
        ui.trace_node_width_slider.setValue(s["trace_node_width"])
        ui.trace_node_height_slider.setValue(s["trace_node_height"])
        ui.trace_node_h_spacing_slider.setValue(s["trace_node_h_spacing"])
        ui.trace_node_v_spacing_slider.setValue(s["trace_node_v_spacing"])
        ui.trace_node_use_border_cb.setChecked(s["trace_node_use_border"])
        ui.trace_node_use_shadow_cb.setChecked(s["trace_node_use_shadow"])
        _set_button_face(ui.trace_node_root_color_pb,
                                           s["trace_node_root_color"])
        _set_button_face(ui.trace_node_atomic_color_pb,
                                           s["trace_node_atomic_color"])
        _set_button_face(ui.trace_node_composite_color_pb,
                                           s["trace_node_composite_color"])
        _set_button_face(ui.trace_node_schema_color_pb,
                                           s["trace_node_schema_color"])
        _set_button_face(ui.trace_node_say_color_pb,
                                           s["trace_node_say_color"])
        ui.trace_node_color_gradient_slider.setValue(
                                           s["trace_node_color_gradient"])
        ui.trace_edge_arrow_size_slider.setValue(s["trace_edge_arrow_size"])
        _set_button_face(ui.trace_edge_in_color_pb, s["trace_edge_in_color"])
        _set_button_face(ui.trace_edge_follows_color_pb,
                                           s["trace_edge_follows_color"])
        _set_button_face(ui.trace_edge_user_defined_color_pb,
                                           s["trace_edge_user_defined_color"])

        # graphs
        ui.graph_node_width_slider.setValue(s["graph_node_width"])
        ui.graph_node_height_slider.setValue(s["graph_node_height"])
        ui.graph_node_h_spacing_slider.setValue(s["graph_node_h_spacing"])
        ui.graph_node_v_spacing_slider.setValue(s["graph_node_v_spacing"])
        ui.graph_node_corner_rounding_slider.setValue(
                                           s["graph_node_corner_rounding"])
        ui.graph_node_use_border_cb.setChecked(s["graph_node_use_border"])
        _set_button_face(ui.graph_node_color_pb, s["graph_node_color"])
        ui.graph_node_color_gradient_slider.setValue(
                                           s["graph_node_color_gradient"])
        ui.graph_edge_arrow_size_slider.setValue(s["graph_edge_arrow_size"])
        _set_button_face(ui.graph_edge_color_pb, s["graph_edge_color"])

        # code editor
        _set_button_face(ui.code_editor_keyword_color_pb,
                                           s["code_editor_keyword_color"])
        _set_button_face(ui.code_editor_meta_symbol_color_pb,
                                           s["code_editor_meta_symbol_color"])
        _set_button_face(ui.code_editor_schema_color_pb,
                                           s["code_editor_schema_color"])
        _set_button_face(ui.code_editor_root_color_pb,
                                           s["code_editor_root_color"])
        _set_button_face(ui.code_editor_atomic_color_pb,
                                           s["code_editor_atomic_color"])
        _set_button_face(ui.code_editor_composite_color_pb,
                                           s["code_editor_composite_color"])
        _set_button_face(ui.code_editor_comment_color_pb,
                                           s["code_editor_comment_color"])
        _set_button_face(ui.code_editor_quoted_text_color_pb,
                                           s["code_editor_quoted_text_color"])
        _set_button_face(ui.code_editor_variable_color_pb,
                                           s["code_editor_variable_color"])
        _set_button_face(ui.code_editor_number_color_pb,
                                           s["code_editor_number_color"])
        _set_button_face(ui.code_editor_operator_color_pb,
                                           s["code_editor_operator_color"])

        # reports, tables
        pass

        # bar charts
        ui.bar_chart_bar_length_slider.setValue(s["bar_chart_bar_length"])
        ui.bar_chart_bar_thickness_slider.setValue(s["bar_chart_bar_thickness"])
        ui.bar_chart_bar_gap_slider.setValue(s["bar_chart_bar_gap"])
        ui.bar_chart_bar_use_border_cb.setChecked(s["bar_chart_bar_use_border"])
        _set_button_face(ui.bar_chart_bar_color1_pb, s["bar_chart_bar_color1"])
        _set_button_face(ui.bar_chart_bar_color2_pb, s["bar_chart_bar_color2"])
        _set_button_face(ui.bar_chart_bar_color3_pb, s["bar_chart_bar_color3"])
        _set_button_face(ui.bar_chart_bar_color4_pb, s["bar_chart_bar_color4"])
        _set_button_face(ui.bar_chart_bar_color5_pb, s["bar_chart_bar_color5"])
        _set_button_face(ui.bar_chart_bar_color6_pb, s["bar_chart_bar_color6"])
        _set_button_face(ui.bar_chart_bar_color7_pb, s["bar_chart_bar_color7"])
        _set_button_face(ui.bar_chart_bar_color8_pb, s["bar_chart_bar_color8"])

        # activity diagrams
        ui.ad_h_spacing_slider.setValue(s["ad_h_spacing"])
        ui.ad_v_spacing_slider.setValue(s["ad_v_spacing"])
        ui.ad_action_width_slider.setValue(s["ad_action_width"])
        ui.ad_action_height_slider.setValue(s["ad_action_height"])
        ui.ad_action_corner_rounding_slider.setValue(
                                           s["ad_action_corner_rounding"])
        _set_button_face(ui.ad_action_color_pb, s["ad_action_color"])
        ui.ad_action_color_gradient_slider.setValue(
                                           s["ad_action_color_gradient"])
        ui.ad_action_use_border_cb.setChecked(s["ad_action_use_border"])
        ui.ad_edge_arrow_size_slider.setValue(s["ad_edge_arrow_size"])
        _set_button_face(ui.ad_edge_color_pb, s["ad_edge_color"])
        ui.ad_start_size_slider.setValue(s["ad_start_size"])
        _set_button_face(ui.ad_start_color_pb, s["ad_start_color"])
        ui.ad_start_use_border_cb.setChecked(s["ad_start_use_border"])
        ui.ad_end_size_slider.setValue(s["ad_end_size"])
        _set_button_face(ui.ad_end_color_pb, s["ad_end_color"])
        ui.ad_end_use_border_cb.setChecked(s["ad_end_use_border"])
        ui.ad_decision_width_slider.setValue(s["ad_decision_width"])
        ui.ad_decision_height_slider.setValue(s["ad_decision_height"])
        _set_button_face(ui.ad_decision_color_pb, s["ad_decision_color"])
        ui.ad_decision_use_border_cb.setChecked(s["ad_decision_use_border"])
        ui.ad_bar_width_slider.setValue(s["ad_bar_width"])
        ui.ad_bar_height_slider.setValue(s["ad_bar_height"])
        _set_button_face(ui.ad_bar_color_pb, s["ad_bar_color"])
        ui.ad_bar_use_border_cb.setChecked(s["ad_bar_use_border"])

    def _connect_color_pb(self, pb, color_key):
        @Slot()
        def pb_action_function():
            color = QColorDialog.getColor(
                           QColor(settings[color_key]),
                           self,
                           "Select color for %s"%color_key,
                           QColorDialog.ColorDialogOption.DontUseNativeDialog)
            if color.isValid():
                color_value = color.name()
                self.settings_manager.change_one_setting(color_key, color_value)
                _set_button_face(pb, color_value)
        pb.pressed.connect(pb_action_function)

    def _connect_cb(self, cb, cb_key):
        @Slot(bool)
        def cb_action_function(is_checked):
            self.settings_manager.change_one_setting(cb_key, bool(is_checked))
        cb.stateChanged.connect(cb_action_function)

    def _connect_slider(self, slider, slider_key):
        @Slot(int)
        def slider_action_function(slider_value):
            self.settings_manager.change_one_setting(slider_key, slider_value)
        slider.valueChanged.connect(slider_action_function)

    def _connect_controls(self):
        ui = self.ui

        # background
        self._connect_slider(ui.background_color_gradient_slider,
                                                "background_color_gradient")
        self._connect_color_pb(ui.background_color_pb, "background_color")

        # generation
        self._connect_cb(ui.generation_background_use_border_cb,
                                          "generation_background_use_border")
        self._connect_cb(ui.generation_traces_use_border_cb,
                                          "generation_traces_use_border")
        self._connect_cb(ui.generation_graphs_use_border_cb,
                                          "generation_graphs_use_border")
        self._connect_cb(ui.generation_reports_use_border_cb,
                                          "generation_reports_use_border")
        self._connect_cb(ui.generation_tables_use_border_cb,
                                          "generation_tables_use_border")
        self._connect_cb(ui.generation_charts_use_border_cb,
                                          "generation_charts_use_border")
        self._connect_cb(ui.generation_ad_use_border_cb,
                                          "generation_ad_use_border")

        # traces
        self._connect_slider(ui.trace_hide_collapse_opacity_slider,
                                           "trace_hide_collapse_opacity")
        self._connect_slider(ui.trace_node_width_slider, "trace_node_width")
        self._connect_slider(ui.trace_node_height_slider, "trace_node_height")
        self._connect_slider(ui.trace_node_h_spacing_slider,
                                                "trace_node_h_spacing")
        self._connect_slider(ui.trace_node_v_spacing_slider,
                                                "trace_node_v_spacing")
        self._connect_cb(ui.trace_node_use_border_cb, "trace_node_use_border")
        self._connect_cb(ui.trace_node_use_shadow_cb, "trace_node_use_shadow")
        self._connect_color_pb(ui.trace_node_root_color_pb,
                                            "trace_node_root_color")
        self._connect_color_pb(ui.trace_node_atomic_color_pb,
                                            "trace_node_atomic_color")
        self._connect_color_pb(ui.trace_node_composite_color_pb,
                                            "trace_node_composite_color")
        self._connect_color_pb(ui.trace_node_schema_color_pb,
                                            "trace_node_schema_color")
        self._connect_color_pb(ui.trace_node_say_color_pb,
                                            "trace_node_say_color")
        self._connect_slider(ui.trace_node_color_gradient_slider,
                                            "trace_node_color_gradient")
        self._connect_slider(ui.trace_edge_arrow_size_slider,
                                            "trace_edge_arrow_size")
        self._connect_color_pb(ui.trace_edge_in_color_pb, "trace_edge_in_color")
        self._connect_color_pb(ui.trace_edge_follows_color_pb,
                                            "trace_edge_follows_color")
        self._connect_color_pb(ui.trace_edge_user_defined_color_pb,
                                            "trace_edge_user_defined_color")

        # graphs
        self._connect_slider(ui.graph_node_width_slider, "graph_node_width")
        self._connect_slider(ui.graph_node_height_slider, "graph_node_height")
        self._connect_slider(ui.graph_node_h_spacing_slider,
                                                "graph_node_h_spacing")
        self._connect_slider(ui.graph_node_v_spacing_slider,
                                                "graph_node_v_spacing")
        self._connect_slider(ui.graph_node_corner_rounding_slider,
                                                "graph_node_corner_rounding")
        self._connect_cb(ui.graph_node_use_border_cb, "graph_node_use_border")
        self._connect_color_pb(ui.graph_node_color_pb, "graph_node_color")
        self._connect_slider(ui.graph_node_color_gradient_slider,
                                            "graph_node_color_gradient")
        self._connect_slider(ui.graph_edge_arrow_size_slider,
                                            "graph_edge_arrow_size")
        self._connect_color_pb(ui.graph_edge_color_pb, "graph_edge_color")

        # code editor
        self._connect_color_pb(ui.code_editor_keyword_color_pb,
                                            "code_editor_keyword_color")
        self._connect_color_pb(ui.code_editor_meta_symbol_color_pb,
                                            "code_editor_meta_symbol_color")
        self._connect_color_pb(ui.code_editor_schema_color_pb,
                                            "code_editor_schema_color")
        self._connect_color_pb(ui.code_editor_root_color_pb,
                                            "code_editor_root_color")
        self._connect_color_pb(ui.code_editor_atomic_color_pb,
                                            "code_editor_atomic_color")
        self._connect_color_pb(ui.code_editor_composite_color_pb,
                                            "code_editor_composite_color")
        self._connect_color_pb(ui.code_editor_comment_color_pb,
                                            "code_editor_comment_color")
        self._connect_color_pb(ui.code_editor_quoted_text_color_pb,
                                            "code_editor_quoted_text_color")
        self._connect_color_pb(ui.code_editor_variable_color_pb,
                                            "code_editor_variable_color")
        self._connect_color_pb(ui.code_editor_number_color_pb,
                                            "code_editor_number_color")
        self._connect_color_pb(ui.code_editor_operator_color_pb,
                                            "code_editor_operator_color")

        # reports, tables
        pass

        # bar charts
        self._connect_slider(ui.bar_chart_bar_length_slider,
                                            "bar_chart_bar_length")
        self._connect_slider(ui.bar_chart_bar_thickness_slider,
                                            "bar_chart_bar_thickness")
        self._connect_slider(ui.bar_chart_bar_gap_slider,
                                            "bar_chart_bar_gap")
        self._connect_cb(ui.bar_chart_bar_use_border_cb,
                                            "bar_chart_bar_use_border")
        self._connect_color_pb(ui.bar_chart_bar_color1_pb,
                                            "bar_chart_bar_color1")
        self._connect_color_pb(ui.bar_chart_bar_color2_pb,
                                            "bar_chart_bar_color2")
        self._connect_color_pb(ui.bar_chart_bar_color3_pb,
                                            "bar_chart_bar_color3")
        self._connect_color_pb(ui.bar_chart_bar_color4_pb,
                                            "bar_chart_bar_color4")
        self._connect_color_pb(ui.bar_chart_bar_color5_pb,
                                            "bar_chart_bar_color5")
        self._connect_color_pb(ui.bar_chart_bar_color6_pb,
                                            "bar_chart_bar_color6")
        self._connect_color_pb(ui.bar_chart_bar_color7_pb,
                                            "bar_chart_bar_color7")
        self._connect_color_pb(ui.bar_chart_bar_color8_pb,
                                            "bar_chart_bar_color8")

        # activity diagrams
        self._connect_slider(ui.ad_h_spacing_slider, "ad_h_spacing")
        self._connect_slider(ui.ad_v_spacing_slider, "ad_v_spacing")
        self._connect_slider(ui.ad_action_width_slider, "ad_action_width")
        self._connect_slider(ui.ad_action_height_slider, "ad_action_height")
        self._connect_slider(ui.ad_action_corner_rounding_slider,
                                            "ad_action_corner_rounding")
        self._connect_color_pb(ui.ad_action_color_pb, "ad_action_color")
        self._connect_slider(ui.ad_action_color_gradient_slider,
                                            "ad_action_color_gradient")
        self._connect_cb(ui.ad_action_use_border_cb, "ad_action_use_border")
        self._connect_slider(ui.ad_edge_arrow_size_slider, "ad_edge_arrow_size")
        self._connect_color_pb(ui.ad_edge_color_pb, "ad_edge_color")
        self._connect_slider(ui.ad_start_size_slider, "ad_start_size")
        self._connect_color_pb(ui.ad_start_color_pb, "ad_start_color")
        self._connect_cb(ui.ad_start_use_border_cb, "ad_start_use_border")
        self._connect_slider(ui.ad_end_size_slider, "ad_end_size")
        self._connect_color_pb(ui.ad_end_color_pb, "ad_end_color")
        self._connect_cb(ui.ad_end_use_border_cb, "ad_end_use_border")
        self._connect_slider(ui.ad_decision_width_slider, "ad_decision_width")
        self._connect_slider(ui.ad_decision_height_slider, "ad_decision_height")
        self._connect_cb(ui.ad_decision_use_border_cb, "ad_decision_use_border")
        self._connect_color_pb(ui.ad_decision_color_pb, "ad_decision_color")
        self._connect_slider(ui.ad_bar_width_slider, "ad_bar_width")
        self._connect_slider(ui.ad_bar_height_slider, "ad_bar_height")
        self._connect_color_pb(ui.ad_bar_color_pb, "ad_bar_color")
        self._connect_cb(ui.ad_bar_use_border_cb, "ad_bar_use_border")

