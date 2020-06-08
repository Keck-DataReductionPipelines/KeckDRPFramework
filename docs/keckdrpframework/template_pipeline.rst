Creating a pipeline using the template
======================================

In this example we will create a data reduction package called MyDRP.

The directory ``pipeline_template`` provides a simple starting point to create a data processing
pipeline.

Start by making a copy of the directory with all the included subdirectories

.. code-block:: python

  >>> mkdir MyPipeline
  >>> cd MyPipeline
  >>> cp -r <KeckDRPFramework_LOCATION>/keckdrpframework/pipeline_template/. .

Setup.py
^^^^^^^^
You can now start editing the files in the new pipeline, starting with ``setup.py``. In this file,
it is important to edit the NAME, the description and the licence. Note that this file assumes that
any command line interface script will live in the ``scripts`` directory. Note also that the package name
is currently set to ``my_pipeline``. In the next step, we will rename this directory to be the actual
package name of your pipeline, so you need to change this variable accordingly.

Eventually, your ``setup.py`` file should contain:
.. code-block:: python

  NAME = 'MyDRP'

And the setup dictionary should contain:
.. code-block:: python

   packages=['MyDRP',],

Create the main pipeline
^^^^^^^^^^^^^^^^^^^^^^^^

As a first step, rename the directory ``my_pipeline`` to be the name of the pipeline that you are creating

.. code-block:: python

  >>> mv my_pipeline MyDRP

In the subdirectory ``pipelines``, rename the ``template_pipeline.py``

.. code-block:: python

  >>> cd MyDRP/pipelines
  >>> mv template_pipeline.py MyDRP.py

You can now edit the ``MyDRP.py`` file by completing the entries in the ``event_table``. A complete description of the
event table is provided in :ref:`events_actions`. The ``import`` section of this file is made of two
parts: first we import the necessary framework modules such as:

.. code-block:: python

  from keckdrpframework.pipelines.base_pipeline import BasePipeline

Then we import all the primitives that are defined in the ``primitives`` directory, and that will
ultimately provide the actual processing. Using the primitive that we will define later, your import
should look like this:

.. code-block:: python

  from ..primitives.mydrp_primitive import *

In the simple case in which a single primitive is invoked, a single entry in the event table is all that is needed.
Remember that the format for the event table is:

.. code-block:: python

  event_name: (primitive_name, state, next event)

Which can be simplified to:

.. code-block:: python

  event_name: (primitive_name, None, None)

if no state update is required and we don't need to trigger another event after the first.

Again, using the primitive that we will define later, your event table will look like this:

.. code-block:: python

  event_table: {
     "mydrp_event": ("DrpPrimitive", None, None)
     }

The final step is to change the name of the main class, from ``template_pipeline`` to ``MyDRP``:

.. code-block:: python

  class MyDRP (BasePipeline):


Connecting the event to the code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's now turn to the primitives directory, and start by renaming the ``template_primitive.py`` file
to a suitable name

.. code-block:: python

  >>> mv template_primitive.py mydrp_primitive.py

We can now edit the file to change the name of the primitive that is defined in the file. Change the name
``Template`` to the primitive_name that you have used in your event table.

.. code-block:: python

 class DrpPrimitive(BasePrimitive):
    def __init__(self, action, context)
        """
        Constructor
        """
        BasePrimitive.__init__(self, action, context)


    def _perform (self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        print("Processing: %s" % self.action.args.name)
        #raise Exception ("Not yet implemented")

Note that we have replaced the "not yet implemented" code with a very simple operation, such as
printing the name of the file being processed. This is just to have code that can run without
generating an exception.

See the :ref:`primitives` documentation for a complete description of the primitives.

Creating the startup script
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final step to run the pipeline is to trigger the new event and apply it to a file, such as FITS file.
There are many ways of doing this (see :ref:`_startup_script`).

The easiest approach is to use the "single file" method, where the use specifies the ``-frames`` argument.

In the script, make sure that the event that is generates is not ``next_file`` but ``mydrp_event``, which
is the event that you specified in the ``event_table``.

In practice, the specific section of the startup script would say:

.. code-block:: python

  # single frame processing
    elif args.frames:
        for frame in args.frames:
            arguments = Arguments(name=frame)
            framework.append_event('mydrp_event', arguments)

Other changes that are needed to this files are:
 - add the import for the pipeline at the beginning
 - pass the imported pipeline as an argument to the framework initialization code

.. code-block:: python

  from MyDRP.pipelines.MyDRP import MyDRP

.. code-block:: python

    try:
        framework = Framework(MyDRP, config)
    except Exception as e:
        print("Failed to initialize framework, exiting ...", e)

We are now ready to install the pipeline and run it (we will use an example file called myfitsfile.fits)

.. code-block:: python

  >>> python setup.py develop
  >>> template_script -frames=myfitsfile.fits -c config.cfg

Here we are assuming that the configuration parameters in config.cfg are correct. A discussion of the
configuration parameters can be found in TBD.

If everything worked correctly, the script will assign the file to an argument and pass the argument
to the ``mydrp_event``, which is associated to the ``DrpPrimitive`` code. The code in that primitive
will inherit the argument, accessed via ``self.action.args`` and will execute the ``_perform`` method
of the class.

The result of the run should look like this:

.. code-block:: python

    2019-12-17 10:20:49:DRPF:INFO: Framework initialized
    2019-12-17 10:20:49:DRPF:INFO: Event to action ('DrpPrimitive', None, None)
    2019-12-17 10:20:49:DRPF:INFO: Framework main loop started
    2019-12-17 10:20:49:DRPF:INFO: Executing action DrpPrimitive
    Processing: myfitsfile.fits
    2019-12-17 10:20:49:DRPF:INFO: Action DrpPrimitive done
    2019-12-17 10:20:50:DRPF:INFO: No new events - do nothing
    2019-12-17 10:20:50:DRPF:INFO: No pending events or actions, terminating

