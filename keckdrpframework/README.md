# Keck DRP Framework source code directory

The sub-directories:
- config
- core
- models
- pipelines
- utils
- unit_tests

contain the source code of the DRP framework.

The sub-directories
- examples
- templates

contain supplemental code for testing and documentation.

The sub-directory 'examples' contains a very simple pipeline.

The sub-directory 'templates' contains a skeleton of a pipeline that can be used to start a new pipeline.

Copies of the configuration file 'config.cfg' and the logger configuration file 'logger.cfg' are provided in 'examples' and 'templates'.
These configuration files may need to be modified when developing or testing in a new environment.

Similarly, the start-up scripts runTest\_harness.sh and runTest\_template.sh need to be adapted for the actual Python environment.

See templates/make_copy.sh to create a new skeleton pipeline.
 

