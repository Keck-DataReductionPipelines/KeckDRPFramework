.. _startup_scripts:

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

To reduce a single file or a set of files, the framework can be started with the following command line:

.. code-block:: python

  >>> template_script.py -frames=file1.fits file2.fits -c config.cfg

The default script will add a default event to the queue, using the file name as a argument. This event
is specified in the configuration file, as ``default_ingestion_event``. A standard event is provided
as default, called ``ingest_only``. This event is always available, inherited from the ``BasePipeline``.
It does not process the data in any way. Note that the reason why we introduced the idea of a default
event upon ingestion is that the framework is also able to automatically monitor a directory and ingest
the files as they appear. When run in that mode, it is necessary to have a default processing step.

Ingestion of all the files in a specified directory
---------------------------------------------------

If a number of files are already stored in a specified directory, the framework can be started with the
following command line:

.. code-block:: python

  >>> template_script.py -infiles=*.fits -directory=/home/data -c config.cfg

All the files in the specified directory will be ingested if they match the infiles pattern, and a
``next_file`` event will be triggered for each of them. If ``-m -W`` are specified in the command line,
the framework will continue to monitor the directory, and trigger the default ingestion event for each new file.
See previous section for a description of the default event.

Starting the framework processing engine with no files
------------------------------------------------------

It is possible to start the framework independently from any actual data to process. This is useful
for the server mode, which is currently implemented as an http API but will be replaced by Remote Procedure
Call.

To start the framework in this mode, use this command line:

.. code-block:: python

  >>> template_script.py -s -c config.cfg

Note about the next_file event
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is important to remember that a number of automatic ingestion routines trigger a ``next_file`` event,
which must be defined in the event_table of the pipeline.
For now, if you want to trigger a different function, we recommend this solution: modify the event table
so that the ``next_file`` event automatically points to a different event:

.. code-block:: python

   event_table: {
     "next_file": ("my_own_event", None, None)
      }

It is the event name (``next_file``) that is hard-coded in the framework, not the actual Class or Function that
is being evaluated.
