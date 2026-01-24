from sys import maxsize
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import QRectF
from PySide6.QtGui import QUndoStack
from empty_gry_graph import empty_gry_graph
from box_types import BACKGROUND_BOX
from box import Box, BOX_PADDING
from view_trace import ViewTrace
from view_report import ViewReport
from view_table import ViewTable
from view_graph import ViewGraph
from view_bar_chart import ViewBarChart
from view_gantt_chart import ViewGanttChart
from view_ad import ViewAD # Activity Diagram

def _change_node_spacing(gry_view, x_ratio, y_ratio):
    if x_ratio != 1.0:
        for gry_node in gry_view["nodes"]:
            gry_node["x"] *= x_ratio
    if y_ratio != 1.0:
        for gry_node in gry_view["nodes"]:
            gry_node["y"] *= y_ratio

def _change_edge_spacing(gry_view, x_ratio, y_ratio):
    if x_ratio != 1.0:
        for gry_edge in gry_view["edges"]:
            gry_edge["ep1_x"] *= x_ratio
            gry_edge["ep2_x"] *= x_ratio
    if y_ratio != 1.0:
        for gry_edge in gry_view["edges"]:
            gry_edge["ep1_y"] *= y_ratio
            gry_edge["ep2_y"] *= y_ratio

def _change_title_spacing(gry_view, x_ratio, y_ratio):
    if x_ratio != 1.0:
        gry_view["title"]["x"] *= x_ratio
    if y_ratio != 1.0:
        gry_view["title"]["y"] *= y_ratio

# update spacing when the item is not initialized
def _change_gry_trace_item_spacing(gry_trace, x_ratio, y_ratio):
    # all trace items come with x,y
    _change_node_spacing(gry_trace, x_ratio, y_ratio)
    _change_edge_spacing(gry_trace, x_ratio, y_ratio)

# update spacing when the item is not initialized
def _change_gry_graph_item_spacing(gry_graph, x_ratio, y_ratio):
    # no graph items are placed until box has x,y
    if "x" in gry_graph["box"]:
        _change_title_spacing(gry_graph, x_ratio, y_ratio)
        _change_node_spacing(gry_graph, x_ratio, y_ratio)
        _change_edge_spacing(gry_graph, x_ratio, y_ratio)

# update spacing when the item is not initialized
def _change_gry_ad_item_spacing(gry_ad, x_ratio, y_ratio):
    # only nodes are placed until box has x,y
    _change_node_spacing(gry_ad, x_ratio, y_ratio)
    if "x" in gry_ad["box"]:
        _change_title_spacing(gry_ad, x_ratio, y_ratio)
        _change_edge_spacing(gry_ad, x_ratio, y_ratio)

