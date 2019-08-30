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
- `Bokeh`

Installation
============
You can download the code by cloning this repository::

  git clone https://github.com/Keck-DataReductionPipelines/KeckDRPFramework.git

Change directory into the KeckDRPF directory and run::

  python setup.py install

Framework concepts
==================

At its core, the KDRPF is an engine that allows to run arbitrary code on arbitrary objects
without a pre-determined sequence of steps. This section describes the basic concepts upon which the framework is designed.

Primitives
^^^^^^^^^^
The operational code is contained in primitives, which are either functions or classes and are limited to simple,
single-purpose operations. The framework offers a few basic primitives and a template to build your own.
An example of a primitive would be a function that subtract the bias level from a CCD image.

Primitives can be defined in a number of different ways.

The best way to define a primitive is by subclassing the ``Base_primitive`` class, which contains a number of useful
methods. In its full implementation, the ``Base_primitive`` class contains the following methods:

- ``_pre_condition``, which must return ``True`` for the framework to actually execute the code
- ``_perform``, which contains the actual code and should return valid arguments
- ``_post_condition``, which is checked upon completion of the code contained in the ``_perform`` method

The execution of the code contained in a class defined following our template is governed by the ``apply`` method,
which is standard and should not be modified. The apply method works like this::

    def apply (self):
        if self._pre_condition():
            output = self._perform()
            if self._post_condition():
                self.output = output
        return self.output

If a the full check on pre and post conditions is not necessary, a simpler class can be defined by simply preserving the ``__init__``
and the ``_perform`` methods.
An example of a primitive defined this way is a simple FITS reader::

 def open_nowarning (filename):
     with warnings.catch_warnings():
           warnings.simplefilter('ignore', AstropyWarning)
           return pf.open(filename)

 class simple_fits_reader (Base_primitive):
     '''
     classdocs
     '''

     def __init__(self, action, context):
        '''
        Constructor
        '''
        Base_primitive.__init__(self, action, context)

    def _perform (self):
        '''
        Expects action.args.name as fits file name
        Returns HDUs or (later) data model
        '''
        name = self.action.args.name
        self.logger.info (f"Reading {name}")
        out_args = Arguments()
        out_args.name = name
        out_args.hdus = open_nowarning(name)

        return out_args

In this case we are using an externally defined function called ``open_nowarning`` and calling it from within the class. Note that way that the return
arguments are build: first, an instance of the ``Arguments`` class is instantiated, then two properties are defined: ``name`` and ``hdus``. We will describe
the use of arguments in the following section.

If the standard class is used to define a primitive, note that the ``__init__`` method should initialize the ``Base_primitive`` as well. The example above
(the simple FITS reader) shows how to do that, and can be copied and pasted exactly as it is. We will return on the concept of ``action`` and ``context``
later in this document.



Arguments
^^^^^^^^^
The functions contained in the primitives operate on a set of arguments that are automatically passed to the
function by the framework. The function can produce output arguments that the framework will keep in memory,
ready for the next function to pick them up. Our definition of arguments is completely generic: we do not have a
predefined data model. Pipeline developers can use any data model that can be represented by a Python object,
and assign it to the arguments dictionary.




The framework triggers the execution of a function
by triggering an event. As an example, if a function exists that ingests a FITS file into
some sort of complex object and parses the header, such a function would be an event, and the
framework would trigger it upon user request or when a new file appears on a directory being monitored.
Each event can trigger another event if needed.
Another important concept is the context, which is a permanent storage for objects that must
exist during the execution of the framework. Examples of elements that are stored in the
context are: the logging facility and configuration parameters.
Finally, the actual execution of the events is delegated to two queues, a low priority and high priority
queue. The high priority queue contains events that must be run sequentially in specified order.
The low priority queue contains events that don't need to be run immediately, but instead can
wait until the high priority queue is empty. An example: the appearance of a new file on disk, or
maybe multiple files, generate events such as "ingest_file" that will be added to the low priority queue.
If there are events that must follow the file ingestion, such as determining the file type, and possibly
triggering reduction steps, those steps must be run sequentially on the same file, before a new
file is ingested.

Primitives
----------

Reference/API
=============

.. automodapi:: keckdrpframework
