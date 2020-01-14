#!/usr/bin/python3

# =============================================== #
# LanTalk Client
# License: GPL-3.0
# Maintainer: TR_SLimey <tr_slimey@protonmail.com>
# Description: Configurable python3 scripts
# (server & client) for real-time, encrypted
# messaging on a Local Area Network
# (and outside of it) using HTTP(S).
# =============================================== #

#
# Dependencies
#

import json
import threading
import tkinter as tk
import http.client
import socket
import time

#
# Define constants
#

LOG_LEVEL = 0
LOG_LEVEL_NAMES = ["DBUG", "INFO", "WARN", "ERRO"]

#
# Define functions
#


def log(level, message):
    """Log messages to the console if they have the required log level."""
    global_log_level = LOG_LEVEL
    if level > len(LOG_LEVEL_NAMES)-1 or level < 0:
        # If the log level is invalid, ignore (for example, after an update)
        return
    # If the LogLevel is lower than the message's, print the message
    if level >= int(global_log_level):
        print("[ {} ] < {} > | {}".format(LOG_LEVEL_NAMES[level],
              time.strftime("%d/%m/%Y %H:%M:%S"), message))

#
# GUI class
#


class Client():
    """
    The main class of the LanTalk client.

    This class handles the GUI and communication with the server.
    """

    def __init__(self):
        """
        Create windows and initialise class properties.

        Creates a dict of all windows in the GUI and initialises class
        properties such as:
            self.master (main window)
            self.current_widgets (dict of widgets on current window)
            self.available_servers (list of servers the user can connect to)
        """
        # Init class properties
        self.master = tk.Tk()  # The main window
        # A dict of all the widgets currently displayed with names as keys
        self.current_widgets = {}
        # A list of servers which the user can connect to
        self.available_servers = []

        # Define the different windows and what properties they have
        self.windows = {
            # Default basic window without any widgets. Only exists so the
            # window can easily be reset between changes
            "DEFAULT": {
                "title": "LanTalk Client",
                "size": "450x450",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                # 2D dict of widgets. Lists contain:
                # [widget_object_creator, placing_method], for example:
                # [lambda: tk.Button(text="Example"),
                # lambda widget: widget.grid(row=1, column=1)].
                # The lambda is nescessary before the widget object so that a
                # new object is created every time, otherwise there are errors
                "widgets": {
                },
                # List of functions to run after creating the GUI and widgets
                "after_widget_creation_functions": [
                ],
                # List of threads which should be started with this window
                "threads": [
                ],
            },
            # Server finder dialog allowing the user to select and
            # connect to a server
            "SERVER_FIND": {
                "title": "LanTalk Client - Server Finder",
                "size": "450x450",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                "widgets": {
                    "indicator_label": [
                        lambda: tk.Label(self.master, text="Searching for local servers...\nFound: {}", background="#777777"),
                        lambda w: w.grid(row=0, column=0, rowspan=100, columnspan=400, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "server_list_box": [
                        lambda: tk.Listbox(self.master, background="#888888"),
                        lambda w: w.grid(row=100, column=0, rowspan=1000, columnspan=399, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "server_list_box_scrollbar": [
                        lambda: tk.Scrollbar(self.master),
                        lambda w: w.grid(row=100, column=399, rowspan=1000, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "select_server_button": [
                        lambda: tk.Button(self.master, text="Choose Server", background="#999999"),
                        lambda w: w.grid(row=1100, column=0, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "add_server_button": [
                        lambda: tk.Button(self.master, text="Add Server", background="#999999", command=lambda: self.createwindow("SERVER_ADD")),
                        lambda w: w.grid(row=1100, column=200, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                },
                "after_widget_creation": [
                    lambda: self.current_widgets["server_list_box"].config(yscrollcommand=self.current_widgets["server_list_box_scrollbar"].set),
                    lambda: self.current_widgets["server_list_box_scrollbar"].config(command=self.current_widgets["server_list_box"].yview),
                ],
                "threads": [
                ],
            },
            # Server adding dialog allowing the user to add a server which
            # was not automatically detected or is not on the LAN
            "SERVER_ADD": {
                "title": "LanTalk Client - Add Server",
                "size": "450x450",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                "widgets": {  # TODO: Add the entry widgets for the server details
                    "indicator_label": [
                        lambda: tk.Label(self.master, text="Add LanTalk Server", background="#777777"),
                        lambda w: w.grid(row=0, column=0, rowspan=100, columnspan=400, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "add_server_button": [
                        lambda: tk.Button(self.master, text="Add", background="#999999"),
                        lambda w: w.grid(row=1100, column=0, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                    "cancel_button": [
                        lambda: tk.Button(self.master, text="Cancel", background="#999999", command=lambda: self.createwindow("SERVER_FIND")),
                        lambda w: w.grid(row=1100, column=200, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)
                    ],
                },
                "after_widget_creation": [
                ],
                "threads": [
                ],
            },
            "CHAT_SCREEN": {
                "title": "LanTalk Client - Chat ({})",
                "size": "600x600",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                "widgets": {  # TODO: Add the chat widgets
                    "indicator_label": [lambda: tk.Label(self.master, text="{}", background="#777777"), lambda w: w.grid(row=0, column=0, rowspan=100, columnspan=400, sticky=tk.N+tk.S+tk.E+tk.W)],
                    "clear_message_button": [lambda: tk.Button(self.master, text="Clear", background="#999999"), lambda w: w.grid(row=1100, column=0, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)],
                    "send_message_button": [lambda: tk.Button(self.master, text="Send", background="#999999"), lambda w: w.grid(row=1100, column=200, rowspan=100, columnspan=200, sticky=tk.N+tk.S+tk.E+tk.W)],
                },
                "after_widget_creation": [
                ],
                "threads": [
                ],
            }
        }

        self.createwindow("SERVER_FIND")  # Open straight to the server finder

    # GUI management functions
    def createwindow(self, name):
        """
        Reset the current window and convert it into a different window.

        Clear all the widgets on the window and replace them with the widgets
        of the specified window.
        """
        self.resetwindow()  # Reset the window first of all

        window = self.windows[name]  # Select the given window

        self.master.title(window["title"])  # Set the title
        self.master.geometry(window["size"])  # Set the size of the window
        self.master.minsize(window["minsize"][0], window["minsize"][1])
        self.master.maxsize(window["maxsize"][0], window["maxsize"][1])

        for widget_name in window["widgets"].keys():  # For every widget name
            # Add the widget to the list of widgets
            self.current_widgets[widget_name] = window["widgets"][widget_name][0](
            )
            window["widgets"][widget_name][1](
                self.current_widgets[widget_name])  # Put the grid on the window

        for function in window["after_widget_creation"]:
            function()  # Run the functions to be ran after widgets are created

        # Make the widgets resize with the window horizontally
        for column in range(self.master.grid_size()[0]):
            self.master.columnconfigure(column, weight=1)
        # Make the widgets resize with the window vertically
        for row in range(self.master.grid_size()[1]):
            self.master.rowconfigure(row, weight=1)

    def resetwindow(self):
        """
        Remove all widgets from the window and reset everything.

        The properties of the current master window are replaced with the
        defaults and all widgets are removed.
        """
        # Reset title to default
        self.master.title(self.windows["DEFAULT"]["title"])
        # Reset size to default
        self.master.geometry(self.windows["DEFAULT"]["size"])
        self.master.minsize(
            self.windows["DEFAULT"]["minsize"][0], self.windows["DEFAULT"]["minsize"][1])
        self.master.maxsize(
            self.windows["DEFAULT"]["maxsize"][0], self.windows["DEFAULT"]["maxsize"][1])

        # For every currently existing widget
        # (.copy required because the size of the dict changes)
        for widget_name in self.current_widgets.copy().keys():
            try:
                # Try removing the widget but fail silently (it could have been
                # a child of a previously removed widget)
                self.current_widgets[widget_name].destroy()
            except:
                pass
            # Remove the widget from the list of existing widgets
            del self.current_widgets[widget_name]

    def mainloop(self):
        """Run the mainloop of the main window."""
        self.master.mainloop()

    # Server connection functions
    def add_server(self, srv_name, srv_ip, srv_port, srv_version, srv_crypt):
        """Add a server to the list of available servers."""
        self.available_servers.append([
            srv_name,
            srv_ip,
            srv_port,
            srv_version,
            srv_crypt
        ])

#
# Main body
#


def main():
    """
    Run the main body of the program.

    This function mostly just creates an instance of the Client class
    and runs the window mainloop.
    """
    # Create a new instance of the client and start it
    client = Client()
    client.mainloop()

#
# Start the client if ran as standalone
#


if __name__ == "__main__":

    # Run the main part of the script if called directly as standalone
    main()
