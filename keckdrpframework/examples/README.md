# Examples

This directory contains examples of pipelines.
   - fits2png_pipeline


## How to run

The Python script test_harness.py is a simple program to start and test the pipelines.
The name of the pipeline is passed as a parameter. The test harness tries to find the pipeline
in the directories listed in the configuration file, see __pipeline_path__.

The test harness assumes that a directory or a list of files is given. 
These files are then appended to the event queue for processing. 

runTest_harness.sh is a simple wrapper to help test the pipelines. 
It sets the necessary environment variables for the right version of Python.

      runTest_harness.sh pipeline_name config_file files ...
      
      or
      
      runTest_harness.sh pipeline_name config_file -d dirname
      
For example:

      runTest_harness fits2png_pipeline config.cfg -d ../unit_tests/ 


When multi-processing is desired, there more options.
First, a Queue manager process must be started that manages a shared queue for all consumers/clients.
These consumers/clients can run on the same host or different hosts.


