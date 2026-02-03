from PySide6.QtWidgets import QMenu

"""
Provides the graph pane menu.
"""

def make_graph_pane_menu(gui_manager):

    menu = QMenu("&Graph pane")

    menu.addAction(gui_manager.graphs_manager.action_show_hidden_components)
    menu.addAction(gui_manager.graphs_manager
                   .action_show_hidden_components_all_graphs)
    menu.addSeparator()
    menu.addAction(gui_manager.action_zoom_in)
    menu.addAction(gui_manager.action_zoom_out)
    return menu

