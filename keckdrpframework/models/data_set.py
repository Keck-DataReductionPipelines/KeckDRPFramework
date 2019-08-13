'''
Created on Jul 8, 2019

@author: skwok
'''

import os
import threading
import time
import glob
import pandas as pd

import astropy.io.fits as pf
from astropy.utils.exceptions import AstropyWarning
import warnings

class Data_set:
    '''
    Represents the data set
    Content is stored in self.data_table
    '''

    def __init__(self, dirname, logger, config):
        '''
        Constructor
        '''
        self.dir_name = dirname
        self.logger = logger
        self.config = config
        self.data_table = pd.DataFrame()
        self.must_stop = False
        self.monitor_interval = config.monitor_interval
        self.file_type = config.file_type
        self.update_date_set()

    def digest_new_item (self, filename):
        """
        Returns the information to be stored.
        The format must be a pd.Series with names and values.
        The Series will have a name = filename 
        """
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', AstropyWarning)
                hdr = pf.getheader(filename)                
                return pd.Series(dict(zip(hdr.keys(), hdr.values())), name=filename)
        except Exception as e:
            self.logger.error (f"Failed to open file {filename}, {e}")
        
        return None
    
    def append_item (self, filename):
        """
        Appends item, if not already exists.
        """
        if os.path.isfile(filename) and not filename in self.data_table.index:
            row = self.digest_new_item (filename)
            if not row is None:
                short = os.path.basename(filename)
                self.logger.info(f"Appending {short} data set")
                self.data_table = self.data_table.append (row)
    
        
    def update_date_set (self):
        """
        Updates the content of this data set.
        Called by loop() when monitoring the directory.
        Or can be called on demand.
        """
        if self.dir_name is None:
            return
        if not os.path.isdir(self.dir_name):
            return
        flist = glob.glob (self.dir_name + '/' + self.file_type)
        flist = sorted (flist)
        for f in flist:
            self.append_item(f)
            
    def getInfo (self, index, column):
        try:
            return self.data_table.at[index, column]
        except:
            self.logger.warn("Keyword %s is not avaialble" % str(column))
            return None
            
    def loop (self):
        '''
        Waits for changes in the directory, then digests the changes.
        Maybe needs to monitor other events also
        '''
        ok = True
        last_time = 0
        while ok:
            dir_state = os.stat(self.dir_name)
            curr_time = dir_state.st_mtime
            if curr_time > last_time:
                self.update_date_set ()
                last_time = curr_time
            time.sleep (self.monitor_interval)
            if self.must_stop:
                break
            
    def start_monitor (self):
        '''
        Monitors for changes in the given directory
        '''
        thr = threading.Thread(target=self.loop)
        thr.setDaemon(True)
        thr.start()
        
    def stop_monitor (self):
        self.must_stop = True

        
if __name__ == '__main__':
    
    from utils.DRPF_logger import getLogger
    import config.framework_config as framework_config

    config = framework_config.ConfigClass ("config.cfg")
    logger = getLogger(config.logger_config_file)
    
    data_set = Data_set ('../../test_fits', logger, config)
    data_set.start_monitor()
    print ("Waiting ...")
    time.sleep (10)
    print ("Done")
    data_set.stop_monitor()
    print (data_set.data_table)
