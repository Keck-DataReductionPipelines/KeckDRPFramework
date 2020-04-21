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

from tools.interface import import_module

import_module("keckdrpframework")

from keckdrpframework.core.framework import Framework
from keckdrpframework.models.arguments import Arguments


def _parseArguments(in_args):
    description = "Test harness for Keck DRP Framework"
    usage = "\n{} [-w] [-W] [-s] [-i] [-c config_file] pipeline [file [files ...]]|[-d dirname]\n".format(in_args[0])
    epilog = "\nRuns the given pipeline using the given configuration\n"

    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description, usage=usage, epilog=epilog)

    parser.add_argument("-c", "--config", dest="config_file", type=str, help="Configuration file")
    parser.add_argument("-w", "--wait_for_event", dest="wait_for_event", action="store_true", help="Wait for events")
    parser.add_argument("-W", "--continue", dest="continuous", action="store_true", help="Continue processing, wait for ever")
    parser.add_argument(
        "-s",
        "--start_queue_manager_only",
        dest="queue_manager_only",
        action="store_true",
        help="Starts queue manager only, no processing",
    )
    parser.add_argument("-i", "--ingest_data_only", dest="ingest_data_only", action="store_true", help="Ingest data and terminate")
    parser.add_argument("-d", "--directory", dest="dirname", type=str, help="Input directory")

    parser.add_argument(dest="pipeline_name", type=str, help="Name of the pipeline class")
    parser.add_argument(dest="infiles", help="Input files", nargs="*")

    args = parser.parse_args(in_args[1:])
    return args


if __name__ == "__main__":

    args = _parseArguments(sys.argv)

    try:
        pipeline_name = args.pipeline_name
        config = args.config_file
    except Exception as e:
        print(e)
        args.print_help()
        sys.exit(1)

    try:
        framework = Framework(pipeline_name, config)
    except Exception as e:
        print("Test harness failed to initialize framework, exiting ...", e)
        traceback.print_exc()
        sys.exit(1)

    framework.logger.info("Framework initialized")

    if args.queue_manager_only:
        # The queue manager runs for ever.
        framework.logger.info("Starting queue manager only, no processing")
        framework.start_queue_manager()
    else:
        framework.logger.debug(f"infiles {args.infiles}, dirname {args.dirname}")
        if (len(args.infiles) > 0) or args.dirname is not None:
            # Ingest data and terminate
            framework.ingest_data(args.dirname, args.infiles)
            nfiles = framework.context.data_set.get_size()
            cfg = framework.config
            cargs = Arguments(cnt=nfiles, out_name="test.html", pattern="*.png", dir_name=cfg.output_directory)
            framework.append_event("contact_sheet", cargs)

        framework.start(args.queue_manager_only, args.ingest_data_only, args.wait_for_event, args.continuous)
