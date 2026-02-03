from PySide6.QtGui import QColor
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtWidgets import QStyle

from paint_graph_item import paint_graph_item
from graph_list_table_model import GRAPH_COLUMN
from font_helper import cell_height

# ref. https://github.com/scopchanov/CustomList/blob/master/app/src/Delegate.cpp
class GraphListTableViewDelegate(QStyledItemDelegate):

    def __init__(self, graph_list_table, navigation_column_width_manager):
        super(GraphListTableViewDelegate, self).__init__()
        self.graph_list_table = graph_list_table
        self.navigation_column_width_manager = navigation_column_width_manager

   # paint
    def paint(self, painter, option, proxy_model_index):
        # all but column 0 should be hidden in graph_list_table_view
        if proxy_model_index.column() != GRAPH_COLUMN:
            raise Exception("Bad")

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # translate axis to cell
        painter.translate(option.rect.x(), option.rect.y())

        # this graph
        graph_index, column = self.graph_list_table\
                         .proxy_model_index_to_graph_index(proxy_model_index)
        if column != GRAPH_COLUMN:
            raise RuntimeError("bad")
        graph_item = self.graph_list_table.source_model.graphs[graph_index]

        # paint the graph within the bounds defined in option.rect
        _scope = 0
        paint_graph_item(painter, graph_item, graph_index, _scope, option)

        # draw dividing line
        painter.setPen(Qt.GlobalColor.gray)
        bottom = option.rect.height() - 1
        width = option.rect.width()
        painter.drawLine(0, bottom, width, bottom)

        # restore painter state
        painter.restore()

    # sizeHint
    def sizeHint(self, _option, _model_index):
        # Make width hint narrow to prevent horizontal scrollbar.
        # Make the height the width allowance plus text height
        # plus 1 taller for dividing line so actual graph is square.
        # The size actually provided to paint() is in option.rect.
        return QSize(1, self.navigation_column_width_manager.width
                        + cell_height() + 1)

