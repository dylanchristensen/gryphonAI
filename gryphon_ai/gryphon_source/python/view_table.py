from box_types import TABLE_BOX
from box import Box
from view_text import ViewText
from view_table_table import ViewTableTable

class ViewTable():

    def __init__(self, background_box, gry_table):
        super().__init__()

        self.background_box = background_box
        self.table_box = Box(self, TABLE_BOX, gry_table["box"])

        # table
        self.table = ViewTableTable(self.table_box, gry_table["data"])

        # title
        self.title = ViewText(self.table_box, gry_table["title"])

        # maybe align the table
        if not "x" in gry_table["box"]:
            self.table.setX(0)
            self.table.setY(0)
            self.title.align_above([self.table])

            # indicate geometry change in any content in order to
            # immediately correct changed table_box geometry and box
            self.title.prepareGeometryChange()

            # align box to the right of the upper right edge
            # of the current parent bounds
            self.table_box.align_to_right(background_box)

        self.table_box.set_parent_box(background_box)

    def reset_appearance(self):
        self.table.reset_appearance()
        self.table_box.reset_appearance()

    def get_gry(self):
        gry_table = {"box":self.table_box.get_gry(),
                     "title":self.title.get_gry(),
                     "data":self.table.get_gry(),
                    }
        return gry_table

    def paint_items(self, painter, option, widget):
        if not self.table_box.is_visible:
            return
        painter.save()
        painter.translate(self.table_box.pos())
        self.table_box.paint(painter, option, widget)
        painter.translate(self.table.pos())
        self.table.paint(painter, option, widget)
        painter.restore()

