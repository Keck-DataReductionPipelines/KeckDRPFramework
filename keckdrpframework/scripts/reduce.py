'''
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
'''

from keckdrpframework.core.framework import Framework
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.pipelines.kcwi_pipeline import Kcwi_pipeline
from keckdrpframework.models.arguments import Arguments
import subprocess
import time
import argparse


def reduce(file_name):
    subprocess.Popen('bokeh serve', shell=True)
    time.sleep(2)

    pipeline = Kcwi_pipeline()
    framework = Framework(pipeline,  'KCWI_config.cfg')
    framework.config.instrument = ConfigClass("instr.cfg")
    framework.logger.info("Framework initialized")

    framework.logger.info("Checking path for files")

    args = Arguments(name=file_name)
    framework.append_event('next_file', args)

    framework.start()
    framework.waitForEver()


def main():

    parser = argparse.ArgumentParser(description='Process a single file.')
    parser.add_argument('frame', nargs=1, type=str, help='input image file')

    args = parser.parse_args()

    reduce(args.frame[0])
