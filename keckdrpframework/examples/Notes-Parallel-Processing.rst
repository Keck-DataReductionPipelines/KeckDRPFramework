Introduction
============

The DRPF has the option to in single-processing or multi-processing
mode. In both cases, the execution of the primitives is triggered by
events, which are stored in the event queue. In single-processing mode,
the framework takes one event out of the event queue, finds the
corresponding action and executes the associated primitive. Once the
primitive is completed, the framework takes another event from the event
queue and repeats until the event queue is empty. Primitives can add
events to another queue, the high priority event queue. The framework
always takes events from this high priority event queue first, before
working with the regular event queue. This allows the primitives to
control the sequence of processing depending on the input data or on the
result of an operation.

In multi-processing mode, the event queue is replaced by an
implementation that can be shared by multiple processes. In
multi-processing mode, multiple DRP framework processes can be started.
Each one runs a processing loop in one thread. A DRPF process can
execute only one primitive at a time. Parallelism is achieved by having
multiple DRPF processes running simultaneously. These DRPF processes
share a common event queue, which is hosted by the DRPF process that is
started first.

Queue Manager
=============

The multi-processing event queue must be created first before it can be
shared amongst processes. The process that creates this event queue is
called the Queue Manager, which is a subclass of the BaseManager from
the module multiprocessing. Processes that want to access the event
queue connect to the Queue Manager and request a reference to the queue.
This reference is an object that looks, feels and acts like a regular
queue although it may be hosted by a remote process running on a remote
host.

In multi-processing mode, a DRP framework process starts and connects to
the Queue Manager. If the connection fails, the process starts the Queue
Manager. In other words, the first DRP process always becomes the Queue
Manager.

The Queue Manager only provides access to one single event queue. DRP
framework processes instantiate their own high priority queue, which is
not shared.

Queue Manager vs Multiprocessing Queue
--------------------------------------

The multiprocessing module also provides an implementation of a Queue.
This Queue differs from the Queue Manager in that the former must be
used with the fork/spawn method of creating children processes. The
Queue Manager allows the Worker processes to be started separately, on
demand, and on a remote host.

Managers and Workers
====================

In single-processing mode, the event queue must be filled either at
startup or periodically through a separate thread (for example via
data_set), and the framework handles one event at a time. In
multi-processing mode, the tasks of filling the event queue and handling
the events can be assigned to separate processes.

Managers are the processes that fill the event queue, while Workers are
processes that handle the events. In normal operations, there will be
more Workers than Managers, usually one Manager. The Queue Manager does
not have to be a Manager. A process can be Manager and Worker at the
same time. Once a pool of Workers is started, the number of Workers does
not have to be constant. More Workers can be added to the pool or
removed from the pool depending on resources or demand.

Work Scenarios
==============

Single Process
--------------

A single process can work in multi-processing mode, where the process is
the Queue Manager, Manager and Worker. From the operation point of view,
there is no difference between this mode and the single-processing mode.

One Manager – Multiple Workers
------------------------------

A DRPF process is started in multi-processing mode and pre-fills the
event queue. As in the single process case, this process starts hanlding
the events. New DRPF Worker processes can be started. These Workers
connect to the first process and start handling the events in parallel.

The first process is the Queue Manager, Manager, and Worker. The other
processes are Workers.

Multiple Managers – Multiple Workers
------------------------------------

A DRPF process is started in multi-processing mode but does not fill the
event queue. Worker processes are started with the “wait_for_event”
option.

A new DRPF process is started with the “ingest_data_only” option. This
process fills or adds new items to the event queue and terminates. The
waiting processes now can start handling the events.

Multiple data ingesting processes can be started, for example monitoring
different directories or data streams. They do not need to run
continuously, can started and stopped manually on demand.

Queue Manager, Manager, and Workers
-----------------------------------

A DRPF process can start as Queue Manager only. This process does not
handle events. Its only purpose is to host the event queue. Data
ingesting processes can start separately. Worker processes can start
when computing resources become available.

Starting and Stopping Workers
-----------------------------

Once a pool of DRPF process is started, the Queue Manager must remain
running. If the Queue Manager stops, all the Worker processes will also
stop when they fail to access the event queue.

