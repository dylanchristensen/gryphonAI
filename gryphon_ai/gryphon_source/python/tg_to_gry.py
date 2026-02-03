# convert .tg to .gry for standard Gryphon import
# ref https://gitlab.nps.edu/monterey-phoenix/trace-generator/-/blob/master/Documentation/JSON_file_structure.pdf

"""
One graph holds one trace and lists of views.
The global view is at graphs[0].  The remaining views follow.
The data structure for all graph objects are homogeneous.
The graphs data structure can be represented directly in JSON.
"""

from edge_bezier_placer import EdgeBezierPlacer
from settings_manager import settings
from verbose import verbose

# placed box 
def _placed_box(should_show):
    return {"is_visible":True, "is_boxed":should_show, "x":0, "y":0}

# box that needs to be placed
def _box(should_show):
    return {"is_visible":True, "is_boxed":should_show}

# remove underscores
def _strip_underscore(text_item):
    return text_item.replace('_'," ")
def _strip_underscores(text_items):
    return [item.replace('_'," ") for item in text_items]
def _maybe_strip_underscores(items):
    result = list()
    for item in items:
        if type(item) == str:
            result.append(item.replace("_", " "))
        else:
            result.append(item)
    return result

# starting template for a graph
def empty_graph():
    graph = dict()

    # background
    graph["box"] = _placed_box(settings["generation_background_use_border"])

    # zero or more of these views
    graph["says"] = list()
    graph["reports"] = list()
    graph["graphs"] = list()
    graph["tables"] = list()
    graph["bar_charts"] = list()
    graph["gantt_charts"] = list()
    graph["activity_diagrams"] = list()
    graph["user_annotations"] = list()

    return graph

# (20 report)
def _view_report(view_object):
    return {"title":_strip_underscore(view_object[0]),
            "lines":view_object[1:],
            "box":_box(settings["generation_reports_use_border"]),
           }

# (22 graph)
def _view_graph(view_object):

    # nothing has x,y until force_directed_layout is invoked
    title = {"text":view_object[0]}
    nodes = list()
    edges = list()
    index = 0
    graph = {"title":title, "nodes":nodes, "edges":edges,
             "box":_box(settings["generation_graphs_use_border"]),
            }
    for tg_node in view_object[1]: # (23)
        # prepare graph node name without underscores
        nodes.append({"id":tg_node[0], "label":_strip_underscore(tg_node[1])})
    for tg_edge_directed in view_object[2]:
        edges.append({"from_id":tg_edge_directed[0],
                      "to_id":tg_edge_directed[1],
                      "label":tg_edge_directed[2],
                      "type":"directed"})
    for tg_edge_undirected in view_object[3]:
        edges.append({"from_id":tg_edge_undirected[0],
                      "to_id":tg_edge_undirected[1],
                      "label":tg_edge_undirected[2],
                      "type":"undirected"})
    return graph

# (32)
def _view_table(view_object):
    return {"title":{"text":_strip_underscore(view_object["title"])},
            "data":{"headers":_strip_underscores(view_object["tabs"]),
                       "rows":[_maybe_strip_underscores(row)
                                       for row in view_object["rows"]],
                   },
            "box":_box(settings["generation_tables_use_border"]),
           }

# (33 bar)
# (34 Gantt)
def _view_bar_or_gantt_chart(view_object):
    # prepare all titles and labels without underscores

    # x axis text is provided twice
    if view_object["tabs"][0] != view_object["X_AXIS"]:
        print("tg_to_gry view bar or gantt unexpected inequality",
                        view_object["tabs"][0], view_object["X_AXIS"])

    return {"title":{"text":_strip_underscore(view_object["title"])},
            "legend":{"names":_strip_underscores(
                               [name for name in view_object["tabs"][1:]])},
            "plot":{"axis_title":_strip_underscore(view_object["X_AXIS"]),
                    "tick_labels":_strip_underscores([row[0]
                                         for row in view_object["rows"]]),
                    "tick_values":[row[1:] for row in view_object["rows"]],
                   },
            "box":_box(settings["generation_charts_use_border"]),
           }

