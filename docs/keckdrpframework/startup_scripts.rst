Startup Scripts
===============

The easiest way to start the framework is by using startup scripts.

A complete example of such as script can be found in the ``pipeline_template/scripts`` directory.

The first part of the script contains the argument parser, which might be more complex than actually needed
for the specific application.

The ``__main__`` part of the script processes the arguments and starts the processing.

Operational modes
^^^^^^^^^^^^^^^^^

Reduction of individual files
-----------------------------

To reduce a single file or a set of files, the framework can be started with the following command line::

  template_script.py -frames=file1.fits,file2.fits -c config.cfg

The default script will add a ``next_file`` event to the queue, using the file name as a argument. This is
specified in the script itself, and can be changed if needed.

Ingestion of all the files in a specified directory
---------------------------------------------------

If a number of files are already stored in a specified directory, the framework can be started with the
following command line::

  template_script.py -infiles=*.fits -directory=/home/data -c config.cfg

All the files in the specified directory will be ingested if they match the infiles pattern, and a
``next_file`` event will be triggered for each of them. If ``-m -W`` are specified in the command line,
the framework will continue to monitor the directory, and trigger a ``next_file`` event for each new file.

Starting the framework processing engine with no files
------------------------------------------------------

It is possible to start the framework independently from any actual data to process. This is useful
for the server mode, which is currently implemented as an http API but will be replaced by Remote Procedure
Call.

To start the framework in this mode, use this command line::

  template_script.py -s -c config.cfg

Note about the next_file event
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is important to remember that a number of automatic ingestion routines trigger a ``next_file`` event,
which must be defined in the event_table of the pipeline.
For now, if you want to trigger a different function, we recommend this solution: modify the event table
so that the ``next_file`` event automatically points to a different event::

   event_table: {
     "next_file": ("my_own_event", None, None)
      }

It is the event name (``next_file``) that is hard-coded in the framework, not the actual Class or Function that
is being evaluated.
