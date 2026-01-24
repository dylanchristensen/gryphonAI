# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QColorDialog, \
                              QAbstractButton
from PySide6.QtGui import QColor
from settings_dialog import Ui_SettingsDialog
from settings import settings
from color_helper import contrasting_color

# background is background color, text is #ffffff in contrasting white or black
def _set_button_face(button, background_color_name):
    text_color = contrasting_color(QColor(background_color_name)).name()
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
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)

        # make tab text print in full and scroll for Mac
        self.ui.settings_widget.setElideMode(Qt.TextElideMode.ElideNone)
        self.ui.settings_widget.setUsesScrollButtons(True)

        # connect close
        ui.button_box.button(QDialogButtonBox.StandardButton.Close) \
                         .clicked.connect(self.accept)

        self._connect_controls()
        self._set_settings()

        # connect to set setting values when multiple settings change
        self.settings_manager.signal_multiple_settings_changed.connect(
                                                      self._set_settings)

    def _set_export_image_format_button(self):
        image_format = settings["export_image_format"]
        buttons = [(".bmp", self.ui.export_image_format_bmp_rb),
                   (".jpg", self.ui.export_image_format_jpg_rb),
                   (".pdf", self.ui.export_image_format_pdf_rb),
                   (".png", self.ui.export_image_format_png_rb),
                   (".svg", self.ui.export_image_format_svg_rb),
                  ]
        for pb_image_format, pb in buttons:
            if pb_image_format == image_format:
                pb.setChecked(True)
                return

        # an invalid format will leave button unchecked
        print("export_image_format '%s' not recognized" %image_format)

    def _set_settings(self):
        s = settings
        ui = self.ui

        # export
        ui.export_background_is_transparent_cb.setChecked(
                                         s["export_background_is_transparent"])
        ui.export_header_is_hidden_cb.setChecked(
                                         s["export_header_is_hidden"])
        ui.export_header_vertical_spacing_slider.set_value(
                                         s["export_header_vertical_spacing"])
        self._set_export_image_format_button()

        # background
        ui.background_color_gradient_slider.set_value(
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
        ui.trace_hide_collapse_opacity_slider.set_value(
                                           s["trace_hide_collapse_opacity"])
        ui.trace_node_width_slider.set_value(s["trace_node_width"])
        ui.trace_node_height_slider.set_value(s["trace_node_height"])
        ui.trace_node_h_spacing_slider.set_value(s["trace_node_h_spacing"])
        ui.trace_node_v_spacing_slider.set_value(s["trace_node_v_spacing"])
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
        ui.trace_node_color_gradient_slider.set_value(
                                           s["trace_node_color_gradient"])
        ui.trace_edge_arrow_size_slider.set_value(s["trace_edge_arrow_size"])
        ui.trace_edge_annotation_width_slider.set_value(
                                           s["trace_edge_annotation_width"])
        ui.trace_edge_annotation_background_opacity_slider.set_value(
                                 s["trace_edge_annotation_background_opacity"])
        _set_button_face(ui.trace_edge_in_color_pb, s["trace_edge_in_color"])
        _set_button_face(ui.trace_edge_follows_color_pb,
                                           s["trace_edge_follows_color"])
        _set_button_face(ui.trace_edge_user_defined_color_pb,
                                           s["trace_edge_user_defined_color"])

        # graphs
        ui.graph_node_width_slider.set_value(s["graph_node_width"])
        ui.graph_node_height_slider.set_value(s["graph_node_height"])
        ui.graph_node_h_spacing_slider.set_value(s["graph_node_h_spacing"])
        ui.graph_node_v_spacing_slider.set_value(s["graph_node_v_spacing"])
        ui.graph_node_corner_rounding_slider.set_value(
                                           s["graph_node_corner_rounding"])
        ui.graph_node_use_border_cb.setChecked(s["graph_node_use_border"])
        ui.graph_node_use_shadow_cb.setChecked(s["graph_node_use_shadow"])
        _set_button_face(ui.graph_node_color_pb, s["graph_node_color"])
        ui.graph_node_color_gradient_slider.set_value(
                                           s["graph_node_color_gradient"])
        ui.graph_edge_arrow_size_slider.set_value(s["graph_edge_arrow_size"])
        ui.graph_edge_annotation_width_slider.set_value(
                                           s["graph_edge_annotation_width"])
        ui.graph_edge_annotation_background_opacity_slider.set_value(
                                s["graph_edge_annotation_background_opacity"])
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
        ui.bar_chart_bar_length_slider.set_value(s["bar_chart_bar_length"])
        ui.bar_chart_bar_thickness_slider.set_value(
                                                 s["bar_chart_bar_thickness"])
        ui.bar_chart_bar_gap_slider.set_value(s["bar_chart_bar_gap"])
        ui.bar_chart_bar_use_border_cb.setChecked(s["bar_chart_bar_use_border"])
        ui.bar_chart_bar_annotation_decimal_places_slider.set_value(
                              s["bar_chart_bar_annotation_decimal_places"])
        _set_button_face(ui.bar_chart_bar_color1_pb, s["bar_chart_bar_color1"])
        _set_button_face(ui.bar_chart_bar_color2_pb, s["bar_chart_bar_color2"])
        _set_button_face(ui.bar_chart_bar_color3_pb, s["bar_chart_bar_color3"])
        _set_button_face(ui.bar_chart_bar_color4_pb, s["bar_chart_bar_color4"])
        _set_button_face(ui.bar_chart_bar_color5_pb, s["bar_chart_bar_color5"])
        _set_button_face(ui.bar_chart_bar_color6_pb, s["bar_chart_bar_color6"])
        _set_button_face(ui.bar_chart_bar_color7_pb, s["bar_chart_bar_color7"])
        _set_button_face(ui.bar_chart_bar_color8_pb, s["bar_chart_bar_color8"])

        # activity diagrams
        ui.ad_h_spacing_slider.set_value(s["ad_h_spacing"])
        ui.ad_v_spacing_slider.set_value(s["ad_v_spacing"])
        ui.ad_action_width_slider.set_value(s["ad_action_width"])
        ui.ad_action_height_slider.set_value(s["ad_action_height"])
        ui.ad_action_corner_rounding_slider.set_value(
                                           s["ad_action_corner_rounding"])
        _set_button_face(ui.ad_action_color_pb, s["ad_action_color"])
        ui.ad_action_color_gradient_slider.set_value(
                                           s["ad_action_color_gradient"])
        ui.ad_action_use_border_cb.setChecked(s["ad_action_use_border"])
        ui.ad_edge_arrow_size_slider.set_value(s["ad_edge_arrow_size"])
        _set_button_face(ui.ad_edge_color_pb, s["ad_edge_color"])
        ui.ad_start_size_slider.set_value(s["ad_start_size"])
        _set_button_face(ui.ad_start_color_pb, s["ad_start_color"])
        ui.ad_start_use_border_cb.setChecked(s["ad_start_use_border"])
        ui.ad_end_size_slider.set_value(s["ad_end_size"])
        _set_button_face(ui.ad_end_color_pb, s["ad_end_color"])
        ui.ad_end_use_border_cb.setChecked(s["ad_end_use_border"])
        ui.ad_decision_width_slider.set_value(s["ad_decision_width"])
        ui.ad_decision_height_slider.set_value(s["ad_decision_height"])
        _set_button_face(ui.ad_decision_color_pb, s["ad_decision_color"])
        ui.ad_decision_use_border_cb.setChecked(s["ad_decision_use_border"])
        ui.ad_bar_width_slider.set_value(s["ad_bar_width"])
        ui.ad_bar_height_slider.set_value(s["ad_bar_height"])
        _set_button_face(ui.ad_bar_color_pb, s["ad_bar_color"])
        ui.ad_bar_use_border_cb.setChecked(s["ad_bar_use_border"])

        # titles
        ui.title_width_slider.set_value(s["title_width"])

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

    def _connect_export_image_format_button_group(self):
        @Slot(QAbstractButton)
        def button_group_action_function(pb):
            self.settings_manager.change_one_setting(
                         "export_image_format", pb.text())
        group = self.ui.export_image_format_button_group
        group.buttonClicked.connect(button_group_action_function)

    def _connect_controls(self):
        ui = self.ui
        sm = self.settings_manager

        # export
        self._connect_cb(ui.export_background_is_transparent_cb,
                                          "export_background_is_transparent")
        self._connect_cb(ui.export_header_is_hidden_cb,
                                          "export_header_is_hidden")
        ui.export_header_vertical_spacing_slider.connect_slider(0, 20, sm,
                     "export_header_vertical_spacing",
                     "Vertical space between the header and the graph")

        # background
        ui.background_color_gradient_slider.connect_slider(100, 200, sm,
                     "background_color_gradient", "Background color gradient")
        self._connect_color_pb(ui.background_color_pb, "background_color")
        self._connect_export_image_format_button_group()

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
        ui.trace_hide_collapse_opacity_slider.connect_slider(0, 255, sm,
                     "trace_hide_collapse_opacity",
                     "Opacity of hidden/collapsed nodes and edges")
        ui.trace_node_width_slider.connect_slider(20, 333, sm,
                     "trace_node_width", "Trace node width")
        ui.trace_node_height_slider.connect_slider(10, 200, sm,
                     "trace_node_height", "Trace node height")
        ui.trace_node_h_spacing_slider.connect_slider(15, 550, sm,
                     "trace_node_h_spacing", "Trace node horizontal spacing")
        ui.trace_node_v_spacing_slider.connect_slider(15, 100, sm,
                     "trace_node_v_spacing", "Trace node vertical spacing")
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
        ui.trace_node_color_gradient_slider.connect_slider(100, 200, sm,
                     "trace_node_color_gradient", "Trace node color gradient")
        ui.trace_edge_arrow_size_slider.connect_slider(3, 20, sm,
                     "trace_edge_arrow_size", "Trace edge arrow size")
        ui.trace_edge_annotation_width_slider.connect_slider(50, 300, sm,
                  "trace_edge_annotation_width", "Trace edge annotation width")
        ui.trace_edge_annotation_background_opacity_slider.connect_slider(
                   0, 255, sm, "trace_edge_annotation_background_opacity",
                     "Trace edge annotation background opacity")
        self._connect_color_pb(ui.trace_edge_in_color_pb, "trace_edge_in_color")
        self._connect_color_pb(ui.trace_edge_follows_color_pb,
                                            "trace_edge_follows_color")
        self._connect_color_pb(ui.trace_edge_user_defined_color_pb,
                                            "trace_edge_user_defined_color")

        # graphs
        ui.graph_node_width_slider.connect_slider(20, 333, sm,
                     "graph_node_width", "Graph node width")
        ui.graph_node_height_slider.connect_slider(10, 200, sm,
                     "graph_node_height", "Graph node height")
        ui.graph_node_h_spacing_slider.connect_slider(40, 550, sm,
                     "graph_node_h_spacing", "Graph node horizontal spacing")
        ui.graph_node_v_spacing_slider.connect_slider(20, 100, sm,
                     "graph_node_v_spacing", "Graph node vertical spacing")
        ui.graph_node_corner_rounding_slider.connect_slider(0, 99, sm,
                     "graph_node_corner_rounding", "Graph node corner rounding")
        self._connect_cb(ui.graph_node_use_border_cb, "graph_node_use_border")
        self._connect_cb(ui.graph_node_use_shadow_cb, "graph_node_use_shadow")
        self._connect_color_pb(ui.graph_node_color_pb, "graph_node_color")
        ui.graph_node_color_gradient_slider.connect_slider(100, 200, sm,
                     "graph_node_color_gradient", "Graph node color gradient")
        ui.graph_edge_arrow_size_slider.connect_slider(3, 20, sm,
                     "graph_edge_arrow_size", "Graph edge arrow size")
        ui.graph_edge_annotation_width_slider.connect_slider(50, 300, sm,
                  "graph_edge_annotation_width", "Graph edge annotation width")
        ui.graph_edge_annotation_background_opacity_slider.connect_slider(
                   0, 255, sm, "graph_edge_annotation_background_opacity",
                     "Graph edge annotation background opacity")
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
        ui.bar_chart_bar_length_slider.connect_slider(50, 400, sm,
                     "bar_chart_bar_length", "Bar chart bar length")
        ui.bar_chart_bar_thickness_slider.connect_slider(10, 100, sm,
                     "bar_chart_bar_thickness", "Bar chart bar thickness")
        ui.bar_chart_bar_gap_slider.connect_slider(0, 100, sm,
                     "bar_chart_bar_gap", "Bar chart gap between bars")
        self._connect_cb(ui.bar_chart_bar_use_border_cb,
                                            "bar_chart_bar_use_border")
        ui.bar_chart_bar_annotation_decimal_places_slider.connect_slider(
                     0, 4, sm, "bar_chart_bar_annotation_decimal_places",
                     "Number of decimal places to show in bar annotation")
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
        ui.ad_h_spacing_slider.connect_slider(40, 250, sm,
                     "ad_h_spacing", "Activity diagram horizontal spacing")
        ui.ad_v_spacing_slider.connect_slider(25, 100, sm,
                     "ad_v_spacing", "Activity diagram vertical spacing")
        ui.ad_action_width_slider.connect_slider(20, 333, sm,
                     "ad_action_width", "Activity diagram action width")
        ui.ad_action_height_slider.connect_slider(10, 200, sm,
                     "ad_action_height", "Activity diagram action height")
        ui.ad_action_corner_rounding_slider.connect_slider(0, 99, sm,
                     "ad_action_corner_rounding",
                     "Activity diagram action corner rounding")
        self._connect_color_pb(ui.ad_action_color_pb, "ad_action_color")
        ui.ad_action_color_gradient_slider.connect_slider(100, 200, sm,
                     "ad_action_color_gradient",
                     "Activity diagram action color gradient")
        self._connect_cb(ui.ad_action_use_border_cb, "ad_action_use_border")
        ui.ad_edge_arrow_size_slider.connect_slider(3, 20, sm,
                     "ad_edge_arrow_size",
                     "Activity diagram action edge arrow size")
        self._connect_color_pb(ui.ad_edge_color_pb, "ad_edge_color")
        ui.ad_start_size_slider.connect_slider(9, 50, sm,
                     "ad_start_size", "Activity diagram start size")
        self._connect_color_pb(ui.ad_start_color_pb, "ad_start_color")
        self._connect_cb(ui.ad_start_use_border_cb, "ad_start_use_border")
        ui.ad_end_size_slider.connect_slider(9, 50, sm,
                     "ad_end_size", "Activity diagram end size")
        self._connect_color_pb(ui.ad_end_color_pb, "ad_end_color")
        self._connect_cb(ui.ad_end_use_border_cb, "ad_end_use_border")
        ui.ad_decision_width_slider.connect_slider(15, 50, sm,
                     "ad_decision_width", "Activity diagram decision width")
        ui.ad_decision_height_slider.connect_slider(15, 50, sm,
                     "ad_decision_height", "Activity diagram decision height")
        self._connect_cb(ui.ad_decision_use_border_cb, "ad_decision_use_border")
        self._connect_color_pb(ui.ad_decision_color_pb, "ad_decision_color")
        ui.ad_bar_width_slider.connect_slider(87, 200, sm,
                     "ad_bar_width", "Activity diagram bar width")
        ui.ad_bar_height_slider.connect_slider(10, 20, sm,
                     "ad_bar_height", "Activity diagram bar height")
        self._connect_color_pb(ui.ad_bar_color_pb, "ad_bar_color")
        self._connect_cb(ui.ad_bar_use_border_cb, "ad_bar_use_border")

        # titles
        ui.title_width_slider.connect_slider(50, 300, sm,
                     "title_width", "Maximum title width")


