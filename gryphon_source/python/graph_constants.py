from PySide6.QtWidgets import QGraphicsItem
_type = QGraphicsItem.UserType
def _next():
    global _type
    _type += 1
    return _type

# user-defined QGraphicsItem types
BOX_TYPE = _next()
NODE_TYPE = _next()
NODE_SHADOW_TYPE = _next()
EDGE_TYPE = _next()
EDGE_GRIP_TYPE = _next()
VIEW_BAR_CHART_BARS_TYPE = _next()
VIEW_GANTT_CHART_BARS_TYPE = _next()
VIEW_REPORT_TYPE = _next()
VIEW_GRAPH_NODE_SHADOW_TYPE = _next()
VIEW_GRAPH_NODE_TYPE = _next()
VIEW_GRAPH_EDGE_TYPE = _next()
VIEW_TABLE_TYPE = _next()
VIEW_AD_NODE_TYPE = _next()
VIEW_AD_EDGE_TYPE = _next()

# shared types
EDGE_ANNOTATION_TYPE = _next()
VIEW_TITLE_TYPE = _next()
VIEW_LEGEND_TYPE = _next()

# items grouped by location management
LOCATION_POS = (NODE_TYPE, VIEW_BAR_CHART_BARS_TYPE, VIEW_GANTT_CHART_BARS_TYPE,
                VIEW_REPORT_TYPE, VIEW_GRAPH_NODE_TYPE, VIEW_TABLE_TYPE,
                VIEW_AD_NODE_TYPE, VIEW_TITLE_TYPE, VIEW_LEGEND_TYPE)
LOCATION_BEZIER = (EDGE_TYPE, VIEW_GRAPH_EDGE_TYPE)
LOCATION_AD_EDGE = (VIEW_AD_EDGE_TYPE,)
LOCATION_NOT_MANAGED = (BOX_TYPE, NODE_SHADOW_TYPE, EDGE_GRIP_TYPE,
                        VIEW_GRAPH_NODE_SHADOW_TYPE, EDGE_ANNOTATION_TYPE)
             