class GraphItem(QObject):
    """Defines one graph item.
    Data structures:
      * trace, reports, tables, graphs, ...
      * node_lookup (list<int>) for the trace view

    Call reset_appearance when graph should be painted differently.
    """

    def __init__(self, gry_graph):
        super().__init__()
        self.gry_graph = gry_graph
        self.is_initialized = False

    # align views when they are not yet aligned
    def _align_views(self):
        # starting x, y
        x = 0
        y = 0

        # align trace
        if "trace" in self.gry_graph:
            x1, y1, w, h = self.trace.box.boundingRect().getRect()
            self.trace.box.setX(x - x1)
            self.trace.box.setY(y - y1)

            # put views to right of trace
            x += w + BOX_PADDING

        # align remaining views downward to right of trace
        for views in [self.view_reports, self.view_tables, self.view_graphs,
                      self.view_bar_charts, self.view_gantt_charts,
                      self.view_activity_diagrams]:
            for view in views:
                x1, y1, w, h = view.box.boundingRect().getRect()
                view.box.setX(x - x1)
                view.box.setY(y - y1)
                y_before = y
                y += h + BOX_PADDING

    # call this before rendering
    def initialize_items(self):
        if self.is_initialized:
            # already done
            return

        gry_graph = self.gry_graph

        # this item's undo stack
        self.undo_stack = QUndoStack()

        # outermost box
        self.background_box = Box(self, BACKGROUND_BOX, gry_graph["box"], None)

        # trace
        if "trace" in gry_graph:
            self.trace = ViewTrace(self.background_box, gry_graph["trace"])

        # view | report
        self.view_reports = list()
        for gry_view in gry_graph["reports"]:
            self.view_reports.append(ViewReport(self.background_box, gry_view))

        # view | table
        self.view_tables = list()
        for gry_view in gry_graph["tables"]:
            self.view_tables.append(ViewTable(self.background_box, gry_view))

        # view | graph
        self.view_graphs = list()
        for gry_view in gry_graph["graphs"]:
            self.view_graphs.append(ViewGraph(self.background_box, gry_view))

        # view | bar charts
        self.view_bar_charts = list()
        for gry_view in gry_graph["bar_charts"]:
            self.view_bar_charts.append(ViewBarChart(self.background_box,
                                                                  gry_view))

        # view | Gantt charts
        self.view_gantt_charts = list()
        for gry_view in gry_graph["gantt_charts"]:
            self.view_gantt_charts.append(ViewGanttChart(self.background_box,
                                                                  gry_view))

        # view | activity diagrams
        self.view_activity_diagrams = list()
        for gry_view in gry_graph["activity_diagrams"]:
            self.view_activity_diagrams.append(ViewAD(self.background_box,
                                                                  gry_view))

        if not self.has_trace() and not self.has_non_trace():
            # empty graph with uninitialized background box
            self.background_box.reset_appearance()

        self.is_initialized = True

        # maybe align views
        if not "x" in gry_graph["box"]:
            self._align_views()

    def get_gry(self):
        if self.is_initialized:
            gry_graph = empty_gry_graph()
            gry_graph["box"] = self.background_box.get_gry()

            # trace
            if self.has_trace():
                gry_graph["trace"] = self.trace.get_gry()

            view_tuples = [("reports", self.view_reports),
                           ("tables", self.view_tables),
                           ("graphs", self.view_graphs),
                           ("bar_charts", self.view_bar_charts),
                           ("gantt_charts", self.view_gantt_charts),
                           ("activity_diagrams", self.view_activity_diagrams),
                          ]
            for name, views in view_tuples:
                for view in views:
                    gry_graph[name].append(view.get_gry())

            return gry_graph
        else:
            return self.gry_graph

    def paint_items(self, painter, _option, _widget):

        # background box
        self.background_box.paint(painter, _option, _widget)

        # trace
        if self.has_trace():
            self.trace.paint_items(painter, _option, _widget)

        # any views:
        for views in [self.view_reports, self.view_tables, self.view_graphs,
                      self.view_bar_charts, self.view_gantt_charts,
                      self.view_activity_diagrams]:
            for view in views:
                view.paint_items(painter, _option, None)

    def has_trace(self):
        return "trace" in self.gry_graph

    def has_non_trace(self):
        return bool(len(self.gry_graph["graphs"])
                  + len(self.gry_graph["reports"])
                  + len(self.gry_graph["tables"])
                  + len(self.gry_graph["bar_charts"])
                  + len(self.gry_graph["gantt_charts"])
                  + len(self.gry_graph["activity_diagrams"]))

    # make any hidden views visible
    def unhide_hidden_views(self):
        if self.is_initialized:
            # make view boxes visible
            if self.has_trace():
                self.trace.box.set_visible(True)
            for views in [self.view_reports, self.view_tables, self.view_graphs,
                          self.view_bar_charts, self.view_gantt_charts,
                          self.view_activity_diagrams]:
                for view in views:
                    view.box.set_visible(True)
        else:
            # make gry_graph boxes visible
            if self.has_trace():
                self.gry_graph["trace"]["box"]["is_visible"] = True

            for view in ["graphs", "reports", "tables", "bar_charts",
                             "gantt_charts", "activity_diagrams"]:
                for gry_view in self.gry_graph[view]:
                    gry_view["box"]["is_visible"] = True

    # reset appearance when graph color or shape changes
    def reset_appearance(self):
        if self.is_initialized:
            self.background_box.reset_appearance()
            if self.has_trace():
                self.trace.reset_appearance()
            for views in [self.view_reports, self.view_tables, self.view_graphs,
                          self.view_bar_charts, self.view_gantt_charts,
                          self.view_activity_diagrams]:
                for view in views:
                    view.reset_appearance()

    def change_item_spacing(self, ratios):
        # trace
        h_ratio, v_ratio = ratios["trace_h"], ratios["trace_v"]
        if h_ratio != 1.0 or v_ratio != 1.0:
            if self.is_initialized:
                if self.has_trace():
                    self.trace.change_item_spacing(h_ratio, v_ratio)
            else:
                if "trace" in self.gry_graph:
                    _change_gry_trace_item_spacing(self.gry_graph["trace"],
                                                   h_ratio, v_ratio)

        # graphs
        h_ratio, v_ratio = ratios["graph_h"], ratios["graph_v"]
        if h_ratio != 1.0 or v_ratio != 1.0:
            if self.is_initialized:
                for graph in self.view_graphs:
                    graph.change_item_spacing(h_ratio, v_ratio)
            else:
                for gry_graph in self.gry_graph["graphs"]:
                    _change_gry_graph_item_spacing(gry_graph, h_ratio, v_ratio)

        # activity diagrams
        h_ratio, v_ratio = ratios["ad_h"], ratios["ad_v"]
        if h_ratio != 1.0 or v_ratio != 1.0:
            if self.is_initialized:
                for ad in self.view_activity_diagrams:
                    ad.change_ad_item_spacing(h_ratio, v_ratio)
            else:
                for gry_ad in self.gry_graph["activity_diagrams"]:
                    _change_gry_ad_item_spacing(gry_ad, h_ratio, v_ratio)

    def bounding_rect(self):
        self.initialize_items()
        return self.background_box.boundingRect()

