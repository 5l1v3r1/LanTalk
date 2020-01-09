#!/usr/bin/python3

# =============================================== #
# LanTalk Server
# License: GPL-3.0
# Maintainer: TR_SLimey <tr_slimey@protonmail.com>
# Description: Configurable python3 scripts
# (server & client) for real-time, encrypted
# messaging on a Local Area Network
# (and outside of it) using HTTP.
# =============================================== #

#
# Dependencies
#

import socket
import json
import re
import ipaddress
import os
import time
import threading
import random
import sys
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

#
# Constants (Settings which should generally be left untouched)
#

SOFTWARE_VERSION = (1,0,0) # Server version
LTS_HOME_DIR = "." # Where to look for all the files
LOG_LEVEL_NAMES = ["DBUG", "INFO", "WARN", "ERRO"]
CONF_LOCATION = "lanTalkSrv.conf" # Name of the config file
ID_SUFFIX_LENGTH = 10 # Length of the suffix (numbers after the dot)
MARK_AS_OFFLINE_DELAY = 7 # How many seconds to wait until marking a user offline (by default, client sends heartbeats every 5 seconds)

VALID_CONF_OPTIONS = { # Dict of config options and functions to validate them. Each function takes one argument, the value
	"LogLevel": lambda val: True if not haserror("int({})".format(val)) and int(val) in range(0, len(LOG_LEVEL_NAMES)) else False,
	"ServerName": lambda val: True if len(val) <= 40 else False, # Length under 40 (for client UI) check
	"ServerColorScheme": lambda val: True if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", val) else False, # Regex check if it's a valid hex color code
	"MaxClients": lambda val: True if val.replace("-","",1).isnumeric() and int(val) >= -1 else False, # Numeric and -1 or higher
	"BindAddr": lambda val: True if not haserror("ipaddress.ip_address({})".format(val)) or val == "" else False, # Check if valid IP address
	"BindPort": lambda val: True if val.isnumeric() and int(val) >= 1 and int(val) <= 65535 else False, # Check if valid port
	"ConstantServerBcast": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
	"ConstantServerBcastInterval": lambda val: True if val.isnumeric() and int(val) > 0 else False, # Is an integer and non-zero
	"AnswerBcastRequests": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
	"RequireAuth": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
	"AuthFile": lambda val: True if os.path.isfile(os.path.join(LTS_HOME_DIR, val)) else False, # If the file exists
	"SslCertFile": lambda val: True if os.path.isfile(os.path.join(LTS_HOME_DIR, val)) else False, # If the file exists
}

DEFAULT_CONF_OPTIONS = {
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

class InvalidConfigException(Exception): pass

#
# Function definitions
#

# Helper functions
def haserror(command):
	"""Checks whether running the arument causes an error. Warning: runs whatever is passed to it."""
	try:
	    if type(command) == str: exec(command)
	    else: command()
	    return False
	except: return True

def log(level, message):
	"""Logs messages to the console if they have the required log level."""
	if level > len(LOG_LEVEL_NAMES)-1 or level < 0: return # If the log level is invalid, ignore (for example, after an update)
	if level >= int(CONF["LogLevel"]): # If the LogLevel is lower than the message's, print the message
	    print("[ {} ] < {} > | {}".format(LOG_LEVEL_NAMES[level], time.strftime("%d/%m/%Y %H:%M:%S"), message))

# Config functions
def conf_parse(conf_string):
	"""Parses a config string in the form: `setting = value`, one setting per line, lines starting with # are ignored."""
	config = {} # Define empty config
	lines = conf_string.split("\n") # Separate lines of the config
	current_line = 0 # Line counter for error messages
	for line in lines:
	    current_line += 1 # Increment line counter
	    line=line.strip() # Remove any spaces around the line
	    if line.startswith("#") or line == "": continue # If the line is blank or starts with a hash, ignore it
	    line = line.split("=", 1) # Split the line at the first = sign
	    if len(line) != 2: raise InvalidConfigException("File: `{}`, line: `{}/{}`, setting: `{}`. Invalid setting.".format(CONF_LOCATION, current_line, len(lines),line[0])) # If the line is not the right format, throw an error
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
		log(0, "Starting Threads")
		# Start the threads (get all methods of the object and if their name starts with `thread_`, run them as threads)
		for thread in [getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and method.startswith("thread_")]:
			print("started a thread")
			# Add the thread to the list of threads
			self.threads.append(threading.Thread(target=thread))
			# Start last thread in the list (the one we just added)
			self.threads[-1].start()

	# Client management methods
	def generate_session_id(self, username):
		"""Generates an ID for user sessions when they are logged in. The IDs follow this pattern: `<username>.<random number>`."""
		# Session IDs will consist of the username and a random ID
		return "{}.{}".format(username, "".join([str(random.randint(1,9)) for x in range(ID_SUFFIX_LENGTH)]))

	# Thread methods
	def thread_login_manager(self):
		"""A thread which manages user logins"""
		while self.run_threads:
			time.sleep(5)
			print("thread 1")

	def thread_disconnect_manager(self):
		"""A thread which constantly checks for the time of the last heartbeat of each user and removes any users which didn't show signs of life recently."""
		while self.run_threads:
			#for client in self.signed_in_clients:
				#pass # TODO: Create the thread
			time.sleep(6)
			print("thread 2")


	# Misc. methods
	def stop_threads(self, wait_for_threads=True):
		"""Stop all threads started by this class and optionally wait for them to exit. Waits by default."""
		# Log that the threads are being stopped
		log(0, "Stopping Server Threads")
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
	"""The main body of the LanTalk server script."""

	try: # Exit cleanly no matter what

		# Beginning
		log(1, "LanTalk Server Starting")
		time.sleep(1) # Wait a bit (it looks better :P)

		# HTTP server section
		log(1, "Started listening on [{}:{}]".format(CONF["BindAddr"] if not CONF["BindAddr"] == "" else "*", CONF["BindPort"]))
		server = LanTalkServer((CONF["BindAddr"], int(CONF["BindPort"])), LanTalkServerRequestHandler)
		try: server.serve_forever()
		except KeyboardInterrupt: pass

		log(1, "Stopped listening for connections")

		server.stop_threads()

		log(1, "LanTalk Server Stopped")

		# Clean exit
		sys.exit(0)

	except Exception as err: # On any uncaught error
		# Log the error first of all
		log(3, "Fatal error encountered. The server will exit cleanly.\nError: {}".format(err))

		# Stop all threads since the script should have gotten far enough to start them but fail silently
		try: server.stop_threads()
		except: pass

		# Exit cleanly but report error (non-zero status code)
		sys.exit(1)

#
# Read the config and start the server if ran as standalone
#

if __name__ == "__main__":

	# Config reader section
	# Read the config file
	with open(os.path.join(LTS_HOME_DIR, CONF_LOCATION),"r") as conf_file:
		conf_string = conf_file.read()

	# Put the config string through the config functions. The end result should be a valid config dict
	CONF = conf_add_missing(conf_validate(conf_parse(conf_string)))

	CONF["LogLevel"] = 0 # Debugging override (to be commented out unless in development)

	log(0, "Config read and parsed successfully")

	# Run the main part of the script
	main()
