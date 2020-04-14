"""
Test template for DRP Framework

"""

import sys
import os.path
import time
import argparse
import traceback

from keckdrpframework.core.framework import Framework
from keckdrpframework.models.arguments import Arguments


def _parseArguments(in_args):
    description = "Test template for Keck DRP Framework"
    usage = "\n{} pipeline config_file [file [files ...]]|[-d dirname]\n".format(in_args[0])
    epilog = "\nRuns the given pipeline using the given configuration\n"

    parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description, usage=usage, epilog=epilog)

    parser.add_argument(dest="pipeline_name", type=str, help="Name of the pipeline class")

    parser.add_argument(dest="config_file", type=str, help="Configuration file")

    parser.add_argument(dest="infiles", help="Input files", nargs="*")

    parser.add_argument("-d", "--directory", dest="dirname", type=str, help="Input directory")

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
        print("Test template failed to initialize framework, exiting ...", e)
        traceback.print_exc()
        sys.exit(1)

    framework.logger.info("Framework initialized")

    print(args.infiles, args.dirname)
    if (len(args.infiles) > 0) or args.dirname is not None:
        # Ingest data and terminate
        framework.ingest_data(args.dirname, args.infiles)

    framework.start()
