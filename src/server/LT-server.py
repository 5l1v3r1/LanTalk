#!/usr/bin/python3

# =============================================== #
# LanTalk Server
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
import re
import ipaddress
import os
import time
import threading
import random
import sys
import socket
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

#
# Constants (Settings which should generally be left untouched)
#


# Server version
SOFTWARE_VERSION = (1, 0, 0)
LOG_LEVEL_NAMES = ["DBUG", "INFO", "WARN", "ERRO"]
# Name of the config file and location (same dir as script)
CONF_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "lanTalkSrv.conf")
# Length of the suffix (numbers after the dot)
ID_SUFFIX_LENGTH = 10
# How many seconds to wait until marking a user offline
# (by default, client sends heartbeats every 2 seconds)
MARK_AS_OFFLINE_DELAY = 5

# Dict of config options and functions to validate them.
# Each function takes one argument, the value.
VALID_CONF_OPTIONS = {
    "HomeDir": lambda val: True if os.path.isdir(val) else False, # If the directory exists
    "LogLevel": lambda val: True if not haserror(lambda: int(val)) and int(val) in range(0, len(LOG_LEVEL_NAMES)) else False, # If is an integer in the correct range
    "ServerName": lambda val: True if len(val) <= 40 else False, # Length under 40 (for client UI) check
    "ServerColorScheme": lambda val: True if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", val) else False, # Regex check if it's a valid hex color code
    "MaxClients": lambda val: True if val.replace("-","",1).isnumeric() and int(val) >= -1 else False, # Numeric and -1 or higher
    "BindAddr": lambda val: True if not haserror(lambda: ipaddress.ip_address(val)) or val == "" else False, # Check if valid IP address
    "BindPort": lambda val: True if val.isnumeric() and int(val) >= 1 and int(val) <= 65535 else False, # Check if valid port
    "ConstantServerBcast": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "ConstantServerBcastInterval": lambda val: True if val.isnumeric() and int(val) > 0 else False, # Is an integer and non-zero
    "AnswerBcastRequests": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "RequireAuth": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "AuthFile": lambda val: True if os.path.isfile(val) else False, # If the file exists
    "SslCertFile": lambda val: True if os.path.isfile(val) else False, # If the file exists
}

DEFAULT_CONF_OPTIONS = {
    "HomeDir": ".",
    "LogLevel": "1",
    "ServerName": "A lanTalk Server",
    "ServerColorScheme": "#333333",
    "MaxClients": "-1",
    "BindAddr": "",
    "BindPort": "8866",
    "ConstantServerBcast": "no",
    "ConstantServerBcastInterval": "5",
    "AnswerBcastRequests": "yes",
    "RequireAuth": "yes",
    "AuthFile": "lanTalkSrv-auth.dat",
    "SslCertFile": "",
}

#
# Error classes
#


# Raised when there are problems processing the config
class InvalidConfigException(Exception):
    """Error thrown when an error in the config is detected."""

    pass

#
# Function definitions
#


# Helper functions
def haserror(command):
    """
    Check whether running the arument causes an error.

    Warning: runs whatever is passed to it.
    """
    try:
        # If the arg is a string, exec it
        if type(command) == str:
            exec(command)
        # If not, it's probably a function so call it
        else:
            command()
        # If we got here, there was no error so return False
        return False
    except:
        return True


def log(level, message):
    """Log messages to the console if they have the required log level."""
    # If the log level is not yet read (pre-config logging), assume default
    global_log_level = CONF["LogLevel"] if "CONF" in globals() else DEFAULT_CONF_OPTIONS["LogLevel"]
    if level > len(LOG_LEVEL_NAMES)-1 or level < 0:
        # If the log level is invalid, ignore (for example, after an update)
        return
    # If the LogLevel is lower than the message's, print the message
    if level >= int(global_log_level):
        print("[ {} ] < {} > | {}".format(LOG_LEVEL_NAMES[level], time.strftime("%d/%m/%Y %H:%M:%S"), message))