# (35)
def _view_activity_diagram(view_object):
    nodes = list()
    edges = list()
    title = {"text":view_object[0]}
    index = 0
    gry_ad = {"title":title, "nodes":nodes, "edges":edges,
              "box":_box(settings["generation_ad_use_border"]),
              }

    # nodes, composition depends on node type
    for tg_node in view_object[1]: # (37)
        node_type = tg_node[0]
        node_id = tg_node[1]

        # adjust trace-generator x for bar node type
        tg_x = tg_node[2]
        if node_type == "b":
            tg_x = (tg_node[4] - 1) / 2

        gry_node = {"node_type":tg_node[0],
                    "node_id":tg_node[1],
                    "x":tg_x * settings["ad_h_spacing"],
                    "y":tg_node[3] * settings["ad_v_spacing"],
                   }
        if len(tg_node) == 5:
            gry_node["label"] = _strip_underscore(tg_node[4])
        elif len(tg_node) == 6:
            gry_node["bar_width"] = tg_node[4]
            gry_node["label"] = _strip_underscore(tg_node[5])
        nodes.append(gry_node)

    # edges
    for tg_edge in view_object[2]:
        edges.append({"from_id":tg_edge[0],
                      "to_id":tg_edge[1],
                     })

    return gry_ad

def _add_view_object(view_object, gry_graph):
    if verbose():
        print("tg_to_gry _add_view_object", view_object)
    if "REPORT" in view_object:
        gry_graph["reports"].append(_view_report(view_object["REPORT"]))
    if "GRAPH" in view_object:
        gry_graph["graphs"].append(_view_graph(view_object["GRAPH"]))
    if "TABLE" in view_object:
        gry_graph["tables"].append(_view_table(view_object["TABLE"]))
    if "BAR_CHART" in view_object and "ROTATE" in view_object["BAR_CHART"]:
        tg_chart = _view_bar_or_gantt_chart(view_object["BAR_CHART"])
        rotate = view_object["BAR_CHART"]["ROTATE"]
        if rotate == 0: # BAR_CHART
            gry_graph["bar_charts"].append(tg_chart)
        elif rotate == 1: # GANTT_CHART
            gry_graph["gantt_charts"].append(tg_chart)
        else:
            print("unrecognized BAR_CHART mode: %d"%rotate)
    if "AD" in view_object: # Activity Diagram
        gry_graph["activity_diagrams"].append(_view_activity_diagram(
                                             view_object["AD"]))

def _trace_edge(tg_edge, relation, label, nodes, placer):
    gry_edge = dict()
    from_id = tg_edge[1]
    gry_edge["from_id"] = from_id
    gry_edge["relation"] = relation
    to_id = tg_edge[0]
    gry_edge["to_id"] = to_id
    gry_edge["label"] = label
    gry_from_node = nodes[from_id]
    gry_to_node = nodes[to_id]
    ep1_x, ep1_y, ep2_x, ep2_y = placer.place_cubic_bezier_points(
                  from_id, gry_from_node["x"], gry_from_node["y"], 
                  to_id, gry_to_node["x"], gry_to_node["y"])
    gry_edge["ep1_x"] = ep1_x
    gry_edge["ep1_y"] = ep1_y
    gry_edge["ep2_x"] = ep2_x
    gry_edge["ep2_y"] = ep2_y
    return gry_edge

