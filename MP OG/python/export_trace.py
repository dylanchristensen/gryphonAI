from math import ceil
from PySide6.QtCore import QSize, QSizeF, QRect, QRectF
from PySide6.QtCore import QMarginsF
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtGui import QPainter, QImage, QPageSize, QPdfWriter
from PySide6.QtWidgets import QStyleOption
from font_helper import cell_height, text_width
from preferences import preferences
from os_compatibility import is_mac
from settings import preferred_pen, settings
from paint_raw import paint_background, mark_flag, paint_header
from box import BOX_PADDING
from verbose import verbose

def _header_width(left_text, right_text):
    if not settings["export_header_is_hidden"]:

        # account for margins, text, mark icon, and space between
        return text_width(left_text) + text_width(right_text) + 5*2 + 30 + 10
    else:
        # no header
        return 0

def _header_height():
    if not settings["export_header_is_hidden"]:
        return cell_height() + settings["export_header_vertical_spacing"]
    else:
        return 0


# left and right text
def _header_text(graph_index, graph_item, scope):
    if graph_index == 0:
        return "Global view", ""
    else:
        left_text = "Scope %d  Trace %d"%(scope, graph_index)
        if settings["trace_show_type_1_probability"] \
                           and "trace" in graph_item.gry_graph:
            right_text = "Type 1 probability %.8g"%(
                           graph_item.gry_graph["trace"]["probability"])
        else:
            right_text = ""
    return left_text, right_text

def _graph_rect(graph_item, graph_index, scope):

    # identify the graph size without the header
    w = graph_item.bounding_rect().width()
    h = graph_item.bounding_rect().height()

    # accout for optional header
    if not settings["export_header_is_hidden"]:
        left_text, right_text = _header_text(graph_index, graph_item, scope)
        header_w = _header_width(left_text, right_text)
        header_h = _header_height()
        w = max(w, header_w)
        h += header_h

    rect = QRect(0, 0, ceil(w), ceil(h))

    # adjust rectangle boundary based on test results
    if settings["export_image_format"] in [".bmp", ".jpg", ".png"]:
        rect.adjust(0, 0, 1, 1)
    elif settings["export_image_format"] == ".pdf":
        rect.adjust(0, 0, 3, 3)
    elif settings["export_image_format"] == ".svg":
        rect.adjust(-1, -1, 1, 1)
    else:
        raise RuntimeError

    return rect

def _paint(painter, graph_rect, graph_item, graph_index, scope):
    # set the font family else Mac selects font-family=".AppleSystemUIFont"
    if is_mac():
        font = painter.font()
        if verbose():
            print("export font before setFamily:", font)
        font.setFamily("Arial")
        if verbose():
            print("export font after setFamily:", font)
        painter.setFont(font)

    # usually paint the background
    if settings["export_image_format"] in [".png", ".svg"] \
                    and settings["export_background_is_transparent"]:
        # (.png or .svg) and transparent so no background
        pass
    else:
        paint_background(painter, graph_rect)

    # maybe paint the header
    if not settings["export_header_is_hidden"]:
        # paint the header
        left_text, right_text = _header_text(graph_index, graph_item, scope)
        mark = mark_flag(graph_item)
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setPen(preferred_pen())
        paint_header(painter, graph_index, left_text, right_text, mark,
                     graph_rect.width())
        painter.translate(0, _header_height())

    # paint the graph
    painter.translate(-graph_item.bounding_rect().topLeft())
    graph_item.paint_items(painter, QStyleOption(), graph_item)

def _export_image(graph_rect, filename, graph_item, graph_index, scope):
    image = QImage(graph_rect.width(), graph_rect.height(),
                   QImage.Format_ARGB32)
    painter = QPainter(image)
    _paint(painter, graph_rect, graph_item, graph_index, scope)
    painter.end()
    try:
        success = image.save(filename, None, 100)
        if success:
            return ""
        else:
            return "Error: Export failed"
    except Exception as e:
        status = "Error exporting image file '%s': %s" % (filename, str(e))
        return status

