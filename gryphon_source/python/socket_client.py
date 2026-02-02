from platform import system
from os.path import exists
import threading
import socket
import select
import lzma
import json
import traceback
from socket_client_endpoint import selected_endpoint, selected_endpoint_info, \
                                   select_best_endpoint

# connect to host, may throw exception
def _attempt_connect_socket():
    host = selected_endpoint()["host"]
    port = selected_endpoint()["port"]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(selected_endpoint()["timeout"])
    s.connect((host, port))
    return s

def _connect_socket():
    try:
        return _attempt_connect_socket()
    except Exception as e:
        select_best_endpoint()
        return _attempt_connect_socket()

compile_thread = None
check_syntax_thread = None

def _send_check_syntax_request(s, schema_name, mp_code_text):

    # compose the arguments as bytes using \0 parameter separation
    # and lzma compression
    b_arguments = schema_name.encode('utf-8') + b"\0" + \
                  mp_code_text.encode('utf-8')
    b_payload = lzma.compress(b_arguments)

    # the check syntax command
    b_command = b"syntax  "

    # the payload size
    b_size = ("%8d"%len(b_payload)).encode('utf-8')

    # send check syntax request
    s.send(b_command)
    s.send(b_size)
    s.send(b_payload)

def _send_compile_request(s, schema_name, scope, mp_code_text):

    # compose the arguments as bytes using \0 parameter separation
    # and lzma compression
    s_scope = "%d"%scope
    b_arguments = schema_name.encode('utf-8') + b"\0" + \
                  s_scope.encode('utf-8') + b"\0" + \
                  mp_code_text.encode('utf-8')
    b_payload = lzma.compress(b_arguments)

    # the compile command
    b_command = b"compile "

    # the payload size
    b_size = ("%8d"%len(b_payload)).encode('utf-8')

    # send compile request
    s.send(b_command)
    s.send(b_size)
    s.send(b_payload)

def _get_count_response_bytes(thread, count):
    b_response = b''
    interval_counter = 0
    pulse_interval = int(10 / 0.02) # 10 second pulse
    while len(b_response) < count:
        ready = select.select([thread.s], [], [], 0.02)
        if ready[0]:
            b_response += thread.s.recv(count)
        if thread.stop_event.is_set():
            break

        # send watchdog pulse
        interval_counter += 1
        if interval_counter % pulse_interval == 0:
            thread.s.send(b"pulse")
    return b_response

def _get_response_bytes(thread):

    # response size
    b_response_size = _get_count_response_bytes(thread, 8)
    if len(b_response_size) == 0:
        response_size = 0
    else:
        response_size = int(b_response_size.decode('utf-8'))

    # response
    b_response_compressed = _get_count_response_bytes(thread, response_size)
    if len(b_response_size) == 0:
        b_response = b''
    else:
        b_response = lzma.decompress(b_response_compressed)
    return b_response

# do not run this when the compile thread is active
class CheckSyntaxThread(threading.Thread):

    def __init__(self, schema_name, mp_code_text, callback):
        threading.Thread.__init__(self)
        self.schema_name = schema_name
        self.mp_code_text = mp_code_text
        self.callback = callback
        self.stop_event = threading.Event()

    def run(self):
        try:
            self.s = _connect_socket()
            self.s.setblocking(False)
            _send_check_syntax_request(self.s, self.schema_name,
                                       self.mp_code_text)
            b_response = _get_response_bytes(self)
            self.s.close()
            response = b_response.decode('utf-8')
            self.callback(response)
        except Exception as e:
            response = "Socket error: %s, %s"%(selected_endpoint_info(), str(e))
            print(response)
            traceback.print_exc()
            self.callback(response)

class CompileThread(threading.Thread):

    def __init__(self, schema_name, scope, mp_code_text, callback):
        threading.Thread.__init__(self)
        self.s = None
        self.schema_name = schema_name
        self.scope = scope
        self.mp_code_text = mp_code_text
        self.callback = callback
        self.stop_event = threading.Event()

    def run(self):
        try:
            self.s = _connect_socket()
            self.s.setblocking(False)
            _send_compile_request(self.s, self.schema_name,
                                  self.scope, self.mp_code_text)
            b_response = _get_response_bytes(self)
            self.s.close()
            if b_response == b'':
                b_response = b'Cancelled\0{}\0'
            b_status, b_generated_json_text, b_log = b_response.split(b"\0")
            status = b_status.decode('utf-8')
            generated_json = json.loads(b_generated_json_text.decode('utf-8'))
            log_text = b_log.decode('utf-8')
            self.callback(status, generated_json, log_text)
        except Exception as e:
            response = "Socket error: %s, %s"%(selected_endpoint_info(), str(e))
            print(response)
            traceback.print_exc()
            self.callback(response, {}, "")

# do not check syntax if compile is active
def socket_mp_check_syntax(schema_name, mp_code_text, callback):
    global check_syntax_thread
    if compile_thread and compile_thread.is_alive():
        callback("Syntax checking is disabled when trace-generator is running")
        return
    if check_syntax_thread and check_syntax_thread.is_alive():
        check_syntax_thread.stop_event.set()
        check_syntax_thread.join(10)

    check_syntax_thread = CheckSyntaxThread(schema_name, mp_code_text, callback)
    check_syntax_thread.start()

# start compiling, closing the previous socket if a previous compile
# thread was active
def socket_mp_compile(schema_name, scope, mp_code_text, callback):
    global compile_thread
    if compile_thread and compile_thread.is_alive():
        # force close its socket and start a new compile thread
        compile_thread.stop_event.set()
        compile_thread.join(10)

    compile_thread = CompileThread(schema_name, scope, mp_code_text, callback)
    compile_thread.start()

def socket_mp_cancel_compile():
    if compile_thread and compile_thread.is_alive():
        compile_thread.stop_event.set()
        # force close its socket
        try:
            compile_thread.s.close()
        except Exception as e:
            pass

