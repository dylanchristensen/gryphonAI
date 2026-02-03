from PySide6.QtGui import QRadialGradient, QLinearGradient
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QRectF
from settings_manager import settings
from font_helper import font_height, cell_height
from settings_manager import preferred_pen
from preferences_manager import preferences
from font_helper import text_width

BOX_PADDING = 20

def _paint_background(painter, fill_rect):
    gradient = QLinearGradient(fill_rect.topLeft(),
                               fill_rect.bottomRight())
    c = QColor(settings["background_color"])
    gradient.setColorAt(0, c.lighter(settings["background_color_gradient"]))
    gradient.setColorAt(0.5, c)
    gradient.setColorAt(1, c.darker(settings["background_color_gradient"]))
    painter.fillRect(fill_rect, QBrush(gradient))

# return left and right text
def _header_text(graph_index, graph_item, scope):
    if graph_index == 0:
        return "Global view", ""
    else:
        left_text = "Scope %d  Trace %d"%(scope, graph_index)
        if preferences["show_type_1_probability"] \
                           and "trace" in graph_item.gry_graph:
            right_text = "Type 1 probability %.8g"%(
                           graph_item.gry_graph["trace"]["probability"])
        else:
            right_text = ""
    return left_text, right_text

def _brief_header_text(graph_index, graph_item):
    if graph_index == 0:
        return "Global"
    else:
        if preferences["show_type_1_probability"] \
                           and "trace" in graph_item.gry_graph:
            return "%d  p=%.8g"%(graph_index,
                           graph_item.gry_graph["trace"]["probability"])
        else:
            return "%d"%graph_index

def _paint_mark(painter, mark, x):
    # move painter to center of mark near top-right corner
    painter.save()

    # get color based on mark
    if mark == "M":
        c1 = Qt.GlobalColor.red
        c2 = Qt.GlobalColor.darkRed
    else:
        # mark not recognized
        c1 = Qt.GlobalColor.gray
        c2 = Qt.GlobalColor.darkGray

    # draw circle
    painter.translate(x - 12, 12)
    gradient = QRadialGradient(-3, -3, 10)
    gradient.setColorAt(0, c1)
    gradient.setColorAt(1, c2)
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(-7, -7, 14, 14)
    painter.restore()

def _paint_header(painter, graph_index, left_text, right_text, mark,
                  left_margin, right_margin):
    y = font_height()
    if graph_index == 0:
        # paint the global view title
        painter.drawText(left_margin + 5, y, left_text)

    else:
        # paint the left text
        painter.drawText(left_margin + 5, y, left_text)

        # paint right text and any mark
        x = int(right_margin) - 5
        if mark == "U":
            # no mark
            painter.drawText(x - text_width(right_text), y, right_text)
        else:
            painter.drawText(x - text_width(right_text) - 30, y, right_text)
            _paint_mark(painter, mark, x)

def _paint_graph(painter, graph_item, option):

    # paint box and trace
    painter.save()
    painter.translate(graph_item.trace.trace_box.pos())
    graph_item.trace.trace_box.paint(painter, option, None)
    if graph_item.nodes and graph_item.trace_box._visible:
        painter.translate(graph_item.trace_box.pos())
        graph_item.trace_box.paint(painter, option, None)
        for edge in graph_item.edges:
            edge.paint(painter, option, None)
        for node in graph_item.nodes:
            # translate for this node
            painter.save()
            painter.translate(node.pos())
            node.paint(painter, option, None)
            painter.restore()
    painter.restore()

    # paint any views
    for report in graph_item.view_reports:
        painter.save()
        painter.translate(report.pos())
        report.paint(painter, option, None)
        painter.restore()
    for table in graph_item.view_tables:
        painter.save()
        painter.translate(table.pos())
        table.paint(painter, option, None)
        painter.restore()

# graph_index 0 is the global view.  graph_index 1 and on are the traces
"""
Paint the graph by calling paint on the QGraphicsItem items.
We use their paint methods instead of managing them as QGraphicsItems in
a QGraphicsScene because QGraphicsItems can't live in multiple scenes.

We paint graph items two ways:
* For the graph list, we paint the title above the graph
  and paint the background and graph below it, scaled.
* For exported plots, we paint the title within the graph
  and we do not scale it.

We use option to determine which way to paint.  If option defines a width
and height, we are painting a scaled view for the graph list.
"""
def paint_graph_item(painter, graph_item, graph_index, scope, option):

    painter.save()
    p = BOX_PADDING

    # mark
    if "trace" in graph_item.gry_graph:
        mark = graph_item.gry_graph["trace"]["mark"]
    else:
        mark = None

    # paint depending on destination
    if option.rect.width() == 0:
        # For .png export: Not scaled, the header is within the background.
        graph_bounds = graph_item.bounding_rect().adjusted(
                                               -p, -p - cell_height(), p, p)

        w = graph_bounds.width()
        if graph_index == 0 and w < 200: # force empty global view wider
            w = 200
        h = graph_bounds.height()
        _paint_background(painter, QRectF(0, 0, w, h))
        painter.setPen(preferred_pen())
        left_text, right_text = _header_text(graph_index, graph_item, scope)
        _paint_header(painter, graph_index, left_text, right_text, mark,
                      BOX_PADDING, graph_bounds.width() - BOX_PADDING)
        painter.translate(-graph_bounds.x(), -graph_bounds.y())
        graph_item.paint_items(painter, option, graph_item)

    else:
        # For graph list: a brief header is above the painted background
        # and the graph is scaled.
        graph_bounds = graph_item.bounding_rect().adjusted(-p, -p, p, p)
        w = option.rect.width()
        h = option.rect.height()
        left_margin = 0
        right_margin = w
        left_text = _brief_header_text(graph_index, graph_item)
        _paint_header(painter, graph_index, left_text, "", mark,
                      left_margin, right_margin)
        painter.translate(0, cell_height())

        scale = min(w / graph_bounds.width(),
                    (h-cell_height()) / graph_bounds.height())
        painter.scale(scale, scale)
        painter.translate(-graph_bounds.x(), -graph_bounds.y())
        _paint_background(painter, graph_bounds)
        graph_item.paint_items(painter, option, graph_item)

    painter.restore()

