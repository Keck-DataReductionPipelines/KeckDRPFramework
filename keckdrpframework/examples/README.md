# Examples

This directory contains examples of pipelines.
   - fits2png_pipeline


### Before running

- Please review the configuration file `config.cfg`.
- There are 6 FITS files in the directory ../unit_tests/test_files that can be used for testing.
- Output directory is defined in the configuration, see option `output_directory`, default is "output".
- This example reads the test files and generates PNG files and saves them in the output directory.
- To test multi-processing, it recommended to use more test files, for example more than 50 files.


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

      runTest_harness.sh fits2png_pipeline config.cfg -d ../unit_tests/test_files 


When multi-processing is desired, there are more options.
First, a Queue manager process must be started that manages a shared queue for all consumers/clients.
These consumers/clients can run on the same host or on different hosts.

The option that enables multiprocessing is `want_multiprocessing = True` in the configuration file, see `config.cfg`.
When enabled, there other options that need to be defined and adapted for your environment:
   -  queue_manager_hostname = "localhost"
   -  queue_manager_portnr = 50101
   -  queue_manager_auth_code = b"a very long authentication code" 

