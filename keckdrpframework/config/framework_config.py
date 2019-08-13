'''
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: shkwok
'''

from keckdrpframework.models.event import Event
#import datetime

import pkg_resources

class ConfigClass:    
    
    def __init__ (self, cgfile=None, defaults=None):
        self.properties = {
            "logger_config_file" : "logger.conf",
            "monitor_interval" : 10, 
            "output_directory": "output",
            "temp_directory": "temp", 
            "http_server_port": 50100,
            "doc_root": ".",
            "file_type": "*.fits"}
        
        if not defaults is None:
            self.properties.update (defaults)
        if not cgfile is None:
            path = cgfile  # always use slash
            cgfile = pkg_resources.resource_filename(__name__, path)
            self.read(cgfile)
    
    def getType (self, value):
        value = value.strip()
        try:
            i = int(value)
            return i
        except:
            pass
        
        try:
            f = float(value)
            return f
        except:
            pass
        
        if value == "True":
            return True
        if value == "False":
            return False
        
        try:
            return eval(value)
        except:
            return value
        
    def read (self, fname):        
        with open(fname, 'r') as fh:
            props = self.properties
            for line in fh:
                line = line.strip()
                if len(line) < 1: continue
                try:
                    idx = line.index("#")
                    line = line[:idx]
                except:
                    pass
                if len(line) < 1: continue
                parts = line.split('=')
                if len(parts) > 1:
                    key, val = parts
                    key = key.strip()
                    val = val.strip()
                    props[key] = self.getType (val)
            return
        raise Exception("Failed to read configuration file " + fname)

    def __getattr__ (self, key):
        return self.properties[key]

if __name__ == "__main__":
    Config = ConfigClass ()
    #path = 'config/config.cfg'  # always use slash
    #filepath = pkg_resources.resource_filename(__name__, path)
    #print(filepath)
    #Config.read(filepath)
    #print(Config.__dict__)
    
    #print (Config.denoise_sigmas[1])
    #print (Config.no_event_event)
    
