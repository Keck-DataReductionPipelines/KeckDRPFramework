"""
Created on Jul 9, 2019

@author: skwok
"""

import logging
import logging.config
import importlib_resources
import os


class DRPFLogger(logging.getLoggerClass()):
    pass


def getLogger(conf_file=None, name="DRPF"):
    if conf_file is not None:
        if os.path.exists(conf_file):
            logging.config.fileConfig(conf_file)
            return logging.getLogger(name)

        for lcf in (conf_file, "logger.conf"):
            path = "config/" + lcf  # always use slash
            ref = importlib_resources.files(__name__) / path
            with importlib_resources.as_file(ref) as conf_file:
                if os.path.exists(conf_file):
                    logging.config.fileConfig(str(conf_file))
                    return logging.getLogger(name)

    return logging.getLogger()
