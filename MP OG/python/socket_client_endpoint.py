from platform import system
from os.path import exists
import socket
from paths_examples import is_bundled
from paths_trace_generator import trace_generator_paths

"""
Interfaces:
  ENDPOINT_NAMES[]
  available_endpoints()
  selected_endpoint()
  select_endpoint(endpoint_name)
  selected_endpoint_info()
"""
# dict of: use_socket, host, port, name
_ENDPOINT = None

# find preferred approach, one of:
#   local trace generator
#   a socket endpoint
# name, host, port, timeout
ENDPOINT_NAMES = ["Inside NPS VPN",
                  "Outside NPS",
                  "localhost",
                  "Local trace generator"]

_SOCKET_ENDPOINTS = [
           ("localhost", "localhost", 6000, 0.1),
           ("Inside NPS VPN", "trace-generator.monterey-phoenix.ern.nps.edu",
            8443, 0.25),
           ("Outside NPS", "3.32.138.226", 6000, 0.5),
                   ]

_ENDPOINT = dict()

# true if connects within timeout
def _connects(host, port, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass

# dict of name:(is_available, use_socket, host, port)
def available_endpoints():
    endpoints = dict()
    # local trace generator
    name = ENDPOINT_NAMES[3]
    endpoint = {"name": name,
                "use_socket": False,
                "host": "no host",
                "port": -1,
                "timeout": 0}
    if exists(trace_generator_paths["trace_generator_root"]):
        endpoint["is_available"] = True
    else:
        endpoint["is_available"] = False
    endpoints[name] = endpoint

    # sockets
    for name, host, port, timeout in _SOCKET_ENDPOINTS:
        endpoint = {"name": name,
                    "use_socket": True,
                    "host": host,
                    "port": port,
                    "timeout": timeout}
        if _connects(host, port, timeout):
            endpoint["is_available"] = True
        else:
            endpoint["is_available"] = False
        endpoints[name] = endpoint

    return endpoints

def select_best_endpoint():
    # default no endpoint
    _ENDPOINT.update({"name": "no endpoint available",
                      "use_socket": True,
                      "host": "Server not available",
                      "port": -1,
                      "timeout": 0,
                      "is_available": False})

    # local trace generator
    if exists(trace_generator_paths["trace_generator_root"]):
        _ENDPOINT.update({"name": ENDPOINT_NAMES[3],
                          "use_socket": False,
                          "host": "no host",
                          "port": -1,
                          "timeout": 0,
                          "is_available": True})

    # one of the sockets
    else:
        for name, host, port, timeout in _SOCKET_ENDPOINTS:
            if _connects(host, port, timeout):
                _ENDPOINT.update({"name": name,
                                  "use_socket": True,
                                  "host": host,
                                  "port": port,
                                  "timeout": timeout,
                                  "is_available": True})


def selected_endpoint():

    # return selection if already defined
    if _ENDPOINT:
        return _ENDPOINT
    else:
        select_best_endpoint()
        return _ENDPOINT

def select_endpoint(endpoint):
    _ENDPOINT.update(endpoint)

def selected_endpoint_info():
    return "Use socket: %s Host: %s Port: %d Name: %s"%(_ENDPOINT["use_socket"],
             _ENDPOINT["host"], _ENDPOINT["port"], _ENDPOINT["name"])

