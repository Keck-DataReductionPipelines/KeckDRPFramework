# Simple examples to show how to communicate with the Queue manager

Note that PYTHONPATH environment variable must be set correctly to run these programs.
For example the parent directory of keckdrpframework must be included in PYTHONPATH.

## start_queue_manager.py
Starts the Queue Manager in the background and exits.
This is useful to run in multiprocessing mode.
Once the queue manager is started, the worker processes can be started and wait for events.

## stop_queue_manager.py
Stopping the Queue Manager effectively stops all the worker processes that use this queue.

## event_queue_info.py
This program simply returns the number of entries in the event queue, which is an indicator of processing progress.

## add_event.py
Addes a new event to the queue. The arguments are event name and event argument.
For example, the event name could be "new_file" and the event argument could be the name of the new file.

# Jupyter notebooks examples

There are two Jupyter notebooks: DRPF-remote-interface.ipynb and Reduce_data.ipynb.

DRPF-remote-interface shows how to communicate with the queue manager.

Reduce_data shows how to run a pipeline in a notebook.