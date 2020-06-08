.. _primitives:

Primitives
==========
The operational code is contained in primitives, which are either functions or classes and are limited to simple,
single-purpose operations. The framework offers a few basic primitives and a template to build your own.
An example of a primitive would be a function that subtract the bias level from a CCD image.

Primitives can be defined in a number of different ways.

Primitives as classes
^^^^^^^^^^^^^^^^^^^^^

The best way to define a primitive is by subclassing the ``Base_primitive`` class, which contains a number of useful
methods. In its full implementation, the ``Base_primitive`` class contains the following methods:

- ``_pre_condition``, which must return ``True`` for the framework to actually execute the code
- ``_perform``, which contains the actual code and should return valid arguments
- ``_post_condition``, which is checked upon completion of the code contained in the ``_perform`` method

The execution of the code contained in a class defined following our template is governed by the ``apply`` method,
which is standard and should not be modified. The apply method works like this:

.. code-block:: python

    def apply (self):
        if self._pre_condition():
            output = self._perform()
            if self._post_condition():
                self.output = output
        return self.output

If a the full check on pre and post conditions is not necessary, a simpler class can be defined by simply preserving the ``__init__``
and the ``_perform`` methods.
An example of a primitive defined this way is a simple FITS reader:

.. code-block:: python

 def open_nowarning (filename):
    with warnings.catch_warnings():
       warnings.simplefilter('ignore', AstropyWarning)
       eturn pf.open(filename)

 class simple_fits_reader (Base_primitive):
     """
     classdocs
     """

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

Note that once the class is defined, it must be made available to the pipeline. This means that the class must be defined
in a module or library or regular Python file that can be imported. See the paragraph about directory structure
for a suggestion on the proper location for primitives.

Primitives as functions
^^^^^^^^^^^^^^^^^^^^^^^
For simple operations, functions can be used to define primitives instead of classes. In this case, there are
no fixed rules as to how the arguments are passed to the function. Functions can be defined directly within the
definition of a pipeline (see pagraph about pipelines) or in their own file, as long as the file can be imported and
the function added to the namespace.






