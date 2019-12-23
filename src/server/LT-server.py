#!/usr/bin/python3

# Import dependencies
import socket
import json
import re
import ipaddress
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Constants
SOFTWARE_VERSION = (1,0,0) # Server version
LTS_HOME_DIR = "." # Where to look for all the files
CONF_LOCATION = "lanTalkSrv.conf" # Name of the config file
VALID_CONF_OPTIONS = { # Dict of config options and functions to validate them
    "ServerName": [
        lambda val: True if len(val) <= 40 else False # Length under 40 (for client UI) check
    ],
    "ServerColorScheme": [
        lambda val: True if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", val) else False # Regex check if it's a valid hex color code
    ],
    "MaxClients": [
        lambda val: True if val.replace("-","",1).isnumeric() and int(val) >= -1 else False # Numeric and -1 or higher
    ],
    "BindAddr": [
        lambda val: True if not haserror(ipaddress.ip_address(val)) else False # Check if valid IP address
    ],
    "BindPort": [
        lambda val: True if val.isnumeric() and int(val) >= 1 and int(val) <= 65535 else False # Check if valid port
    ],
    "ConstantServerBcast": [
        lambda val: True if val.lower() in ["yes", "no"] else False # Check if is "yes" or "no" and ignore caps
    ],
    "ConstantServerBcastInterval": [
        lambda val: True if val.isnumeric() and int(val) < 0 else False # Is an integer and non-zero
    ],
    "AnswerBcastRequests": [
        lambda val: True if val.lower() in ["yes", "no"] else False # Check if is "yes" or "no" and ignore caps
    ],
    "RequireAuth": [
        lambda val: True if val.lower() in ["yes", "no"] else False # Check if is "yes" or "no" and ignore caps
    ],
    "AuthFile": [
        lambda val: True if os.path.isfile(val) # If the file exists
    ],
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


# Config setting validator functions
def validator_isservername(value):
    if len(value) <= 40: return True
    else: return fa;se
def validator_isyesno(value):
    """Checks if the value is either yes or no"""
    if value.lower() in ["yes","no"]: return True
    else: return False

def validator_ishexcolor(value)


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
        if len(line) != 2: raise InvalidConfigException("File: `{}`, line: `{}/{}`, setting: `{}`. Invalid setting.".format(CONF_LOCATION,current_line,len(lines),line[0])) # If the line is not the right format, throw an error
        config[line[0].strip()] = line[1].strip() # Add setting to config. Extra strip needed in case there are spaces around = sign
    return config # Return the parsed config as dict

def conf_validate(conf_dict):
    """Validates the config for the server making sure every option is valid."""
    for setting in conf_dict.keys():
        # If the setting isn't on the pre-defined list, it's invalid so throw an error
        if setting not in VALID_CONF_OPTIONS.keys(): raise InvalidConfigException("File: `{}`. Invalid setting: `{}`.".format(CONF_LOCATION,setting))
        # 
