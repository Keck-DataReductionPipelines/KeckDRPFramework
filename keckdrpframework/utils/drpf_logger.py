"""
Created on Jul 9, 2019

@author: skwok
"""

import logging
import logging.config
import pkg_resources
import os
from astropy.logger import logging_levels
from astropy.wcs.docstrings import name


class DRPFLogger(logging.getLoggerClass()):
    pass


def getLogger(conf_file=None, name="DRPF"):
    if conf_file is not None:
        if os.path.exists(conf_file):
            logging.config.fileConfig(conf_file)
            return logging.getLogger(name)

        for lcf in (conf_file, "logger.conf"):
            path = "config/" + lcf  # always use slash
            conf_file = pkg_resources.resource_filename("keckdrpframework", path)

            if os.path.exists(conf_file):
                logging.config.fileConfig(conf_file)
                return logging.getLogger(name)

    return logging.getLogger()
