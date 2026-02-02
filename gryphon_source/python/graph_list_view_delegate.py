from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtWidgets import QStyle

from graph_list_table_model import GRAPH_COLUMN
from font_helper import cell_height
from paint_raw import paint_background, mark_flag, paint_header
from color_helper import contrasting_color
from settings import settings

def _brief_header_text(graph_index, graph_item):
    if graph_index == 0:
        return "Global"
    else:
        if settings["trace_show_type_1_probability"] \
                           and "trace" in graph_item.gry_graph:
            return "%d  p=%.8g"%(graph_index,
                           graph_item.gry_graph["trace"]["probability"])
        else:
            return "%d"%graph_index

def paint_graph_list_item(painter, graph_item, graph_index, scope, option):

    painter.save()

    graph_bounds = graph_item.bounding_rect()
    w = option.rect.width()
    h = option.rect.height()
    left_text = _brief_header_text(graph_index, graph_item)
    if option.state & QStyle.State_Selected:
        painter.setPen(contrasting_color(
                                  option.palette.highlight().color()))
    mark = mark_flag(graph_item)
    paint_header(painter, graph_index, left_text, "", mark, w)
    painter.translate(0, cell_height())

    if graph_bounds.width() > 0:
        # scale to fit
        scale = min(w / graph_bounds.width(),
                    (h-cell_height()) / graph_bounds.height())
    else:
        # nothing to show
        scale = 1
    painter.scale(scale, scale)
    painter.translate(-graph_bounds.x(), -graph_bounds.y())
    paint_background(painter, graph_bounds)
    graph_item.paint_items(painter, option, graph_item)

    painter.restore()

# ref. https://github.com/scopchanov/CustomList/blob/master/app/src/Delegate.cpp
class GraphListViewDelegate(QStyledItemDelegate):

    def __init__(self, graph_list_selection_model,
                       navigation_column_width_manager):
        super().__init__()
        self.graph_list_selection_model = graph_list_selection_model
        self.navigation_column_width_manager = navigation_column_width_manager

   # paint
    def paint(self, painter, option, proxy_model_index):
        # we should only be accessing the graph column
        if proxy_model_index.column() != GRAPH_COLUMN:
            raise Exception("Bad")

        # Specifically paint the highlight background because Windows
        # fails to do so.
        if option.state & QStyle.State_Selected:
             painter.fillRect(option.rect, option.palette.highlight())

        painter.save()
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # translate axis to cell
        painter.translate(option.rect.x(), option.rect.y())

        # this graph
        graph_index, graph_item = self.graph_list_selection_model \
                                 .graph_index_and_item(proxy_model_index)

        # paint the graph within the bounds defined in option.rect
        _scope = 0
        paint_graph_list_item(painter, graph_item, graph_index, _scope, option)

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

