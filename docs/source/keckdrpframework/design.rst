.. _design:

Design and basic concepts
=========================

This section describes the core ideas behind the design and implementation of the framework.

Setting up and starting the framework
------------------------

The ``framework`` module is the core of the system.

To illustrate a possible way to start up the framework, connect it to the pipeline, and then set it in motion, consider
this example:

.. code-block:: python

 from KCWI_PIPELINE.pipelines.kcwi_pipeline import Kcwi_pipeline

 pipeline = Kcwi_pipeline()
 framework = Framework(pipeline, 'config.cfg')
 framework.start()

This block of code performs a full start up of the framework, but doesn't do any processing (see startup_scripts_).

These are the operations happening behind the scene:

* an instance of the ``BasePipeline`` class is created and assigned to the ``pipeline`` variable
* an instance of the ``Framework`` class is created, using the pipeline and a configuration file as an argument
* the configuration file is parsed (an actual configuration object can also be used) and loaded
* two event queue are created as explained below, a high priority queue and a low priority queue
* a ``context`` is created, based on ``kcwidrpframework.models.processing_context.ProcessingContext``
* the event loop is started in a separate thread

The ``start()`` method of the framework accepts the following parameters: ``qm_only`` to start the queue system
without adding any event, ``ingest_data_only`` to TBD(ASK SHUI), ``wait_for_events`` to prevent the framework
from exiting after the last event if processed, and ``continuous`` TBD(ASK SHUI).

The event loop
--------------

The core of the framework is an event loop implemented as a thread. This loop performs the simple operations of
inspecting the low and high priority queues (described below), picking the first event from the top of the queues,
converting the event to an "action", and executing the action.

The sequence of operations is:

* check for events in the high priority queue, if none:
* check for events in the low priority queue
* if no events, either exit or repeat the loop depending on user parameters
* convert the event into an action (an actual class, or a function) using the ``event_table`` of the pipeline
* if the action is a function, look for preconditions and postconditions associated with it
* if the action is a class, run the ``apply()`` method of the class, which automatically checks for pre and post conditions

The event queues
----------------

The framework uses two event queues that are charged with handling the actual execution of the code.
These two queues, called the Low Priority Queue (LPQ) and High Priority Queue (HPQ) are implemented as standard
Python Queues.

The reason for having two queues is related to the need to execute sequences of events in the controlled manner.
A typical example is the need to run multiple operations (multiple events, resulting in multiple actions) on the same
file after it has been ingested. Let's assume that the default event upon ingestion processes the header and,
depending on the image type, triggers a chain of events that are specific to the particular image type: the sequence
could include a simple set of ``remove_overscan`` and ``trim_overscan`` for a bias but very complicated
for a science frame (``remove_overscan``, ``trim_overscan``, ``subtract_bias``, ``apply_flat_field``,
``apply_lambda_calib``
and so on). If a directory contains a number of files, the LPQ would immediately be filled
by calls to the ingestion events for each of the file. As the framework starts to process them, the linked events
would temporarily fill up the HPQ with the processing steps, and the framework would process them before
moving on to the next file. An exception to this is the multiprocessing mode which is described later.

Adding events to the queues
---------------------------

This issue is discussed in other sections such as events_actions_ and startup_scripts_ but it is useful to provide
a general guide here.

Events can be pushed to the low priority queue by using:

.. code-block:: python

   framework.append_event('my_event', arguments)

Where ``arguments`` is an instance of the ``Arguments`` class described in arguments_.

While there should be no need to do it, we can also send events directly to the high priority queue, by using:

.. code-block:: python

    framework.push_event('my_event', argument)

Pushing events to the high priority queue can disrupt the correct processing sequence. It is used by the framework itself
as part of linking events into recipes as described in pipelines_.