# Config functions
def conf_parse(conf_string):
    """
    Parse a config string in the form: `setting = value`, one setting per line.

    Lines starting with # are ignored.
    """
    # Define empty config
    config = {}
    # Separate lines of the config
    lines = conf_string.split("\n")
    # Line counter for error messages
    current_line = 0
    for line in lines:
        # Increment line counter
        current_line += 1
        # Remove any spaces around the line
        line = line.strip()
        if line.startswith("#") or line == "":
            # If the line is blank or starts with a hash, ignore it
            continue
        # Split the line at the first = sign
        line = line.split("=", 1)
        if len(line) != 2: raise InvalidConfigException("File: `{}`, line: `{} /{}`, setting: `{}`. Invalid setting.".format(CONF_LOCATION, current_line, len(lines),line[0])) # If the line is not the right format, throw an error
        config[line[0].strip()] = line[1].strip() # Add setting to config. Extra strip needed in case there are spaces around = sign
    return config # Return the parsed config as dict

def conf_validate(conf_dict):
    """Validates the config for the server making sure every option is valid."""
    for setting in conf_dict.keys():
        # If the setting isn't on the pre-defined list, it's invalid so throw an error
        if setting not in VALID_CONF_OPTIONS.keys(): raise InvalidConfigException("File: `{}`. Invalid setting: `{}`.".format(CONF_LOCATION, setting))
        # Run the testing function for the setting
        if not VALID_CONF_OPTIONS[setting](conf_dict[setting]):
            raise InvalidConfigException("Invalid value `{}` for setting `{}` in config file `{}`!".format(conf_dict[setting], setting, CONF_LOCATION))
        return conf_dict # Despite being unchanged, return the dict for one-liners

def conf_add_missing(conf_dict):
    """Adds missing settings to the config and gives them default values."""
    for setting in DEFAULT_CONF_OPTIONS.keys():
        # If the setting isn't in the user config
        if not setting in conf_dict.keys():
            # Add it with the pre-defined default value
            conf_dict[setting] = DEFAULT_CONF_OPTIONS[setting]
            log(0, "Added setting `{} = {}` (default option)".format(setting, conf_dict[setting]))
    return conf_dict # Return the conf dict with the added configuration

def get_file_contents(file_name, parent_dir=None):
    """Reads a given file cleanly as bytes (to avoid decoding errors) and returns its contents. Raises errors if the file could not be read."""
    # If the parent dir is not specified, use the home dir
    if parent_dir == None: parent_dir = CONF["HomeDir"]
    # Treat the filename as a subpath of the parent
    file_path = os.path.join(parent_dir, file_name)
    # Cleanly open the file and return its contents
    with open(file_path, "rb") as file: return file.read()

#
# Server classes
#


class LanTalkServer(ThreadingMixIn, HTTPServer):
    """The main server class which handles client connections and management"""

    # Initialise class properties
    signed_in_clients = {} # Dict of all clients with session IDs as keys
    messages_to_send = [] # List of messages that are yet to be sent
    threads = [] # A list of threads created by the server
    run_threads = True # Variable controlling whether threads should be running

    # On object creation
    def __init__(self, bind_addr, request_handler):
        # Run the initialisation function of the HTTPServer class (no need for `self` arg - it's passed automatically)
        super().__init__(bind_addr, request_handler)

        # Save the request handler as a property (to allow exchanging data)
        self.request_handler = request_handler

        # Log that threads are being started
        log(0, "Starting threads")
        # Start the threads (get all methods of the object and if their name starts with `thread_`, run them as threads)
        for thread in [getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and method.startswith("thread_")]:
            # Add the thread to the list of threads
            self.threads.append(threading.Thread(target=thread))
            # Start last thread in the list (the one we just added)
            self.threads[-1].start()
        log(0, "All threads started")

    # Client management methods
    def generate_session_id(self, username):
        """Generates an ID for user sessions when they are logged in. The IDs follow this pattern: `<username>.<random number>`."""
        # Session IDs will consist of the username and a random ID
        return "{}.{}".format(username, "".join([str(random.randint(1,9)) for x in range(ID_SUFFIX_LENGTH)]))

    # Thread methods
    def thread_login_manager(self):
        """A thread which manages user logins"""
        while self.run_threads:
            pass # TODO: Create the thread

    def thread_disconnect_manager(self):
        """A thread which constantly checks for the time of the last heartbeat of each user and removes any users which didn't show signs of life recently."""
        while self.run_threads:
            for client in self.signed_in_clients:
                pass # TODO: Create the thread

    # Misc. methods
    def stop_threads(self, wait_for_threads=True):
        """Stop all threads started by this class and optionally wait for them to exit. Waits by default."""
        # Log that the threads are being stopped
        log(0, "Stopping server threads")
        # Tell threads to stop
        self.run_threads = False
        # Wait for the threads to exit if told to
        if wait_for_threads:
            for thread in self.threads:
                thread.join()

