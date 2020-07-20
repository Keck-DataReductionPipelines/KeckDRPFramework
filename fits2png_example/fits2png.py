"""
Test harness for DRP Framework

Created on 2019-09-05

@author skwok
"""

import sys
import os.path
import time
import argparse
import traceback
import logging

#from tools.interface import import_module

#import_module("keckdrpframework")

from keckdrpframework.core.framework import Framework
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.utils.drpf_logger import getLogger


from pipelines.fits2png_pipeline import Fits2pngPipeline

def _parseArguments(in_args):
    description = "FITS2PNG pipeline"

    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description)

    # this is a simple case where we provide a frame and a configuration file
    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description)
    parser.add_argument('-c', dest="config_file", type=str, help="Configuration file")
    parser.add_argument('-frames', nargs='*', type=str, help='input image file (full path, list ok)', default=None)

    # in this case, we are loading an entire directory, and ingesting all the files in that directory
    parser.add_argument('-infiles', dest="infiles", help="Input files", nargs="*")
    parser.add_argument('-d', '--directory', dest="dirname", type=str, help="Input directory", nargs='?', default=None)
    # after ingesting the files, do we want to continue monitoring the directory?
    parser.add_argument('-m', '--monitor', dest="monitor", action='store_true', default=False)

    # special arguments, ignore
    parser.add_argument("-i", "--ingest_data_only", dest="ingest_data_only", action="store_true",
                        help="Ingest data and terminate")
    parser.add_argument("-w", "--wait_for_event", dest="wait_for_event", action="store_true", help="Wait for events")
    parser.add_argument("-W", "--continue", dest="continuous", action="store_true",
                        help="Continue processing, wait for ever")
    parser.add_argument("-s", "--start_queue_manager_only", dest="queue_manager_only", action="store_true",
                        help="Starts queue manager only, no processing")

    args = parser.parse_args(in_args[1:])
    return args


def main():
    args = _parseArguments(sys.argv)


    # load the framework config file from the config directory of this package
    # this part uses the pkg_resources package to find the full path location
    # of framework.cfg
    framework_config_file = "configs/config.cfg"

    # load the logger config file from the config directory of this package
    # this part uses the pkg_resources package to find the full path location
    # of logger.cfg
    framework_logcfg_file = 'configs/logger.cfg'


    # add PIPELINE specific config files
    # this part uses the pkg_resource package to find the full path location
    # of template.cfg or uses the one defines in the command line with the option -c
    if args.config_file is None:
        pipeline_config_file = 'configs/fits2png.cfg'
        pipeline_config = ConfigClass(pipeline_config_file)
    else:
        pipeline_config = ConfigClass(args.pipeline_config_file)


    # END HANDLING OF CONFIGURATION FILES ##########

    try:
        framework = Framework(Fits2pngPipeline, framework_config_file)
        logging.config.fileConfig(framework_logcfg_file)
        framework.config.instrument = pipeline_config
    except Exception as e:
        print("Failed to initialize framework, exiting ...", e)
        traceback.print_exc()
        sys.exit(1)

    # this part defines a specific logger for the pipeline, so that
    # we can separate the output of the pipeline
    # from the output of the framework
    framework.logger = getLogger(framework_logcfg_file, name="DRPF")

    framework.logger.info("Framework initialized")

    # start queue manager only (useful for RPC)
    if args.queue_manager_only:
        # The queue manager runs for ever.
        framework.logger.info("Starting queue manager only, no processing")
        framework.start_queue_manager()

    # frames processing
    elif args.frames:
        for frame in args.frames:
            # ingesting and triggering the default ingestion event specified in the configuration file
            framework.ingest_data(None, args.frames, False)
            # manually triggering an event upon ingestion, if desired.
            # arguments = Arguments(name=frame)
            # framework.append_event('template', arguments)

    # ingest an entire directory, trigger "next_file" on each file, optionally continue to monitor if -m is specified
    elif (len(args.infiles) > 0) or args.dirname is not None:
        framework.ingest_data(args.dirname, args.infiles, args.monitor)

    nfiles = framework.context.data_set.get_size()
    cfg = framework.config
    cargs = Arguments(cnt=nfiles, out_name="test.html", pattern="*.png", dir_name=cfg.output_directory)
    framework.append_event("contact_sheet", cargs)

    framework.start(args.queue_manager_only, args.ingest_data_only, args.wait_for_event, args.continuous)


if __name__ == "__main__":
    main()

