from PySide6.QtGui import QClipboard
from mp_logger import log
from box_types import REPORT_BOX
from box import Box
from view_title import ViewTitle
from view_report_report import ViewReportReport

class ViewReport():

    def copy_report_to_clipboard(self):
        gry_report = self.report.get_gry()

        # title plus data
        csv_text = gry_report["title"] + "\n" \
                       + "\n".join(["%s"%x for x in gry_report["data"]])

        # copy to clipboard
        clipboard = QClipboard()
        clipboard.setText(csv_text)
        log('Report "%s" copied to system clipboard'%gry_report["title"])

    def __init__(self, background_box, gry_report):
        super().__init__()

        self.background_box = background_box
        self.box = Box(self, REPORT_BOX, gry_report["box"], background_box)

        # report
        self.report = ViewReportReport(self.box, gry_report["data"])

        # title
        self.title = ViewTitle(self.box, gry_report["title"])

        # maybe align the report
        if not "x" in gry_report["box"]:
            self.report.setX(0)
            self.report.setY(0)
            self.title.align_above([self.report])
            self.title.prepareGeometryChange()

        # set box geometry
        self.box.reset_appearance()

    def reset_appearance(self):
        self.title.reset_appearance()
        self.report.reset_appearance()
        self.box.reset_appearance()

    def get_gry(self):
        gry_report = {"box":self.box.get_gry(),
                      "title":self.title.get_gry(),
                      "data":self.report.get_gry(),
                     }
        return gry_report

    def paint_items(self, painter, option, widget):
        if not self.box.is_visible:
            return
        painter.save()
        painter.translate(self.box.pos())
        self.box.paint(painter, option, widget)
        for item in [self.title, self.report]:
            painter.save()
            painter.translate(item.pos())
            item.paint(painter, option, widget)
            painter.restore()
        painter.restore()

