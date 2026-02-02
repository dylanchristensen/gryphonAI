# starting template for an empty gry graph
def empty_gry_graph():
    gry_graph = dict()

    # background
    gry_graph["box"] = {"is_visible":True, "is_boxed":False}

    # zero or more of these views
    gry_graph["reports"] = list()
    gry_graph["graphs"] = list()
    gry_graph["tables"] = list()
    gry_graph["bar_charts"] = list()
    gry_graph["gantt_charts"] = list()
    gry_graph["activity_diagrams"] = list()

    return gry_graph

