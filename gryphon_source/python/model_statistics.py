from version_file import VERSION
from collections import defaultdict
from hashlib import blake2b # supposed to be fast
from mp_code_parser import mp_code_event_dict, mp_code_schema
from verbose import verbose

_EVENT_TYPES = ["root", "composite", "atomic"]

def _model_metadata(graphs_manager):
    schema = mp_code_schema(graphs_manager.mp_code)
    lines = list()
    lines.append("MP Gryphon %s"%VERSION)
    lines.append("Schema: %s"%schema)
    lines.append("Scope: %s"%graphs_manager.scope)
    lines.append("")
    return lines

def _event_list(graphs_manager):

    # events from graphs traces
    graph_traces = set()
    for graph_item in graphs_manager.graphs:

        if "trace" in graph_item.gry_graph:
            for node in graph_item.gry_graph["trace"]["nodes"]:
                graph_traces.add(node["label"])

    # make missing events list
    missing_events_tuples = list()
    event_dict = mp_code_event_dict(graphs_manager.mp_code)
    for event_type in _EVENT_TYPES:
        for event in event_dict[event_type]:
            if not event in graph_traces:
                missing_events_tuples.append((event_type, event))

    return missing_events_tuples

# find indexes of similar traces, return a dict of (hash, set of index)
def _trace_indexes_dict(graphs):
    indexes_dict = defaultdict(set)

    for i, graph in enumerate(graphs):
        if "trace" in graph.gry_graph:
            trace = graph.gry_graph["trace"]
            trace_hash = blake2b(digest_size=8) # 8 bytes should be enough

            # node hash: id, label, type
            for node in trace["nodes"]:
                text = "%d%s%s"%(node["id"], node["label"], node["type"])
                trace_hash.update(str.encode(text))

            # edge hash: from_id, to_id, label, relation
            for edge in trace["edges"]:
                text = "%d%d%s%s"%(edge["from_id"], edge["to_id"],
                                   edge["label"], edge["relation"])
                trace_hash.update(str.encode(text))

            indexes_dict[trace_hash.digest()].add(i)
    return indexes_dict

def _no_traces(graphs):
    for graph in graphs:
        if "trace" in graph.gry_graph:
            # trace found
            return False

    # no traces
    return True

# add the sorted list of sorted lists of trace indexes for model_statistics
def _identical_traces(graphs):

    # find indexes of similar traces, return a dict of (hash, set of index)
    indexes_dict = defaultdict(set)
    for i, graph in enumerate(graphs):
        if "trace" in graph.gry_graph:
            trace = graph.gry_graph["trace"]
            trace_hash = blake2b(digest_size=8) # 8 bytes should be enough

            # node hash: id, label, type
            for node in trace["nodes"]:
                text = "%d%s%s"%(node["id"], node["label"], node["type"])
                trace_hash.update(str.encode(text))

            # edge hash: from_id, to_id, label, relation
            for edge in trace["edges"]:
                text = "%d%d%s%s"%(edge["from_id"], edge["to_id"],
                                   edge["label"], edge["relation"])
                trace_hash.update(str.encode(text))

            indexes_dict[trace_hash.digest()].add(i)

    # remove singles
    identical_traces_list = list()
    for _key, value in indexes_dict.items():
        if len(value) > 1:
            identical_traces_list.append(list(value))
    identical_traces_list.sort(key=lambda x:x[0])
    return identical_traces_list

"""
Returns schema, scope, warnings, statistics_text.
Warnings is a set of warning titles for traces and events:
    Traces: no_traces, identical_traces
    Events: missing_events
"""
def model_statistics(graphs_manager):
    # schema and scope
    schema = mp_code_schema(graphs_manager.mp_code)
    scope = graphs_manager.scope

    # warnings and detailed statistics text
    warnings = set()
    lines = list()

    # model metadata
    lines.extend(_model_metadata(graphs_manager))

    # missing events
    event_list_tuples = _event_list(graphs_manager)
    lines.append("Missing events:")
    if event_list_tuples:
        warnings.add("missing_events")
        for event_type, event in event_list_tuples:
            lines.append("%s: %s"%(event_type, event))
    else:
        lines.append("All events are acounted for.")
    lines.append("")

    # no traces
    if _no_traces(graphs_manager.graphs):
        warnings.add("no_traces")

    # identical traces
    lines.append("Identical traces:")
    identical_traces_list = _identical_traces(graphs_manager.graphs)
    if identical_traces_list:
        warnings.add("identical_traces")
        for trace_list in identical_traces_list:
            lines.append("(%s)"%", ".join(["%d"%x for x in trace_list]))
    else:
        lines.append("There are no identical traces.")
    lines.append("")

    # all events from mp code traces
    event_dict = mp_code_event_dict(graphs_manager.mp_code)
    lines.append("Events (informational):")
    for event_type in _EVENT_TYPES:
        for event in event_dict[event_type]:
            lines.append("%s: %s"%(event_type, event))
    lines.append("")

    # optional diagnostics
    if verbose():
        print("schema: %s"%event_dict["schema"])
        for event_type in _EVENT_TYPES:
            for event in event_dict[event_type]:
                print("%s: %s"%(event_type, event))

    return schema, scope, warnings, "\n".join(lines)

