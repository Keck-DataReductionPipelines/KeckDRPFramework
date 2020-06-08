.. _framework:

The DRP Framework and the event queues
======================================

The ``framework`` module is the core of the system.

To illustrate a possible way to start up the framework, connect it to the pipeline, and then set it in motion, consider
this example:

.. code-block:: python

 from ..pipelines.kcwi_pipeline import Kcwi_pipeline

 pipeline = Kcwi_pipeline()
 framework = Framework(pipeline, 'config.cfg')
 framework.config.instrument = ConfigClass("instr.cfg")
 framework.logger.info("Framework initialized")

 framework.logger.info("Checking path for files")


 if os.path.isdir(path):
      flist = glob.glob(path + '/*.fits')
      for f in flist:
          args = Arguments(name=f)
          framework.append_event('next_file', args)

 else:
      args = Arguments(name=path)
      framework.append_event('next_file', args)

 framework.start()
 framework.waitForEver()

At the beginning, we are importing the pipeline definition, which is a class.

The pipeline class is then instantiated and assigned to the variable ``pipeline``, which is passed as an argument to
the ``Framework`` class, together with a configuration file which will be automatically parsed and assigned to the
dictionary ``context.config``.

Additional configuration parameters can be loaded into any user-defined dictionaries. For example, the "instr.cfg" file
is here loaded into the ``context.config.instrument`` making use of a ``ConfigClass`` which is directly derived from the
standard Python configuration system.

This script will take either a path or a file name as a argument. If a path is specified, the list of files is stored
into the ``flist`` variable. A loop is then initiated on these files. For each file, an ``Arguments`` class is
instantiated. The only property of this dictionary is ``args.name`` which is the name of the file.
Finally, the event ``next_file`` is triggered, and the arguments are passed on the function call. If the argument of the
script is a file, the file is passed directly to the event.

The call to ``framework.append_event('next_file', args)`` triggers the execution of the event ``next_file`` as
defined by the ``event_table`` of the imported pipeline. The arguments are those defined in the call.

The instructions ``framework.start()`` and ``framework.waitForEver()`` are standard calls that initiate the execution
and then set the framework into an infinite loop waiting for the execution of all the events.

The event queues
^^^^^^^^^^^^^^^^

At the core of the framework are two event queues that are charged with handling the actual execution of the code.
These two queues, called the Low Priority Queue (LPQ) and High Priority Queue (HPQ) are implemented as standard
Python Queues.

Once the framework has started and is in loop mode, the sequence of events is pretty simple: if events are found in the
HPQ, they are processed in the order in which they are stored in the queue. If an event produces an output, that
output is automatically passed as an argument to the following event in the queue. If the HPQ is empty, then the framework
checks the LPQ for events and triggers those if the are present.  If one of the events

The reason for having two queues is related to the need to execute sequences of events in the controlled manner.
A typical example is the one shown in the script above. If the script finds 10 files in the directory specified in the path,
those 10 files will immediately populate the LPQ with 10 ``next_file`` events. The corresponding pipeline event
``next_file`` contains calls to additional events that must be run, such as ``process_bias`` or ``process_flat``. Those
events will be automatically processed in the HPQ, and therefore will be processed *before* a new file is ingested.

In summary, the combination of LPQ and HPQ assure that a processing sequence is not interrupted by events generated
by the appearance of a new file. Other than the priority, there is no difference between the two queues. Internally,
events are added to the LPQ with a call to ``append_event``, while the ``push_event`` sends the event to the HPQ.