There are two options to determine how Worker processes terminate. The
no_event_event option in the configuration determines whether to
terminate or to wait for new events. Workers can also be started with
the “continuous” option. If a Worker is continuous, it will not
terminate when the event queue is empty. If the continuous option is not
set, the no_event_event in the configuration determines how the process
terminates.

Workers can be started with the “wait_for_event” option. This means that
a Worker will probe the event queue for new events. This is useful for
adding additional Workers when the work load is expected to increase.
These temporary Workers can terminate when the work is done.

To summarize the options:

-  On demand Workers:

   -  | wait_for_event=False, continuous=False,non_event_event=None:
      | If event queue is empty, process terminates.
      | Otherwise handle events until no more events, then terminate

   -  | wait_for_event=True, continuous=False:
      | Wait for event, then handle event until no more events, then
        terminate.

-  Long term Workers:

   -  | continuous=True
      | Workers do not terminate. They must be killed explicitly.

Configuration
=============

The configuration option want_multiprocessing determines the mode. The
permitted values are:

-  True: multi-processing mode

-  False: single-processing mode

When want_multiprocessing=True, the following options are needed:

-  queue_manager_hostname = “hostname”, ie “myserver”

-  queue_manager_portnr = Port_number, ie 50101

-  queue_manager_auth_code = “authorization code”, ie b”This is a code”

Note 1 : Avoid using “localhost” as hostname because all communication
will be limited to the local host and no remote hosts will be able to
connect. Use the actual host name instead.

Note 2: The port number is arbitrary. Choose a port number that is not
already reserved in your environment. Same applied to the authorization
code.

Examples
========

The directory examples in the repository provides a simple pipeline to
demonstrate the capability of the framework. This simple pipeline
produces a PNG file for each input FITS file listed in the command line
or in the given directory. There two Python scripts: test_harness.py and
test_harness2.py. They differ in the way how the pipeline class is
created, test_harness2 is hardware to start the example pipeline. while
test_harness needs the name of the pipeline to start. Otherwise they
have the same options.

The shell script runTest_harness.sh provides a convenient way to start
the Python script.

test_harness2.py [-w] [-W] [-s] [-i] [-c config_file] [file [files ...]]|[-d
dirname]

The options are:

   -w, --wait_for_event: True or False

   -W, --continue: True or False

   -s, --start_queue_manager_only: True or False

   -i, --ingest_data_only: True or False

   -d, --directory: directory name

   -c, --config config_file: name of configuration file

   file [files]: names of FITS files to process

For the examples, the 6 FITS files in the directory
unit_tests/test_files will be used.

Test 1
------

This is the simplest case where only one process is involved.

First, confirm that the flag want_multiprocessing is True and
no_event_event is None in the configuration file, config.cfg.

sh runTest_harness2.sh -c config.cfg –d ../unit_test/test_files

This test produces 6 PNG files in the output directory corresponding to
the 6 FITS files in the ../unit_test/test_files directory. The program
terminates after processing the files.

Test 2
------

One Queue Manager and one Worker.

Start Queue Manager only:

sh runTest_harness2.sh –s -c config.cfg

This process starts the Queue Manager and nothing else.

On the same host or on a remote host run the following command:

sh runTest_harness2.sh -c config.cfg –d ../unit_test/test_files

This process communicates with the Queue Manager to access the event
queue. This process terminates also.

Test 3
------

One Queue Manager, one Manager and Workers.

Start Queue Manager only:

sh runTest_harness2.sh –s -c config.cfg

On one host, run with ingest_data_only option. The process will
terminate once all files are ingested.

sh runTest_harness2.sh–i -c config.cfg –d ../unit_test/test_files

On the same host or on a remote host, run one or more Worker processes:

sh runTest_harness2.sh -c config.cfg

Note that because there only 6 FITS files, the processing is quick. Try
to provide an alternative directory with more files to appreciate the
parallel processing.

Test 4
------

One Queue Manager, Workers start first and one Manager.

Start Queue Manager only:

sh runTest_harness2.sh –s -c config.cfg

On one host, run with wait_for_event option. This process will wait for
events and will terminate when there are no more events.

sh runTest_harness2.sh –w -c config.cfg

On the same host or on a remote host, ingest data only:

sh runTest_harness2.sh –i –d ../unit_test/test_files -c config.cfg

References
==========

1. Python threading module documentation

2. Python multiprocessing module documentation
