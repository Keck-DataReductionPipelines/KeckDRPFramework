********************************
Keck DRP Framework Documentation
********************************

This is the documentation for Keck Data Reduction Pipeline Framework package (KDRPF).

KDRPF is a general framework capable of running data reduction pipelines developed specifically
for Keck instruments, but it can be used to run any type of data reduction pipelines.

It has been developed by the WMKO Data Reduction Project.

This document shows how to install the package, describes the key concepts behind the framework,
and shows the steps necessary to run or develop a pipeline.

Requirements
============

KDRPF has the following requirements:

- `Astropy`
- pandas

Installation
============
You can download the code by cloning this repository::

  git clone https://github.com/Keck-DataReductionPipelines/KeckDRPFramework.git

Change directory into the KeckDRPF directory and run::

  pip install .

If you want to install the Keck DRP Framework for development purposes, you can run::

  pip install -e .

to install it in editable mode.

Note that you will download the ``develop`` branch, which is the default branch.
To switch to the ``master`` branch, use:

.. code-block:: bash

   git checkout -b master --track origin/master


Framework design and concepts
=============================

.. toctree::
   :maxdepth: 1

  keckdrpframework/design.rst
  keckdrpframework/startup_scripts.rst
  keckdrpframework/primitives.rst
  keckdrpframework/arguments.rst
  keckdrpframework/pipelines.rst
  keckdrpframework/events_actions.rst
  keckdrpframework/plotting_bokeh.rst
  keckdrpframework/template_pipeline.rst


Reference API
=============

.. toctree::
   :maxdepth: 1

  keckdrpframework/framework_api

