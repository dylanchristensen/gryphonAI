from PySide6.QtGui import QClipboard
from mp_logger import log
from box_types import TABLE_BOX
from box import Box
from view_title import ViewTitle
from view_table_table import ViewTableTable

class ViewTable():

    def copy_table_to_clipboard(self):
        # create CSV text
        gry_table = self.get_gry()
        title = gry_table["title"]["text"]
        headers = gry_table["data"]["headers"]
        rows = gry_table["data"]["rows"]

        text_rows = list()
        for row_of_columns in gry_table["data"]["rows"]:
            text_rows.append(["%s"%x for x in row_of_columns])

        csv_text = title + "\n" + ", ".join(headers) + "\n" \
                             + "\n".join([", ".join(x) for x in text_rows])

        # copy to clipboard
        clipboard = QClipboard()
        clipboard.setText(csv_text)
        log('Table "%s" copied to the system clipboard'%title)

    def __init__(self, background_box, gry_table):
        super().__init__()

        self.background_box = background_box
        self.box = Box(self, TABLE_BOX, gry_table["box"], background_box)

        # table
        self.table = ViewTableTable(self.box, gry_table["data"])

        # title
        self.title = ViewTitle(self.box, gry_table["title"])

        # maybe align the table
        if not "x" in gry_table["box"]:
            self.table.setX(0)
            self.table.setY(0)
            self.table.prepareGeometryChange()
            self.title.align_above([self.table])
            self.title.prepareGeometryChange()

        # set box geometry
        self.box.reset_appearance()

    def reset_appearance(self):
        self.title.reset_appearance()
        self.table.reset_appearance()
        self.box.reset_appearance()

    def get_gry(self):
        gry_table = {"box":self.box.get_gry(),
                     "title":self.title.get_gry(),
                     "data":self.table.get_gry(),
                    }
        return gry_table

    # paint directly using paint methods rather than through QGraphicsScene
    def paint_items(self, painter, option, widget):
        if not self.box.is_visible:
            return
        painter.save()
        painter.translate(self.box.pos())
        self.box.paint(painter, option, widget)
        for item in [self.title, self.table]:
            painter.save()
            painter.translate(item.pos())
            item.paint(painter, option, widget)
            painter.restore()
        painter.restore()

