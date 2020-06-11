.. _startup_scripts:

Startup Scripts
===============

The easiest way to start the framework is by using startup scripts.
Unfortunately, due to the flexibility of the framework and of the wide variety of different ways of processing files,
the start up script is the most complicated piece of the framework.

A complete example of such as script can be found in the ``pipeline_template/scripts`` directory.

It is convenient to think of this script as being made of different blocks, not all of which are necessary at
any given time.

The import block
^^^^^^^^^^^^^^^^

To use the framework, add these imports to the startup script:

.. code-block:: python

    from keckdrpframework.core.framework import Framework
    from keckdrpframework.config.framework_config import ConfigClass
    from keckdrpframework.models.arguments import Arguments
    from keckdrpframework.utils.drpf_logger import getLogger

The last import is only necessary if we want to customize the logging system, for example to add a secondary log
for the pipeline, distinct from the main framework log.

Additional imports that are normally used are:

.. code-block:: python

    import subprocess
    import time
    import argparse
    import sys
    import traceback
    import pkg_resources
    import logging.config

Finally, it is important to import the actual pipeline definition file. The location of the pipeline can be found by
looking at the structure of the ``pipeline_template`` package.

.. code-block:: python

    from template.pipelines.template_pipeline import TemplatePipeline

Of course, this assumes that there is a pipeline package called ``template``, that is has a submodule called ``pipelines``
(basically a directory with a ``__init__.py`` file) with a ``template_pipeline.py`` module which describes
the actual pipeline as specified in pipelines_.

The argument parser
^^^^^^^^^^^^^^^^^^^

The following section of the startup script implements a function that parses arguments and passes them
to the main function.

There is no mandatory structure for the argument parser: the purpose of the startup script is to
decide how to start the framework, which files to work on, and which event(s) to trigger. Any way that provides
access to these functions is acceptable. A good way to learn about the possible parameters is again to look
at the ``pipeline_template`` startup script, but we can provide a possible set of useful parameters here.
It is important to note that if a parameter is offered to the users, the corresponding piece of code must be added to
the main function, which is the reason why we cannot really provide a standardized startup script.

We start with the definition of the function:

.. code-block:: python

    def _parseArguments(in_args):
        description = "Template pipeline CLI"

        # this is a simple case where we provide a frame and a configuration file
        parser = argparse.ArgumentParser(prog=f"{in_args[0]}", description=description)

* ``parser.add_argument('-c', dest="config_file", type=str, help="Configuration file")`` This parameter can be used
to override the standard configuration file for the pipeline. In the ``pipeline_template`` package, the
configuration files are stored in a ``config`` directory, and accessed directly using the package discovery
system offered by the ``pkg_resources`` Python module. If we add this parameter, users can build a configuration file
in the working directory and then specify that it should be used instead of the default one.

* ``parser.add_argument('-f', '--frames', nargs='*', type=str, help='input image file (full path, list ok)', default=None)``
This parameters specifies which files should be processed by the pipeline

* ``parser.add_argument('-l', '--list', dest='file_list', help='File containing a list of files to be processed', efault=None)``
If used, this parameters allows users to provide a file containing a list of files to be processed

* ``parser.add_argument('-infiles', dest="infiles", help="Input files", nargs="*")`` Paired with the next argument (``-d``)
this argument specifies the file pattern to use in ingesting the files in a directory

* ``parser.add_argument('-d', '--directory', dest="dirname", type=str, help="Input directory", nargs='?', default=None)``
Used with the previous argument, this argument specifies which directory should be used to ingest files.

* ``parser.add_argument('-m', '--monitor', dest="monitor", action='store_true', default=False)`` If this flag is
set in the command line, after ingesting all the files in the directory specified, the framework will enter into
monitoring mode, and keep ingesting files as they appear. It has to be specified together with the ``-W`` argument
which tells the framework to continue operating even when all the events have been processed.

The following arguments are reserved for the pipeline control flow and will be described separately (TBD!!)

