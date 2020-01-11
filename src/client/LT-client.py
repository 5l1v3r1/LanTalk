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

#
# Define constants
#

LOG_LEVEL = 0
LOG_LEVEL_NAMES = ["DBUG", "INFO", "WARN", "ERRO"]

#
# Define functions
#

def log(level, message):
	"""Logs messages to the console if they have the required log level."""

	global_log_level = LOG_LEVEL
	if level > len(LOG_LEVEL_NAMES)-1 or level < 0: return # If the log level is invalid, ignore (for example, after an update)
	if level >= int(global_log_level): # If the LogLevel is lower than the message's, print the message
	    print("[ {} ] < {} > | {}".format(LOG_LEVEL_NAMES[level], time.strftime("%d/%m/%Y %H:%M:%S"), message))

#
# GUI class
#

class Client():
    """The main class of the LanTalk client which handles everything."""

    def __init__(self):
        # Init class properties
        self.master = tk.Tk() # The main window
        self.current_widgets = {} # A dict of all the widgets currently displayed with names as keys

        # Define the different windows and what properties they have
        self.windows = {
            "DEFAULT": {
                "title": "LanTalk Client",
                "size": "500x500",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                "widgets": { # 2D dict of widgets. Lists contain: [widget_object_creator, placing_method], for example: [lambda: tk.Button(text="Example"), lambda widget: widget.grid(row=1, column=1)]. The lambda is nescessary before the widget object so that a new object is created every time, otherwise there are errors
                },
            },
            "SERVER_FINDER": {
                "title": "LanTalk Client - Server Finder",
                "size": "500x500",
                "minsize": [400, 400],
                "maxsize": [1200, 900],
                "widgets": {
                    "title_label": [lambda: tk.Label(self.master, text="LanTalk Client", background="#444444"), lambda w: w.grid(row=0, column=0, columnspan=4, sticky=tk.N+tk.S+tk.W+tk.E)],
                    "server_list_box": [lambda: tk.Frame(self.master, background="#444444", height=self.master.winfo_height()-20, width=self.master.winfo_width()), lambda w: w.grid(row=1, column=0, columnspan=4, sticky=tk.N+tk.S+tk.W+tk.E)]
                }
            }
        }

        self.master.columnconfigure(1, weight=1) # Automatically resize everything when window size changes

        self.createwindow("SERVER_FINDER") # Open straight to the server finder

    def createwindow(self, name):
        """Clears all the widgets on the window and replaces them with the widgets of the specified window."""

        self.resetwindow() # Reset the window first of all
        window = self.windows[name] # Select the given window
        self.master.title(window["title"]) # Set the title
        self.master.geometry(window["size"]) # Set the size of the window
        self.master.minsize(window["minsize"][0], window["minsize"][1])
        self.master.maxsize(window["maxsize"][0], window["maxsize"][1])
        for widget_name in window["widgets"].keys(): # For every widget name
            self.current_widgets[widget_name] = window["widgets"][widget_name][0]() # Add the widget to the list of widgets
            window["widgets"][widget_name][1](self.current_widgets[widget_name]) # Put the grid on the window

    def resetwindow(self):
        """Removes all widgets from the window and resets everything to default."""

        self.master.title(self.windows["DEFAULT"]["title"]) # Reset title to default
        self.master.geometry(self.windows["DEFAULT"]["size"]) # Reset size to default
        self.master.minsize(self.windows["DEFAULT"]["minsize"][0], self.windows["DEFAULT"]["minsize"][1])
        self.master.maxsize(self.windows["DEFAULT"]["maxsize"][0], self.windows["DEFAULT"]["maxsize"][1])
        for widget_name in self.current_widgets.copy().keys(): # For every currently existing widget
            try: self.current_widgets[widget_name].destroy() # Try removing the widget but fail silently (it could have been a child of a previously removed widget)
            except: pass
            del self.current_widgets[widget_name] # Remove the widget from the list of existing widgets

    def mainloop(self):
        """Runs the mainloop of the main window."""

        self.master.mainloop()
        print("Exited GUI") # Temporary

#
# Main body
#

def main():

    # Create a new instance of the client and start it
    client = Client()
    client.mainloop()

#
# Start the client if ran as standalone
#

if __name__ == "__main__":

	# Run the main part of the script if called directly as standalone
	main()
