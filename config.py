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
configPath = 'config.ini'

def init(*args):
    config = configparser.ConfigParser()
    if len(args) > 0:
        global configPath
        configPath = args[0]
    read(config)
    return config

def read(config):
    global configPath
    config.read(configPath)
    userauthconfig = config.get('app', 'PathToUserAuthConfig', fallback='')
    logger.debug("PathToUserAuthConfig: " + userauthconfig)
    if userauthconfig and path.exists(userauthconfig):
        config.read(userauthconfig)
        logger.debug(userauthconfig + " read successfully")

if __name__ == '__main__':
    conf = init()
    if len(sys.argv) == 3:
        print(conf.get(sys.argv[1], sys.argv[2]))


