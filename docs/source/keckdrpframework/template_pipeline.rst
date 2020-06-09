Creating a pipeline using the template
======================================

In this example we will create a data reduction package called MyDRP.

The directory ``pipeline_template`` provides a simple starting point to create a data processing
pipeline.

Start by making a copy of the directory with all the included subdirectories

.. code-block:: python

  >>> mkdir MyPipeline
  >>> cd MyPipeline
  >>> cp -r <KeckDRPFramework_LOCATION>/pipeline_template/. .

Setup.py
^^^^^^^^
You can now start editing the files in the new pipeline, starting with ``setup.py``. In this file,
it is important to edit the NAME, the description and the licence. Note that this file assumes that
any command line interface script will live in the ``scripts`` directory. Note also that the package name
is currently set to ``template``. In the next step, we will rename this directory to be the actual
package name of your pipeline, so you need to change this variable accordingly.

The name of your pipeline should be set correctly in the ``NAME`` variable and in the ``packages`` variable of the
``setup`` dictionary.

The main pipeline
^^^^^^^^^^^^^^^^^^^^^^^^

Defining a pipeline is essentially the same as defining the entries of the ``event_table``.
A complete description of the event table is provided in :ref:`events_actions`.

The ``import`` section of this file is made of two parts: first we import the necessary framework modules such as:

.. code-block:: python

  from keckdrpframework.pipelines.base_pipeline import BasePipeline
  from keckdrpframework.models.processing_context import ProcessingContext
  from keckdrpframework.primitives.simple_fits_reader import SimpleFitsReader

The ``SimpleFitsReader`` import is not necessary but it is a good starting point to import FITS files.

The next step is to import primitives that are defined in the ``primitives`` directory. As explained in the :ref:`primitives`
section, if the name of the file containing a primitive corresponds to the name of the class that defines the
primitive, there is no need to import it (see the example call to ``template2`` in the event table). If this is not the case,
then the primitive must be imported explicitely (see the example call to ``templace`` in the event table).

.. code-block:: python

  from template.primitives.Template import MyTemplate

In the simple case in which a single primitive is invoked, a single entry in the event table is all that is needed.
Remember that the format for the event table is:

.. code-block:: python

  event_name: (primitive_name, state, next event)

Which can be simplified to:

.. code-block:: python

  event_name: (primitive_name, None, None)

if no state update is required and we don't need to trigger another event after the first.

The template pipeline contains 4 events, which have been chosen to illustrate 4 possible cases of the use of
primitives.

* the ``next_file`` event calls the primitive ``SimpleFitsReader`` which is a standard primitive provided by the
  framework and imported explicitly.

* the ``template`` event calls the primitive ``MyTemplate`` which is defined in a file called ``Template.py``, and
 imported explicitly. This primitive belongs to this specific pipeline, not to the framework.

* the ``template2`` event calls the primitive ``Template2`` which is defined in a file called ``Template2.py``. Because
  the name of the class and the name of file are the same, there is no need to explicitly import the module: the
  framework will autodiscover it and import it.

* the ``template_action`` event calls the primitive ``template_action``, which is just a function defined
  in this same pipeline file. This is how we define simple, standard events that don't need their own file or module.

Note that this is a true pipeline, in the sense that each event automatically trigger another one: this is achieved
by declaring the next event (3rd element of the tuple) to be the next event in the pipeline: ``next_file`` calls
``template``, which in turns calls ``template2``, which calls ``template_action``.
This is not necessary: this way of building a pipeline simulates the concept of a recipe.  It is entirely possible to
define a set of independent, disconnected events.


Creating the startup script
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final step to run the pipeline is to trigger eventd and apply it to a file, such as FITS file.
There are many ways of doing this (see :ref:`_startup_script`).

Let's analyze the content of the startup script provided as an example.

We start by importing the newly created pipeline:

.. code-block:: python

   from  template.pipelines.template_pipeline import TemplatePipeline

We then define a set of command line arguments in a function that is passed to the argument parser.

.. code-block:: python

  def _parseArguments(in_args):
    description = "Template pipeline CLI"

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
                        help="Starts queue manager only, no processing",
    )

    args = parser.parse_args(in_args[1:])
    return args

The next step is to define a ``main()`` function, which will parse the arguments and start the processing.

The template contains a number of useful comments that should guide the user throughout the process
of setting up the specific pipeline.

A concept that deserve some explanation is the triggering of the first event.

The framework configuration file ``framework.cfg`` contains the definition of the default event that is
triggered when a file is ingested, specified as:

.. code-block:: python

    #
    # Default event to trigger on new files
    #
    default_ingestion_event = "next_file"

This means that if we don't make any other choice, and we call the method ``framework.ingest_data`` on the list of
frames, the framework will automatically trigger the ``next_file`` event on each file specified on the command
line or in a specified directory. Because we have this event in our ``event_table``, this will work perfectly, and
the rest of the events will be triggered in sequence as specified in the ``event_table``.

Sometimes, it is desirable to trigger a different event. For example, we can specify a different type of ``next_file``
which only parses the header but does not trigger any processing.
To do so, we would first change the ``event_table`` to start with:

.. code-block:: python

    event_table = {

        # this is a standard primitive defined in the framework
        "next_file": ("SimpleFitsReader", "file_ready", None),

We would then manually add the desired event to the queue, as part of the ``template_script.py``, immediately
after the ingestion:

.. code-block:: python

       elif args.frames:
        for frame in args.frames:
            # ingesting and triggering the default ingestion event specified in the configuration file
            framework.ingest_data(None, args.frames, False)
            # manually triggering an event upon ingestion, if desired.
            arguments = Arguments(name=frame)
            framework.append_event('template', arguments)

In this case, for each file we automatically trigger ``next_file``, which returns the control to the framework
without triggering anything else. After that, we define a new argument based on the name of the file,
and we manually add the ``template`` event to the queue.
The result is exactly the same as before, but we have much more control on what happens.

If instead of providing a list of files we want to process an entire directory, we can use the ``-d`` option
paired with the ``-i`` option, to specify the directory and the file pattern to use.
If we want to continue monitoring the directory for new files, we can use the ``-m -W`` combination.

Installation and examples
^^^^^^^^^^^^^^^^^^^^^^^^^

To install the pipeline, use:

.. code-block:: shell

   python setup.py develop (or install)

A few example of using the template pipeline on a set of test data is provided here:

.. code-block:: shell

    > template_script -f <KeckDRPFramework_LOCATION>/keckdrpframework/unit_tests/test_files/*.fits

    > template_script -d <KeckDRPFramework_LOCATION>/keckdrpframework/unit_tests/test_files -i *.fits -m -W

