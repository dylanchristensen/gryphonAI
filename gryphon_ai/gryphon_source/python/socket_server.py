#!/usr/bin/env python3

import os
import threading
from os import makedirs
from os.path import exists
from sys import exit
from argparse import ArgumentParser
import socket
import lzma
import json
import traceback
from trace_generator_runner import RunnerThread
from mp_code_syntax_checker import SyntaxCheckerThread
from paths_trace_generator import trace_generator_paths

PORT = 6000 # must match socket_client

def _get_client_command(connection):
    b_command = connection.recv(8)
    b_size = connection.recv(8)

    # get payload
    size = int(b_size)
    bytes_received = 0
    b_data = b''
    while bytes_received < size:
        more = min(size - bytes_received, 2048)
        chunk = connection.recv(more)
        b_data += chunk
        bytes_received += len(chunk)

    b_arguments = lzma.decompress(b_data)
    return b_command, b_arguments

def _bytes_to_compile_arguments(b_arguments):
    # convert b_arguments into argument list
    b_schema_name, b_scope, b_mp_code_text = b_arguments.split(b"\0")
    schema_name = b_schema_name.decode('utf-8')
    scope = int(b_scope)
    mp_code_text = b_mp_code_text.decode('utf-8')
    return schema_name, scope, mp_code_text

def _bytes_to_check_syntax_arguments(b_arguments):
    # convert b_arguments into argument list
    b_schema_name, b_mp_code_text = b_arguments.split(b"\0")
    schema_name = b_schema_name.decode('utf-8')
    mp_code_text = b_mp_code_text.decode('utf-8')
    return schema_name, mp_code_text

def _compile_response_to_bytes(status, generated_json_text, log):
    b_response = status.encode('utf-8') + b"\0" + \
                 generated_json_text.encode('utf-8') + b"\0" + \
                 log.encode('utf-8')
    return b_response

def _check_syntax_response_to_bytes(status):
    b_response = status.encode('utf-8')
    return b_response

def _send_response(connection, b_response):
    payload = lzma.compress(b_response)

    # the size of the payload as an 8-byte ASCII decimal value
    # prefixed with spaces
    b_size = ("%8d"%len(payload)).encode('utf-8')

    # return size of payload + payload
    connection.send(b_size)
    connection.sendall(payload)

# done when thread is done or when allowed time is exceeded
def _wait_until_check_syntax_done(thread):
    # this should be fast so the client need not pulse
    thread.join(5)
    if thread.is_alive():
        raise RuntimeError("unexpected long syntax check aborted")

# done when thread is done or when client's pulse stops
def _wait_until_compile_done(thread, connection):

    while True:
        # wait 15 seconds, note that the client pulses every 10 seconds
        thread.join(15)
        if not thread.is_alive():
            # normal completion
            break
        b_response = connection.recv(1024)
        if not b_response: 
            # no client pulse
            thread.mp_cancel_compile()

class ServeThread(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.is_done_flag = threading.Event()

    def run(self):
        with self.connection:
            print("Serving %s, %d"%(self.address[0],self.address[1]))
            b_command, b_arguments = _get_client_command(self.connection)
            print("command '%s', size %d"%(b_command.decode('utf-8'),
                                             len(b_arguments)))

            # execute requested command
            if b_command == b"compile ":
                schema_name, scope, mp_code_text = \
                                   _bytes_to_compile_arguments(b_arguments)
                runner_thread = RunnerThread(schema_name, scope, mp_code_text,
                                             self._compile_callback)
                runner_thread.start()
                _wait_until_compile_done(runner_thread, self.connection)
            elif b_command == b"syntax  ":
                schema_name, mp_code_text = \
                              _bytes_to_check_syntax_arguments(b_arguments)
                syntax_checker_thread = SyntaxCheckerThread(schema_name,
                                   mp_code_text, self._check_syntax_callback)
                syntax_checker_thread.start()
                syntax_checker_thread.join(5)
                if syntax_checker_thread.is_alive():
                    raise RuntimeError("unexpected long syntax check aborted")
                _wait_until_check_syntax_done(syntax_checker_thread)
            else:
                s_command = b_command.decode('utf-8')
                raise ValueError("invalid command '%s'" % s_command)

    def _compile_callback(self, status, generated_json, log_text):
        generated_json_text = json.dumps(generated_json)
        b_response = _compile_response_to_bytes(
                                      status, generated_json_text, log_text)
        _send_response(self.connection, b_response)
        self.is_done_flag.set()

    def _check_syntax_callback(self, status):
        b_response = _check_syntax_response_to_bytes(status)
        _send_response(self.connection, b_response)
        self.is_done_flag.set()

# main
if __name__=="__main__":

    # parse server port from input
    parser = ArgumentParser(prog='socket_server.py',
                 description = "Start the Monterey Phoenix (MP) Gryphon " \
                               "Trace Generator Server on port %d"%PORT)
    args = parser.parse_args()

    # make sure trace-generator is ready
    if not exists(trace_generator_paths["rigal_rc"]):
        print("rc does not exist at '%s'.  Did you run "
              "trace-generator's make?"%RIGAL_RC)
        exit(1)

    # open socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", PORT)) # "" means all available interfaces
        s.listen(5)        # number of requests at a time

        # serve clients
        print("Starting Gryphon Trace Generator Server on port %d"%PORT)
        while True:
            try:
                connection, address = s.accept() # block until available
                _thread = ServeThread(connection, address)
                _thread.start()
            except Exception as e:
                traceback.print_exc()
