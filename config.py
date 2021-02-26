""" Common module to read the configuration

The configuration is spread into two files: config.ini and a user
specific private file (configured in config.ini).
The implemented functions that read both places and provide a ConfigParser
to get configuration values.

Functions
    init
        Creates a new ConfigParser object and reads configuration files.
        Attributes
            Path to config file (optional). Default: config.ini
        Returns
            ConfigParser
    read(config)
        Reads the configuration files.

If started as a standalon script, it takes two arguments:
    * configuration section name
    * configuration option name
The script returns the configured value of the section / option.
"""

import configparser
import sys
from os import path
import logging

logger = logging.getLogger(__name__)
CONFIG_PATH = 'config.ini'

def init(*args):
    config = configparser.ConfigParser()
    if len(args) > 0:
        global CONFIG_PATH
        CONFIG_PATH = args[0]
    return config

def read(config_parser):
    global CONFIG_PATH
    config_parser.read(CONFIG_PATH)
    userauthconfig = config_parser.get('app', 'PathToUserAuthConfig', fallback='')
    logger.debug("PathToUserAuthConfig: %s", userauthconfig)
    if userauthconfig and path.exists(userauthconfig):
        config_parser.read(userauthconfig)
        logger.debug("%s read successfully", userauthconfig )

__CONF = init()
read(__CONF)

def reread():
    read(__CONF)

def get(*args, **kwargs):
    return __CONF.get(*args, **kwargs)

def getint(*args, **kwargs):
    return __CONF.getint(*args, **kwargs)

def getboolean(*args, **kwargs):
    return __CONF.getboolean(*args, **kwargs)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        print(__CONF.get(sys.argv[1], sys.argv[2]))
