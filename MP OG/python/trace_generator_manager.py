from PySide6.QtCore import QObject, Signal, Slot
from trace_generator_runner import RunnerThread
from socket_client_endpoint import selected_endpoint
from socket_client import socket_mp_compile, socket_mp_cancel_compile

# use this to signal completion to GUI.  test.py uses a different callback.
class TraceGeneratorCallback(QObject):
    # signal status or "" if okay, generated_json, and any log text.
    signal_compile_response = Signal(str, dict, str,
                                         name='signalCompileResponse')

    def __init__(self):
        super().__init__()

    def send_signal(self, status, generated_json, log_text):
        self.signal_compile_response.emit(status, generated_json, log_text)

class TraceGeneratorManager(QObject):
    """Run the trace-generator."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.runner_thread = None

    # initiate stateful compilation process
    # callback accepts status, json_text, log_text
    def mp_compile(self, schema_name, scope, mp_code_text):
        if selected_endpoint()["use_socket"]:
            # socket
            socket_mp_compile(schema_name, scope, mp_code_text, self.callback)

        else:
            # local trace-generator
            self.runner_thread = RunnerThread(schema_name, scope, mp_code_text,
                                              self.callback)
            self.runner_thread.start()

    def mp_cancel_compile(self):
        if selected_endpoint()["use_socket"]:
            # close socket client's socket
            socket_mp_cancel_compile()

        if self.runner_thread:
            self.runner_thread.mp_cancel_compile()
            # allow time for callback to complete
            self.runner_thread.join(15)

    # clean shutdown
    @Slot()
    def mp_clean_shutdown(self):
        # kill command runner if active
        self.mp_cancel_compile()

        # close socket client's socket
        socket_mp_cancel_compile()

