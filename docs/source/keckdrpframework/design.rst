.. _design:

Design and basic concepts
=========================

This section describes the core ideas behind the design and implementation of the framework.

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
for a science frame (``remove_overscan``, ``trim_overscan``, ``subtract_bias``, ``apply_flat_field``, ``apply_lambda_calib``
and so on). If a directory contains a number of files, the LPQ would immediately be filled
by calls to the ingestion events for each of the file. As the framework starts to process them, the linked events
would temporarily fill up the HPQ with the processing steps, and the framework would process them before
moving on to the next file. An exception to this is the multiprocessing mode which is described later.


