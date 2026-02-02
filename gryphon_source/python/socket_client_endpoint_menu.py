from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtCore import Slot
from socket_client_endpoint import ENDPOINT_NAMES, available_endpoints, \
                                 selected_endpoint, select_endpoint

"""
Provides the socket client endpoint menu
"""

class SocketClientEndpointMenu(QMenu):
    def __init__(self):
        super().__init__("&MP Gryphon Server")

        # actions
        self.action_endpoints = dict()
        self.endpoint_group = QActionGroup(self)
        for endpoint_name in ENDPOINT_NAMES:
            action = QAction(endpoint_name, self)
            action.setCheckable(True)
            self.action_endpoints[endpoint_name] = action
            self.addAction(action)
            self.endpoint_group.addAction(action)
        self.endpoint_group.triggered.connect(self._set_endpoint)
        self.aboutToShow.connect(self._about_to_show)

    @Slot()
    def _about_to_show(self):
        # enable workable endpoints
        self.endpoints = available_endpoints()
        for endpoint_name in ENDPOINT_NAMES:
            action = self.action_endpoints[endpoint_name]
            action.setChecked(False)
            action.setEnabled(self.endpoints[endpoint_name]["is_available"])

        # select the checked endpoint
        endpoint_name = selected_endpoint()["name"]
        if endpoint_name in self.action_endpoints.keys():
            self.action_endpoints[endpoint_name].setChecked(True)

    @Slot()
    def _set_endpoint(self):
        endpoint_name = self.endpoint_group.checkedAction().text()
        endpoint = self.endpoints[endpoint_name]
        select_endpoint(endpoint)

