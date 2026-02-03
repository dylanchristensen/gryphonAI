from PySide6.QtWidgets import QGraphicsItem
_type = QGraphicsItem.UserType
def _next():
    global _type
    _type += 1
    return _type

# user-defined QGraphicsItem types
BOX_TYPE = _next()
NODE_TYPE = _next()
EDGE_TYPE = _next()
EDGE_GRIP_TYPE = _next()
VIEW_ACTIVITY_DIAGRAM_TYPE = _next()
VIEW_BAR_CHART_BARS_TYPE = _next()
VIEW_GANTT_CHART_GANTT_TYPE = _next()
VIEW_REPORT_TYPE = _next()
VIEW_GRAPH_TYPE = _next()
VIEW_GRAPH_NODE_TYPE = _next()
VIEW_GRAPH_EDGE_TYPE = _next()
VIEW_TABLE_TYPE = _next()
VIEW_AD_NODE_TYPE = _next()
VIEW_AD_EDGE_TYPE = _next()

# shared types
VIEW_TEXT_TYPE = _next()
VIEW_LEGEND_TYPE = _next()

