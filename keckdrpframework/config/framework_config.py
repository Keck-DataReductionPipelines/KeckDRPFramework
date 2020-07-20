"""
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: skwok
"""

from keckdrpframework.models.event import Event
from configparser import ConfigParser
import pkg_resources
import os
import sys


class ConfigClass(ConfigParser):
    config_defaults = {
        "name": "DRP-Example",
        "monitor_interval": 10,  # sec,
        "event_timeout": 1,
        "print_trace": True,
        "logger_config_file": "logger.cfg",
        "pipeline_path": ("", "pipelines"),
        "primitive_path": ("", "primitives"),
        "output_directory": "output",
        "temp_directory": "temp",
        "no_event_event": None,
        "default_ingestion_event": "next_file",
        "no_event_wait_time": 5,  # sec,
        "pre_condition_failed_stop": False,
        "file_type": "*.fits",
        "want_http_server": False,
        "http_server_port": 50100,
        "http_doc_root": ".",
        "http_defaultFile": "",
        "want_multiprocessing": False,
        "queue_manager_hostname": "localhost",
        "queue_manager_portnr": 50101,
        "queue_manager_auth_code": b"a very long authentication code",
    }

    def __init__(self, cgfile=None, **kwargs):
        super(ConfigClass, self).__init__(kwargs)
        self.properties = self.config_defaults.copy()
        if "default_section" in kwargs:
            self.default_section = kwargs["default_section"]
        else:
            self.default_section = "DEFAULT"
        if not cgfile is None:
            self.read(cgfile)

    def _getType(self, value):
        if not isinstance(value, str):
            return value

        value = value.strip()

        if value == "True":
            return True
        if value == "False":
            return False
        if value == "None":
            return None

        try:
            return eval(value)
        except Exception:
            pass

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

        return value

    def _getPath(self, path):
        if path is None:
            return None

        if os.path.isfile(path):
            return path
        else:
            fullpath = pkg_resources.resource_filename(__name__, path)
            if os.path.isfile(fullpath):
                return fullpath

        return None

    def read(self, cgfile):
        def digestItems(sec, known):
            values = self.items(sec)
            secValues = {}
            for k, v in values:
                if k in known:
                    continue
                secValues[k] = self._getType(v)
            return secValues

        path = self._getPath(cgfile)
        if path is None:
            return
        super().read(path)

        self.properties.update(digestItems(self.default_section, {}))
        sections = self.sections()

        for sec in sections:
            self.properties[sec] = digestItems(sec, self.properties)

    def __getattr__(self, key):
        val = self.properties.get(key.lower())
        if val is not None:
            return val

        if key in self.sections():
            return dict(self.items(key))

        return None

    def getValue(self, key, defValue=None):
        val = self.properties.get(key)
        if val is None:
            return defValue
        return val


if __name__ == "__main__":
    config = ConfigClass(sys.argv[1])
    print("Properties:\n", config.properties)
