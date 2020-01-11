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

    # Init class properties
    master = tk.Tk() # The main window
    current_widgets = [] # A list of all the widgets currently displayed

    # Define the different windows and what properties they have
    windows = {
        "DEFAULT": {
            "title": "LanTalk Client",
            "size": "500x500",
            "minsize": "500x500",
            "maxsize": "600x600",
            "widgets": { # 2D list of widgets. Sub lists contain: [widget_object, placing_method], for example: [lambda widget: widget.grid(row=1, column=1), tk.Button(text="Example")]

            },
        },
        "SERVER_FINDER": {
            "title": "LanTalk Client - Server Finder",
            "size": "500x500",
            "minsize": "500x500",
            "maxsize": "600x600",
            "widgets": [
                [tk.Label(master, text="LanTalk Client", background="#444444", height=5), lambda w: w.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E)],
                [tk.Frame(master, height="200", width="500"), lambda w: w.grid(row=1, column=0, columnspan=4, sticky=tk.W+tk.E)]
            ]
        }
    }

    def __init__(self):
        self.createwindow("SERVER_FINDER")

    def createwindow(self, name):
        """Clears all the widgets on the window and replaces them with the widgets of the specified window."""
        self.resetwindow() # Reset the window first of all
        window = self.windows[name]
        self.master.title(window["title"])
        self.master.geometry(window["size"])
        for widget in window["widgets"]:
            widget[1](widget[0])


    def resetwindow(self):
        """Removes all widgets from the window"""
        for widget in self.current_widgets:
            try: widget.destroy()
            except: pass

    def mainloop(self):
        """Runs the mainloop of the main window."""
        self.master.mainloop()
        print(1)

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
