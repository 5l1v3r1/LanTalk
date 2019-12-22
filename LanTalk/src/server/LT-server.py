#!/usr/bin/python3

# Import dependencies
import socket
import json
import threading
import http.server

# Define constants
SOFTWARE_VERSION = (1,0,0)
LTS_HOME_DIR = "."
CONF_LOCATION = "lanTalkSrv.conf"
VALID_CONF_OPTIONS = {
    "ServerName": [], # How the server identifies itself
    "ServerColorScheme": [], # Theme the clients will see after connecting. Hex color code
    "MaxClients": [], # How many clients will the server accept at most at any given time
    "BindAddr": [], # Address to bind to
    "BindPort": [], # Port to bind to
    "ConstantServerBcast": [], # Whether the server should constantly broadcast its LAN presence
    "ConstantServerBcastInterval": [], # How long to wait between broadcasts
    "BcastServerOnLan": [], # Whether to broadcast the server at all. Overrides ConstantServerBcast
    "RequireAuth": [], # Whether to allow login without authentication
    "AuthFile": [], # File which stores user credentials. Will be created if does not exist. Ignored if auth not required
}
DEFAULT_CONF_OPTIONS = {
    "ServerName": "A lanTalk Server",
    "ServerColorScheme": "333333",
    "MaxClients": "-1",
    "BindAddr": "",
    "BindPort": "8866",
    "ConstantServerBcast": "no",
    "ConstantServerBcastInterval": "5",
    "BcastServerOnLan": "yes",
    "RequireAuth": "yes",
    "AuthFile": "lanTalkSrv",
}

# Define error classes
class InvalidConfigException(Exception): pass

# Define functions
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
        if len(line) != 2: raise InvalidConfigException("File: `{}`, line: `{}/{}`, setting: `{}`. Invalid setting.".format(CONF_LOCATION,current_line,len(lines),line[0])) # If the line is not the right format, throw an error
        config[line[0].strip()] = line[1].strip() # Add setting to config. Extra strip needed in case there are spaces around = sign
    return config # Return the parsed config as dict

def conf_validate(conf_dict):
    """Validates the config for the server making sure every option is valid."""
    for setting in conf_dict.keys():
        # If the setting isn't on the pre-defined list, it's invalid so throw an error
        if setting not in VALID_CONF_OPTIONS.keys(): raise InvalidConfigException("File: `{}`. Invalid setting: `{}`.".format(CONF_LOCATION,setting))
        # 