.. code-block:: python

    parser.add_argument("-i", "--ingest_data_only", dest="ingest_data_only", action="store_true",
                        help="Ingest data and terminate")
    parser.add_argument("-w", "--wait_for_event", dest="wait_for_event", action="store_true", help="Wait for events")
    parser.add_argument("-W", "--continue", dest="continuous", action="store_true",
                        help="Continue processing, wait for ever")
    parser.add_argument("-s", "--start_queue_manager_only", dest="queue_manager_only", action="store_true",
                        help="Starts queue manager only, no processing",

Finally, the ``_parseArguments`` function is closed by passing the results to the main function:

.. code-block:: python

    args = parser.parse_args(in_args[1:])
    return args

The main function
^^^^^^^^^^^^^^^^^

Opening
-------

The main function opens with:

.. code-block::python

    def main():

    args = _parseArguments(sys.argv)

Configuration
-------------

The configuration system is flexible and can be adapted to the need of the specific pipeline. Normally, it is a good
habit to have a separate configuration file for the framework and one for the pipeline itself. We can also have a
logging configuration file. In the following we will assume that all three files are used.

The basic principle used is this: a standard configuration file is provided for the framework, the pipeline and the logger.
The configuration files live in a ``config`` directory, part of the main package defining the pipeline. Since it is
the most likely to need changes, the pipeline configuration file can be overridden by the ``-c`` parameter. A suitable
part of the code handles this parameter.

The block looks like this:

.. code-block::python

    # START HANDLING OF CONFIGURATION FILES ##########
    pkg = 'template'

    # load the framework config file from the config directory of this package
    # this part uses the pkg_resources package to find the full path location
    # of framework.cfg
    framework_config_file = "configs/framework.cfg"
    framework_config_fullpath = pkg_resources.resource_filename(pkg, framework_config_file)

    # load the logger config file from the config directory of this package
    # this part uses the pkg_resources package to find the full path location
    # of logger.cfg
    framework_logcfg_file = 'configs/logger.cfg'
    framework_logcfg_fullpath = pkg_resources.resource_filename(pkg, framework_logcfg_file)

    # add PIPELINE specific config files
    # this part uses the pkg_resource package to find the full path location
    # of template.cfg or uses the one defines in the command line with the option -c
    if args.config_file is None:
        pipeline_config_file = 'configs/template.cfg'
        pipeline_config_fullpath = pkg_resources.resource_filename(pkg, pipeline_config_file)
        pipeline_config = ConfigClass(pipeline_config_fullpath, default_section='TEMPLATE')
    else:
        pipeline_config = ConfigClass(args.pipeline_config_file, default_section='TEMPLATE')

While the first two are obvious and are only meant to find the full path for the configuration files,
the configuration file for the pipeline deserves some explanation.
In the example shown here, we use ``ConfigClass``, a class provided by the ``keckdrpframework.config.framework_config``
module. This class subclasses the standard ``ConfigParser`` class and provides a set of default parameters and the
possibility of specifying a default section of the configuration file. In our case, the section of the configuration
file is TEMPLATE. This means that the pipeline configuration file will have a ``[TEMPLATE]`` section with
all the parameters related to the pipeline.


The ``pkg`` variable can be se to the actual name of the current package.

Operational modes
^^^^^^^^^^^^^^^^^

Reduction of individual files
-----------------------------

To reduce a single file or a set of files, the framework can be started with the following command line:

.. code-block:: python

  >>> template_script.py -frames=file1.fits file2.fits

The default script will add a default event to the queue, using the file name as a argument. This event
is specified in the configuration file, as ``default_ingestion_event``. A standard event is provided
as default, called ``ingest_only``. This event is always available, inherited from the ``BasePipeline``.
It does not process the data in any way.

Ingestion of all the files in a specified directory
---------------------------------------------------

If a number of files are already stored in a specified directory, the framework can be started with the
following command line:

.. code-block:: python

  >>> template_script.py -infiles=*.fits -directory=/home/data

All the files in the specified directory will be ingested if they match the ``infiles`` pattern, and a
``next_file`` event will be triggered for each of them. If ``-m -W`` are specified in the command line,
the framework will continue to monitor the directory, and trigger the default ingestion event for each new file.
See previous section for a description of the default event.

Starting the framework processing engine with no files
------------------------------------------------------

It is possible to start the framework independently from any actual data to process. This is useful
for the multiprocessing mode.

To start the framework in this mode, use this command line:

.. code-block:: python

  >>> template_script.py

