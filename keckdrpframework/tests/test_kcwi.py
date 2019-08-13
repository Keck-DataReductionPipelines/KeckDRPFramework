'''
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
'''

import sys
#sys.path.append('/Users/lrizzi/Python_Projects/Framework/prototype')
import os.path
import glob

from keckdrpframework.core.framework import Framework
from keckdrpframework.config.framework_config import ConfigClass

from keckdrpframework.pipelines.kcwi_pipeline import Kcwi_pipeline
from keckdrpframework.models.arguments import Arguments
import subprocess
import time


if __name__ == '__main__':

    if len(sys.argv) >= 2:
        path = sys.argv[1]

        subprocess.Popen('bokeh serve', shell=True)
        time.sleep(2)

        pipeline = Kcwi_pipeline()
        framework = Framework(pipeline, 'KCWI_config.cfg')
        framework.config.instrument = ConfigClass("instr.cfg")
        framework.logger.info("Framework initialized")

        framework.logger.info("Checking path for files")


        if os.path.isdir(path):
            #flist = glob.glob(path + '/*.fits')
            flist = ['/Users/lrizzi/KCWI_DATA_1/kb181012_00014.fits',
                     '/Users/lrizzi/KCWI_DATA_1/kb181012_00016.fits']
            flist = ['/Users/lrizzi/KCWI_DATA_1/kb181012_00016.fits']
            for f in flist:
                args = Arguments(name=f)
                framework.append_event('next_file', args)

        else:
            args = Arguments(name=path)
            framework.append_event('next_file', args)

        framework.start()
        framework.waitForEver()

    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))