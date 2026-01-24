from filter_event_item_delegates import ANY_EVENT
"""Provides regenerate_trace_set."""
def _check_threshold(num_matches, equality, threshold):
    if equality == ">=":
        return num_matches >= threshold
    if equality == ">":
        return num_matches > threshold
    if equality == "<=":
        return num_matches <= threshold
    if equality == "<":
        return num_matches < threshold
    if equality == "==":
        return num_matches == threshold
    if equality == "!=":
        return num_matches != threshold
    raise RuntimeError("bad")

def _has_relationship(gry_trace, from_event, to_event, equality, threshold):

    # find potential nodes
    from_node_indexes = set()
    to_node_indexes = set()
    for node in gry_trace["nodes"]:
        if node["label"] == from_event or from_event == ANY_EVENT:
            from_node_indexes.add(node["id"])
        if node["label"] == to_event or to_event == ANY_EVENT:
            to_node_indexes.add(node["id"])

    # find matches
    num_matches = 0
    for edge in gry_trace["edges"]:
        if edge["from_id"] in from_node_indexes \
                       and edge["to_id"] in to_node_indexes:
            num_matches += 1

    # check against threshold
    return _check_threshold(num_matches, equality, threshold)

def _has_recurrence(gry_trace, event, equality, threshold):

    # find number of matches
    num_matches = 0
    for node in gry_trace["nodes"]:
        if node["label"] == event or event == ANY_EVENT:
            num_matches += 1

    # check against threshold
    return _check_threshold(num_matches, equality, threshold)

def regenerate_trace_set(graphs, relationship_list, recurrence_list, use_or):

    if use_or and (relationship_list or recurrence_list):
        # OR and at least one condition is specified so start with empty set
        matching_indexes = set()
    else:
        # start with all traces
        matching_indexes = set(range(len(graphs)))

    # relationship indexes
    for from_event, to_event, equality, threshold in relationship_list:

        matching_indexes_subset = set()
        for i, graph in enumerate(graphs):
            if "trace" in graph.gry_graph:
                gry_trace = graph.gry_graph["trace"]
                if _has_relationship(gry_trace, from_event,
                                     to_event, equality, threshold):
                    matching_indexes_subset.add(i)

        # accumulate result
        if use_or:
            matching_indexes |= matching_indexes_subset
        else:
            matching_indexes &= matching_indexes_subset

    # recurrence indexes
    for event, equality, threshold in recurrence_list:

        matching_indexes_subset = set()
        for i, graph in enumerate(graphs):
            if "trace" in graph.gry_graph:
                gry_trace = graph.gry_graph["trace"]
                if _has_recurrence(gry_trace, event, equality, threshold):
                    matching_indexes_subset.add(i)

        # accumulate result
        if use_or:
            matching_indexes |= matching_indexes_subset
        else:
            matching_indexes &= matching_indexes_subset

    # cache value
    return matching_indexes