def _export_svg(graph_rect, filename, graph_item, graph_index, scope,
                application):

    # create the painter with its target pixel map to paint in
    svg_generator = QSvgGenerator()
    svg_generator.setFileName(filename)
    svg_generator.setSize(QSize(graph_rect.width(), graph_rect.height()))
    svg_generator.setViewBox(graph_rect)

    # make the SVG generator DPI match screen[0] else locations and text
    # scale will not match
    screen = application.screens()[0]
    new_dpi = screen.logicalDotsPerInch()
    if verbose():
        print("qscreen logicalDotsPerInch:", screen.logicalDotsPerInch())
        print("qscreen logicalDotsPerInchX:", screen.logicalDotsPerInchX())
        print("qscreen logicalDotsPerInchY:", screen.logicalDotsPerInchY())
        print("qscreen physicalDotsPerInch:", screen.physicalDotsPerInch())
        print("qscreen physicalDotsPerInchX:", screen.physicalDotsPerInchX())
        print("qscreen physicalDotsPerInchY:", screen.physicalDotsPerInchY())
        print("changing svg dpi %d to screen[0] logical dpi %d"%(
                                svg_generator.resolution(), new_dpi))
    svg_generator.setResolution(new_dpi)

    # start the painter using the configured SVG generator
    painter = QPainter()
    painter.begin(svg_generator)
    _paint(painter, graph_rect, graph_item, graph_index, scope)

    # done
    no_longer_active = painter.end()
    if no_longer_active:
        return ""
    else:
        return "Error: Export failed"

def _export_pdf(graph_rect, filename, graph_item, graph_index, scope):
    printer = QPdfWriter(filename)

    # make the coordinate size match the font size
    # We use 96 dpi instead of printer 1200 dpi because the font size
    # and the coordinate system scale match at 96 dpi.
    printer.setResolution(96)

    # .pdf renders 2x too large so rescale to match the size we see on
    # the screen
    pdf_scale = 0.5

    # make the page size match the coordinate size
    if verbose():
        print("layout before:", printer.pageLayout())
    page_size = QPageSize(QSizeF(graph_rect.width() * 72 / 96 * pdf_scale,
                                 graph_rect.height() * 72 / 96 * pdf_scale),
                          QPageSize.Unit.Point, "Gryphon graph",
                          QPageSize.SizeMatchPolicy.ExactMatch)
    printer.setPageSize(page_size)

    # remove the page margins
    printer.setPageMargins(QMarginsF(0, 0, 0, 0))
    if verbose():
        print("layout after:", printer.pageLayout())
        print("printer resolution:", printer.resolution())
        print("painter font:", painter.font())

    # paint
    painter = QPainter()
    is_opened = painter.begin(printer)

    # pdf cuts off the border so move the painter
    painter.translate(0.5, 0.5)

    # pdf paints 2x too large so rescale
    painter.scale(pdf_scale, pdf_scale)
    if not is_opened:
        return "Error exporting image file '%s'"%filename
    _paint(painter, graph_rect, graph_item, graph_index, scope)
    painter.end()
    return ""

# export trace as image file.  Return (status)
# painting is slightly similar to GraphListItemDelegate.paint().
# return "" else failure status
def export_trace(filename, graph_item, graph_index, scope, application):

    # validate filename extension
    out_type = settings["export_image_format"]
    if filename[-4:] != out_type:
        return "Error: export file type %s does not match filename" \
               " extension for file %s"%(out_type, filename)

    # calculate the graph rectangle
    graph_rect = _graph_rect(graph_item, graph_index, scope)

    if out_type in [".bmp", ".jpg", ".png"]:
        return _export_image(graph_rect, filename,
                             graph_item, graph_index, scope)
    elif out_type == ".pdf":
        return _export_pdf(graph_rect, filename,
                           graph_item, graph_index, scope)
    elif out_type == ".svg":
        return _export_svg(graph_rect, filename,
                           graph_item, graph_index, scope, application)
    else:
        return "unrecognized export graph extention '%s'"%out_type

