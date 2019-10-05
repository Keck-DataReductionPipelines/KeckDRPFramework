'''
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: skwok
'''

from keckdrpframework.models.event import Event

import pkg_resources
import os

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
            # try to see if the file is in the current working directory
            if os.path.isfile(cgfile):
                fullpath = cgfile
            else:
                cwd = os.getcwd()
                fullpath = os.path.join(cwd, cgfile)
                if not os.path.isfile(fullpath):
                    fullpath = pkg_resources.resource_filename(__name__, cgfile)
                if not os.path.isfile(fullpath):
                    return
            self.read(fullpath)
    
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
        try:        
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
        except:
            raise Exception("Failed to read configuration file " + fname)

    def __getattr__ (self, key):
        return self.properties[key]
    
    def get (self, key, defValue):
        val = self.properties.get(key)
        if val is None:
            return defValue
        return val

if __name__ == "__main__":
    Config = ConfigClass ()
