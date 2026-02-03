# logger singleton
def set_logger_targets(statusbar, log_pane):
    global _statusbar
    global _log_pane
    _statusbar = statusbar
    _log_pane = log_pane

def log(log_line):
    _log_pane.appendPlainText(log_line)
    _statusbar.showMessage(log_line)

def clear_log():
    _log_pane.clear()
    _statusbar.clearMessage()

