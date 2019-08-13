'''
Created on Jul 9, 2019

@author: shkwok
'''

import logging
import logging.config
import pkg_resources

class DRPF_Logger (logging.getLoggerClass()):
    pass

def getLogger (conf_file=None, name="DRPF"):    
    if not conf_file is None:
        path = "config/"+conf_file  # always use slash
        conf_file = pkg_resources.resource_filename("keckdrpframework", path)
        print("Conf file: %s" % conf_file)
        logging.config.fileConfig(conf_file)
    return logging.getLogger(name)