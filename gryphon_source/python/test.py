#!/usr/bin/env python3
"""This script tests the trace-generator parser and view rendering systems
   by running each example and exporting each view into .svg files.
"""

import sys
import signal
import hashlib
from os import environ, remove
from glob import glob
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from time import time, strftime, gmtime
from os import makedirs
from os.path import join, normpath, dirname, split
import json
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QApplication
from version_file import VERSION
import resources_rc
from settings import settings
from mp_code_parser import mp_code_event_dict
from export_trace import export_trace
from trace_generator_manager import TraceGeneratorManager
from mp_json_io_manager import read_mp_code_file
from tg_to_gry import tg_to_gry_graphs
from graph_item import GraphItem

_TEST_GRAPHS_DIR = "_test_graphs"
_TEST_DATA_DIR = "_test_data"

COLUMN_TITLES = "test, filename, mp_md5_hash, tg_md5_hash, gry_md5_hash, " \
                "schema_name, scope, time, " \
                "traces, trace_marks, trace_nodes, trace_edges, " \
                "trace_in, trace_follows, trace_user_defined, " \
                "trace_probability_sum, " \
                "activity_diagrams, bar_charts, gantt_charts, " \
                "graphs, reports, tables"

def _file_md5(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        md5 = hashlib.md5(data).hexdigest()
        return "%s..."%(md5[:8])

# report one test result
def report_one(i, mp_code_filename, mp_code_text, schema_name, scope, run_time,
               status, generated_json, log_text, f):

    # print lots of stuff if bad and be done
    if status:
        if status == "trace-generation aborted":
            error_text = "%d, %s, timed out in  %.1f seconds"%(
                                             i, mp_code_filename, run_time)
        else:
            error_text = "%d, %s\n%s\nError: %s"%(
                                      i, mp_code_filename, log_text, status)
        print(error_text)
        print(error_text, file=f)
        return

    # output .tg
    tg_outfile = join(_TEST_DATA_DIR, "%s.tg"%schema_name)
    with open(tg_outfile, "w", encoding='utf-8') as tg_f:
        json.dump(generated_json, tg_f, indent=4, sort_keys=True)

    # get gry data
    gry_graphs = tg_to_gry_graphs(generated_json)

    # output .gry, must match gry_data in gui_manager.py
    if "traces" in gry_graphs and len(gry_graphs["traces"]) > 0:
        selected_graph_index = 1
    else:
        selected_graph_index = 0
    gry_data = {
           "graphs":gry_graphs,
           "mp_code_current":mp_code_text,
           "mp_code_runtime":mp_code_text,
           "scope":scope,
           "selected_graph_index":selected_graph_index,
           "settings":settings,
               }
    gry_outfile = join(_TEST_DATA_DIR, "%s.gry"%schema_name)
    with open(gry_outfile, "w", encoding='utf-8') as gry_f:
        json.dump(gry_data, gry_f, indent=4, sort_keys=True)

    # log the test as CSV
    num_traces = len(gry_graphs) - 1
    num_trace_marks = 0
    num_trace_nodes = 0
    num_trace_edges = 0
    num_trace_in_relations = 0
    num_trace_follows_relations = 0
    num_trace_user_defined_relations = 0
    trace_probability_sum = 0
    num_activity_diagrams = 0
    num_bar_charts = 0
    num_gantt_charts = 0
    num_graphs = 0
    num_reports = 0
    num_tables = 0

    for graph in gry_graphs:

        if "trace" in graph:
            if graph["trace"]["mark"] == "M":
                num_trace_marks += 1
            num_trace_nodes += len(graph["trace"]["nodes"])
            num_trace_edges += len(graph["trace"]["edges"])
            for edge in graph["trace"]["edges"]:
                relation = edge["relation"]
                if relation == "IN":
                    num_trace_in_relations += 1
                elif relation == "FOLLOWS":
                    num_trace_follows_relations += 1
                elif relation == "USER_DEFINED":
                    num_trace_user_defined_relations += 1
                else:
                    raise RuntimeError("bad")
            trace_probability_sum += graph["trace"]["probability"]

        num_activity_diagrams += len(graph["activity_diagrams"])
        num_bar_charts += len(graph["bar_charts"])
        num_gantt_charts += len(graph["gantt_charts"])
        num_graphs += len(graph["graphs"])
        num_reports += len(graph["reports"])
        num_tables += len(graph["tables"])

    # MD5 hashcodes
    md5_mp = _file_md5(mp_code_filename)
    md5_tg = _file_md5(tg_outfile)
    md5_gry = _file_md5(gry_outfile)
             
    # log row
    row = "%d, %s, %s, %s, %s, %s, %d, %.1f, " \
          "%d, %d, %d, %d, %d, %d, %d, %f, " \
          "%d, %d, %d, %d, %d, %d"%(
                   i, mp_code_filename, md5_mp, md5_tg, md5_gry,
                   schema_name, scope, run_time,
                   num_traces, num_trace_marks, num_trace_nodes,
                   num_trace_edges, num_trace_in_relations,
                   num_trace_follows_relations,
                   num_trace_user_defined_relations,
                   trace_probability_sum,
                   num_activity_diagrams, 
                   num_bar_charts, num_gantt_charts,
                   num_graphs, num_reports,
                   num_tables)
    print(row, file=f)

    # make the graphs
    for graph_index, gry_graph in enumerate(gry_graphs):
        outfile = join(_TEST_GRAPHS_DIR, "%s_%03d%s" % (schema_name,
                             graph_index, settings["export_image_format"]))
        graph = GraphItem(gry_graph)
        status = export_trace(outfile, graph, graph_index, scope, application)
        if status:
            raise RuntimeError("Error creating trace file %s, %s"%(
                                                outfile, graph))

class Tester():
    def __init__(self, args):
        self.args = args

        # clean path for exported data
        makedirs(_TEST_DATA_DIR, exist_ok=True)
        old_tgs = glob("%s/*.tg"%_TEST_DATA_DIR)
        for old_tg in old_tgs:
            remove(old_tg)
        old_grys = glob("%s/*.gry"%_TEST_DATA_DIR)
        for old_gry in old_grys:
            remove(old_gry)

        # clean path for exported graphs
        makedirs(_TEST_GRAPHS_DIR, exist_ok=True)
        old_graphs = glob("%s/*.svg"%_TEST_GRAPHS_DIR)
        for old_graph in old_graphs:
            remove(old_graph)

        # the trace generator manager
        self.trace_generator_manager = TraceGeneratorManager(self.callback)

        # be ctrl-c friendly
        signal.signal(signal.SIGINT, self.make_ctrl_c_closure_function())

        # state
        logfile_timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        logfile_filename = "_test_log_%s.csv"%logfile_timestamp
        path_to_models = args.path_to_models
        filenames = sorted(glob("%s/**/*.mp"%path_to_models, recursive=True))
        self.scope = args.scope
        self.timeout = args.timeout
        index = args.index

        # log output
        with open(logfile_filename, "w", buffering=1,
                                             encoding='utf-8') as self.f:

            # print test information
            print("Filename: %s"%logfile_filename, file=self.f)
            print("Gryphon version: %s"%VERSION, file=self.f)
            _parameters = "Directory: %s\nScope: %s\nTime limit: " \
                    "%d seconds\n"%(path_to_models, self.scope, self.timeout)
            print(_parameters)
            print(_parameters, file=self.f)
            print(COLUMN_TITLES, file=self.f)

            # run one or all tests
            if index:
                self.test_one(index, filenames[index-1])
            else:
                for i in range(len(filenames)):
                    print("Testing %d of %d: %s"%(i+1, len(filenames),
                                                  filenames[i]))
                    self.test_one(i+1, filenames[i])

    def test_one(self, i, mp_code_filename):

        # save state for callback
        self.i = i
        self.mp_code_filename = mp_code_filename

        # read mp code
        status, self.mp_code_text = read_mp_code_file(mp_code_filename)
        if status:
            error = "Error in file %s: %s"%(mp_code_filename, status)
            print(error)
            print(error, file=self.f)
            return

        # schema_name
        event_dict = mp_code_event_dict(self.mp_code_text)
        self.schema_name = event_dict["schema"]

        # start time
        self.start_time = time()

        # start trace generation
        self.trace_generator_manager.mp_compile(self.schema_name, self.scope,
                                                self.mp_code_text)

        # Wait for completion else time it out.  It will call callback
        # if it finishes first, else timeout will stop the run and send
        # info to callback indicating the abort.
        self.trace_generator_manager.runner_thread.join(self.timeout)
        if self.trace_generator_manager.runner_thread.is_alive():
            # force quit
            self.trace_generator_manager.mp_cancel_compile()

        # callback will take it from here
        pass

    def callback(self, status, generated_json, log_text):

        # run time
        run_time = time() - self.start_time

        # generate report for this run
        report_one(self.i, self.mp_code_filename,
                   self.mp_code_text, self.schema_name,
                   self.scope, run_time,
                   status, generated_json, log_text,
                   self.f)

    # enable graceful exit by Ctrl C
    def make_ctrl_c_closure_function(self):
        # signal handler for signal.signal
        def ctrl_c_closure_function(_signal, _frame):
            print("Ctrl C exit")
            self.trace_generator_manager.mp_cancel_compile()
#            # allow 10 seconds for clean closure
#            self.trace_generator_manager.runner_thread.join(10)
        return ctrl_c_closure_function

# main
if __name__ == "__main__":

    # attempt to reduce Qt warnings
    environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    # default models
    default_path_to_models = normpath(join(dirname(__file__),
                              "..", "..", "preloaded-examples", "models"))

    # args
    parser = ArgumentParser(description="Gryphon test tool.",
                            formatter_class = ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path_to_models", type=str,
                        default = default_path_to_models,
                        help="The path containing the test files.")
    parser.add_argument("-i", "--index", type=int, default=0,
                        help="The index of a single file to test "
                             "or 0 to test all files.")
    parser.add_argument("-s", "--scope", type=int, default=1,
                        help="The scope to run at.")
    parser.add_argument("-t", "--timeout", type=int, default=60,
                        help="Timeout a run after this many seconds.")
    args = parser.parse_args()

    # create the Qt application
    application = QApplication(sys.argv)

    # test
    Tester(args)
    print("Done.")

