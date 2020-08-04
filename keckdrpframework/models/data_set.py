"""
Created on Jul 8, 2019

@author: skwok
"""

import os
import sys
import threading
import time
import glob
import pandas as pd
from keckdrpframework.models.event import Event
from keckdrpframework.models.arguments import Arguments
import astropy.io.fits as pf
from astropy.utils.exceptions import AstropyWarning
import warnings


class DataSet:
    """
    Represents the data set
    Content is stored in self.data_table, which is a pandas data frame.
    """

    def __init__(self, dirname, logger, config, event_queue):
        """
        Constructor
        """
        self.dir_name = dirname
        self.logger = logger
        self.config = config
        self.data_table = pd.DataFrame()
        self.must_stop = False
        self.monitor_interval = config.monitor_interval
        self.file_type = config.file_type
        self.event_queue = event_queue
        self.update_data_set()

    def digest_new_item(self, filename):
        """
        Returns the information to be stored.
        In this case, the information is simply the FITS header, assuming filename refers to a FITS.
        In case this class is sub-classed to handle other types of data, 
        the returned format must be a pd.Series with names and values.
        The Series will have a name = filename. 
        """

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", AstropyWarning)
                hdr = pf.getheader(filename)
                return pd.Series(dict(zip(hdr.keys(), hdr.values())), name=filename)
        except Exception as e:
            self.logger.error(f"Failed to open file {filename}, {e}")

        return None

    def append_item(self, filename):
        """
        Appends item, if not already exists.
        """
        if filename is None:
            self.logger.warning(f"filename is defined")
            return

        if not os.path.isfile(filename):
            self.logger.warning(f"{filename} is not a file")
            return

        if filename in self.data_table.index:
            self.logger.warning(f"{filename} is already in the table")
            return

        row = self.digest_new_item(filename)
        if not row is None:
            short = os.path.basename(filename)
            self.logger.debug(f"Appending {short} to the data set")
            self.data_table = self.data_table.append(row)
            try:
                self.event_queue.put(Event(self.config.default_ingestion_event, Arguments(name=filename)))
            except:
                self.logger.warning("There is no default ingestion event in the configuration file")

    def update_data_set(self):
        """
        Updates the content of this data set.
        Called by loop() when monitoring the directory.
        Or can be called on demand.
        """
        self.logger.debug("Ingesting data from: %s" % self.dir_name)
        if self.dir_name is None:
            return
        if not os.path.isdir(self.dir_name):
            return
        flist = glob.glob(self.dir_name + "/" + self.file_type)
        flist = sorted(flist)
        for f in flist:
            self.append_item(f)

    def get_info(self, index):
        """
        Retrieves the row [index]        
        """
        return self.data_table.loc[index]

    def get_info_column(self, index, column):
        """
        Retrieves and returns data stored in the data_table.
        index is the name used to append this data.
        column is any key associated with the data, for example a FITS header name.
        """
        try:
            return self.data_table.at[index, column]
        except:
            self.logger.warning("Keyword %s is not available" % str(column))
            return None

    def get_size(self):
        return self.data_table.shape[0]

    def set_info_value(self, index, column, value):
        try:
            self.data_table.at[index, column] = value
        except Exception as e:
            self.logger.warning(f"Failed to set data_table[{index},{column}] to {value}")

    def _loop(self):
        """
        Waits for changes in the directory, then digests the changes.
        Maybe needs to monitor other events also.
        
        """
        ok = True
        last_time = 0
        while ok:
            dir_state = os.stat(self.dir_name)
            curr_time = dir_state.st_mtime
            if curr_time > last_time:
                self.update_data_set()
                last_time = curr_time
            time.sleep(self.monitor_interval)
            if self.must_stop:
                break

    def start_monitor(self):
        """
        Monitors for changes in the given directory.
        
        This must be called separately in the framework main thread before the starting the processing loop.
        """
        thr = threading.Thread(target=self._loop)
        thr.setDaemon(True)
        thr.start()

    def stop_monitor(self):
        """
        Stops the monitoring thread
        """
        self.must_stop = True

    def remove_all(self):
        """
        Removes all entries in data_table.
        """
        self.data_table = self.data_table[0:0]
        self.logger.info(f"Remove all entries date set table")

    def change_directory(self, dirname):
        """
        Changes data set directory
        """
        self.dir_name = dirname
        self.logger.info(f"Changed data set dir to {dirname}")