class LanTalkServerRequestHandler(BaseHTTPRequestHandler):
    """The main request handler class which processes requests made to the server"""

    # Modify BaseHTTPRequestHandler behavior
    server_version = "LanTalkServer/{}".format(SOFTWARE_VERSION) # The "Server" header
    sys_version = "" # Remove Python version from response (it's unnescessary and possibly a security problem)
    protocol_version = "HTTP/1.1" # To support persistent connections for speed

    # Server methods
    def log_message(self, form, *args): # Suppress default logging and only log if right log level set
        """Logs important server events according to the global log level."""
        # TODO: Fix this unholy creature and make it respect what's passed to it ^
        log(0, "{} request from {} for path {}".format(self.command, self.client_address[0], self.path))

    def do_GET(self):
        """Runs when a GET request is received."""
        self.respond("Nothing here yet!") # Temporary. GET requests will serve the panel at some point in the future (TODO)

    def do_POST(self): # The chat protocol will use POST requests
        """Runs when a POST requets is received."""
        pass # TODO: Implement messaging protocol

    # Misc. methods
    def respond(self, message):
        """Send a response to the client with the message"""

        # Add headers
        self.send_response(200, "LanTalk Accepted Request")
        self.send_header("Content-Length", len(message)) # Needed for persistent connections
        self.end_headers()

        # Send the message
        message = message.encode("utf-8")
        self.wfile.write(message)

#
# Main body
#


def main():
    """The main body of the LanTalk server script. Starts the server and runs any setup"""

    # Define CONF as global as all parts of the script use it
    global CONF

    # Define server as a global so that the request handler can access it's properties when requests are made
    global server

    try: # Exit cleanly no matter what

        # Read the config in the script's dir, then put the config string through the config functions. The end result should be a valid config dict
        CONF = conf_add_missing(conf_validate(conf_parse(get_file_contents(CONF_LOCATION, "").decode())))

        CONF["LogLevel"] = 0 # Debugging override (to be commented out unless in development)

        log(0, "Config read and parsed successfully")

        # Beginning
        log(1, "LanTalk Server starting")
        time.sleep(0.5) # Wait a bit (it looks better :P)

        # HTTP server section
        log(1, "Started listening on [{}:{}]".format(CONF["BindAddr"] if not CONF["BindAddr"] == "" else "*", CONF["BindPort"]))
        server = LanTalkServer((CONF["BindAddr"], int(CONF["BindPort"])), LanTalkServerRequestHandler)
        try: server.serve_forever()
        except KeyboardInterrupt: pass

        # When the server exits normally (for some reason) or there's a KeyboardInterrupt, do the following
        log(1, "Stopped listening for connections")

        # Stop all threads started by the server
        server.stop_threads()

        log(1, "LanTalk Server stopped")

        # Clean exit
        sys.exit(0)

    except Exception as err: # If there's any kind of error, log in and exit as cleanly as possible
        # Log the error first of all
        log(3, "Fatal error encountered. The server will exit cleanly.\nError: {}".format(err))

        # Stop all threads since the script should have gotten far enough to start them but fail silently if this causes an error
        try: server.stop_threads()
        except: pass

        # Exit cleanly but report error (non-zero exit code)
        sys.exit(1)

#
# Start the server if ran as standalone
#


if __name__ == "__main__":
    # Run the main part of the script if called directly as standalone
    main()
