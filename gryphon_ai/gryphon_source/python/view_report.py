from box_types import REPORT_BOX
from box import Box
from view_report_report import ViewReportReport

class ViewReport():

    def __init__(self, background_box, gry_report):
        super().__init__()

        self.background_box = background_box
        self.report_box = Box(self, REPORT_BOX, gry_report["box"])
        self.report = ViewReportReport(self.report_box, gry_report)

        # maybe align the report
        if not "x" in gry_report["box"]:
            self.report_box.align_to_right(background_box)
        self.report_box.set_parent_box(background_box)

    def reset_appearance(self):
        self.report.reset_appearance()
        self.report_box.reset_appearance()

    def get_gry(self):
        gry_report = self.report.get_gry()
        gry_report["box"] = self.report_box.get_gry(),
        return gry_report

    def paint_items(self, painter, option, widget):
        if not self.report_box.is_visible:
            return
        painter.save()
        painter.translate(self.report_box.pos())
        self.report_box.paint(painter, option, widget)
        painter.translate(self.report.pos())
        self.report.paint(painter, option, widget)
        painter.restore()

