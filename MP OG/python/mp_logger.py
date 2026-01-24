"""
The logger singleton must be initialized via set_logger_targets else there
will be no output to log pane or status bar and no access to Qt.

Interfaces:
* log(text) logs to log pane and status bar.
* clear_log() clears log pane and status bar.
* begin_timestamps(title) begin a timestamp series, clearing any previous list.
* timestamp(label) take a labeled incremental timestamp.
* show_timestamps() print the timestamp list.
"""
import time
from verbose import verbose

_log_pane = None
_statusbar = None

def set_logger_targets(statusbar, log_pane):
    global _statusbar
    global _log_pane
    _statusbar = statusbar
    _log_pane = log_pane

# log pane and status bar
def log(log_line):
    if _log_pane:
        _log_pane.appendPlainText(log_line)
        _statusbar.showMessage(log_line)
    if verbose():
        print("mp_logger.log:", log_line)

# status bar only
def log_to_statusbar(log_line):
    if _statusbar:
        _statusbar.showMessage(log_line)
    if verbose():
        print("mp_logger.log_to_statusbar:", log_line)

# log pane only
def log_to_pane(log_line):
    if _log_pane:
        _log_pane.appendPlainText(log_line)
    if verbose():
        print("mp_logger.log_to_pane:", log_line)

def clear_log():
    if _log_pane:
        _log_pane.clear()
        _statusbar.clearMessage()

# timestamp support
_start_time = None
_previous_time = None
timestamp_logs = list()

# restart the titled timestamp log with output to pane
def begin_timestamps(title):
    global _start_time
    global _previous_time
    timestamp_logs.clear()
    timestamp_logs.append("Timestamp log for: %s"%title)
    log_to_pane(title)
    _start_time = time.time()
    _previous_time = _start_time

# conclude a named timestamp action with output to pane
def timestamp(label):
    global _start_time
    global _previous_time

    # take current timestamp
    current_time = time.time()
    if _start_time == None:
        print("MP Logger timestamp: Please call begin_timestamps first.")
        _start_time = current_time
        _previous_time = current_time

    # record timestamped event
    event = "%s (%0.2f seconds, total %0.2f seconds)"%(label,
                current_time - _previous_time, current_time - _start_time)
    timestamp_logs.append(event)
    log_to_pane(event)

    # prepare for next timestamp
    _previous_time = current_time

# print timestamp logs to stdout
def show_timestamps():
    if _start_time == None:
        print("No timing results available.")
        return
    for timestamp_log in timestamp_logs:
        print(timestamp_log)
    total = _previous_time-_start_time
    hhmmss = time.strftime('%H:%M:%S', time.gmtime(total))
    print("Total time: %0.2f seconds (%s)"%(total,hhmmss))
    timestamp_logs.clear()

