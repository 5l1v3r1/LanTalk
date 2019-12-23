#!/usr/bin/python3

# Import dependencies
import socket
import json
import re
import ipaddress
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Constants
SOFTWARE_VERSION = (1,0,0) # Server version
LTS_HOME_DIR = "." # Where to look for all the files
LOG_LEVEL = 0 # (0)DEBUG, (1)INFO, (2)WARNING, (3)ERROR
CONF_LOCATION = "lanTalkSrv.conf" # Name of the config file
VALID_CONF_OPTIONS = { # Dict of config options and functions to validate them
    "ServerName": lambda val: True if len(val) <= 40 else False, # Length under 40 (for client UI) check
    "ServerColorScheme": lambda val: True if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", val) else False, # Regex check if it's a valid hex color code
    "MaxClients": lambda val: True if val.replace("-","",1).isnumeric() and int(val) >= -1 else False, # Numeric and -1 or higher
    "BindAddr": lambda val: True if not haserror("ipaddress.ip_address({})".format(val)) or val == "" else False, # Check if valid IP address
    "BindPort": lambda val: True if val.isnumeric() and int(val) >= 1 and int(val) <= 65535 else False, # Check if valid port
    "ConstantServerBcast": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "ConstantServerBcastInterval": lambda val: True if val.isnumeric() and int(val) > 0 else False, # Is an integer and non-zero
    "AnswerBcastRequests": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "RequireAuth": lambda val: True if val.lower() in ["yes", "no"] else False, # Check if is "yes" or "no" and ignore caps
    "AuthFile": lambda val: True if os.path.isfile(val) else False, # If the file exists
}
DEFAULT_CONF_OPTIONS = {
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
}


# Error classes
class InvalidConfigException(Exception): pass


# Helper functions
def haserror(command):
    """Checks whether running the arument causes an error. Warning: runs whatever is passed to it."""
    try:
        if type(command) == str: exec(command)
        else: command()
        return True
    except: return True

def log(level, message):
    LOG_LEVEL_NAMES = ["DBUG", "INFO", "WARN", "ERRO"] # Define names of log levels
    if level > len(LOG_LEVEL_NAMES)-1 or level < 0: return # If the log level is invalid, ignore
    if level >= LOG_LEVEL: # If the LOG_LEVEL is lower than the message's, print the message
        print("[ {} ] < {} > | {}".format(LOG_LEVEL_NAMES[level], time.strftime("%d/%m/%Y %H:%M:%S"), message))


# Config functions
def conf_parse(conf_string):
    """Parses a config string in the form: `setting = value`, one setting per line, lines starting with # are ignored."""
    log(0,"Using conf_parse function to parse the config string")
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
    log(0,"Using conf_validate function to validate the config dict")
    for setting in conf_dict.keys():
        # If the setting isn't on the pre-defined list, it's invalid so throw an error
        if setting not in VALID_CONF_OPTIONS.keys(): raise InvalidConfigException("File: `{}`. Invalid setting: `{}`.".format(CONF_LOCATION, setting))
        # Run the testing function for the setting
        if not VALID_CONF_OPTIONS[setting](conf_dict[setting]):
            raise InvalidConfigException("Invalid value `{}` for setting `{}` in config file `{}`!".format(conf_dict[setting], setting, CONF_LOCATION))
        return conf_dict # Despite being unchanged, return the dict for one-liners

def conf_add_missing(conf_dict):
    """Adds missing settings to the config and gives them default values."""
    log(0,"Using conf_add_missing function to add any missing settings to the config")
    for setting in DEFAULT_CONF_OPTIONS.keys():
        # If the setting isn't in the user config
        if not setting in conf_dict.keys():
            # Add it with the pre-defined default value
            conf_dict[setting] = DEFAULT_CONF_OPTIONS[setting]
            log(0,"Added setting `{} = {}` (default option)".format(setting, conf_dict[setting]))
    return conf_dict # Return the conf dict with the added configuration


# Server class
class LanTalkServer(BaseHTTPRequestHandler):
    """Class which handles the clients"""
    
    # Define some variables
    server_version = "LanTalkServer/{}".format(SOFTWARE_VERSION) # The "Server" header
    sys_version = "" # Remove Python version
    protocol_version = "HTTP/1.1" # To support persistent connections

    def log_message(self, form, *args):
        log(0,"Request from {}".format(self.client_address[0]))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


# Main body
def main():
    """The main body of the LanTalk server script."""

    # Beginning
    log(1,"Started LanTalk Server")
    time.sleep(0.5) # Wait a bit just cause

    # Config reader section
    log(0,"Reading and parsing config")
    with open(CONF_LOCATION,"r") as conf_file: # Read the config file
        conf_string = conf_file.read()
    conf = conf_add_missing(conf_validate(conf_parse(conf_string))) # Put the config string through the config functions. The end result should be a valid config dict
    log(0,"Config read and parsed successfully")

    # Broadcast receiver thread section
    def bcast_recv_thread():
        pass
    #

    # Broadcast sender thread section
    def bcast_send_thread():
        pass
    #

    # Starting HTTP server section
    log(1,"Starting HTTP server on {}:{}".format(conf["BindAddr"] if not conf["BindAddr"] == "" else "*", conf["BindPort"]))
    server = HTTPServer((conf["BindAddr"], int(conf["BindPort"])), LanTalkServer)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    


# Start the server if ran as standalone
if __name__ == "__main__": main()
