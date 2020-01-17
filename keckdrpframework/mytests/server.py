"""
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
"""


import sys
import os.path
import glob

from core.framework import Framework
from config.framework_config import ConfigClass

from pipelines.kcwi_pipeline import Kcwi_pipeline
from models.arguments import Arguments
import subprocess
import time

#
# Local functions
#


if __name__ == "__main__":

    if len(sys.argv) >= 1:
        # path = sys.argv[1]

        pipeline = Kcwi_pipeline()
        framework = Framework(pipeline, "KCWI_config.cfg")
        framework.config.instrument = ConfigClass("instr.cfg")
        if framework.config.instrument.interactive >= 1:
            subprocess.Popen("bokeh serve", shell=True)
            time.sleep(2)

        framework.logger.info("Framework initialized")

        framework.start_http_server()
        framework.logger.info("HTTP server started")

        framework.start()
        framework.waitForEver()
    else:
        print("Usage {} dir_or_file".format(sys.argv[0]))