"""
Actions:
  * Reorganize to hierarchaical homogeneous form.
  * Rescale x, y to pixels, accounting for SAY spacing in y.
  * Remove underscores from many of the fields, e.g. trace event names,
  *                    graph node names, activity diagram node names.
  * Return gry_graphs
"""
def tg_to_gry_graphs(tg_data):
    # the list of global graph at [0] and the traces starting at [1]
    gry_graphs = list()

    # global views for global graph[0]
    gry_graph = empty_graph()
    gry_graphs.append(gry_graph)
    if "GLOBAL" in tg_data:
        tg_global = tg_data["GLOBAL"]
        gry_graph["global_mark"] = tg_global[0]

        # tg json structure doc says a list of say messages is at [1] but
        # there is no say in example 42 so check type instead
        if type(tg_global[1]) == list:
            gry_graph["say"] = tg_global[1] # list
        for view_object in tg_global[1:]:
            if type(view_object) == dict:
                _add_view_object(view_object, gry_graph)

    # traces and trace views for graphs [1:]
    if "traces" in tg_data:
        tg_traces = tg_data["traces"]
    else:
        tg_traces = []

    if verbose():
        print("tg_to_gry.tg_to_gry_graph begin, size %d"%len(tg_traces))

    for tg_trace in tg_traces:
        # start with empty graph template
        gry_graph = empty_graph()
        gry_graphs.append(gry_graph)

        # trace
        gry_trace = {"layout":"default"}
        gry_graph["trace"] = gry_trace
        gry_trace["box"] = _placed_box(settings["generation_traces_use_border"])

        # item 0: trace mark, "U" or "M"
        gry_trace["mark"] = tg_trace[0]

        # item 1: trace probability
        gry_trace["probability"] = tg_trace[1]

        # item 2: event list of nodes
        tg_nodes = tg_trace[2] # event list
        y_extra_say = 0
        nodes = list()
        _nodes = dict() # for placing edges
        gry_trace["nodes"] = nodes
        for tg_node in tg_nodes: # event in event list

            # prepare event name without underscores
            event_name = _strip_underscore(tg_node[0])

            # compute x and y
            x=tg_node[3] * settings["trace_node_h_spacing"]
            y=tg_node[4] * settings["trace_node_v_spacing"]
            if tg_node[1] == "T": # SAY
                # spread out SAY boxes more
                y_extra_say += 22 * (len(event_name)//20)
                y += y_extra_say

            gry_node = dict()
            gry_node["id"] = tg_node[2]
            gry_node["type"] = tg_node[1]
            gry_node["label"] = event_name
            gry_node["x"] = x
            gry_node["y"] = y
            gry_node["hide"] = False
            gry_node["collapse"] = False
            gry_node["collapse_below"] = False

            nodes.append(gry_node)
            _nodes[gry_node["id"]] = gry_node

        # edges
        edges = list()
        placer = EdgeBezierPlacer()

        # item 3: IN relation edges
        tg_in_edges = tg_trace[3]
        gry_trace["edges"] = edges
        for tg_edge in tg_in_edges:
            edges.append(_trace_edge(tg_edge, "IN", "", _nodes, placer))

        # item 4: FOLLOWS relation edges
        tg_follows_edges = tg_trace[4]
        for tg_edge in tg_follows_edges:
            edges.append(_trace_edge(tg_edge, "FOLLOWS", "", _nodes, placer))

        # items 5...: the user-defined named relations or else VIEWS
        for type_specific_element in tg_trace[5:]:
            if isinstance(type_specific_element, list):
                # user defined relation edge
                label = type_specific_element[0]
                for tg_edge in type_specific_element[1:]:
                    edges.append(_trace_edge(tg_edge, "USER_DEFINED",
                                             label, _nodes, placer))

            elif isinstance(type_specific_element, dict) \
                       and len(type_specific_element) == 1 \
                       and "VIEWS" in type_specific_element:
                # view
                for view_object in type_specific_element["VIEWS"]:  # 17
                    _add_view_object(view_object, gry_graph)

            else:
                print("Unexpected input:", type_specific_element)

    if verbose():
        print("tg_to_gry.tg_to_gry_graph end")
    return gry_graphs

