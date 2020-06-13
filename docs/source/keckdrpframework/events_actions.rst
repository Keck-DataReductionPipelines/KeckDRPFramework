.. _events_actions:

Events and Actions
==================

Events
------

A pipeline is defined by creating an event table, linking ``events`` to
the corresponding class or code (see pipelines_).

To define an event, we need to specify the following four elements: ``name``, ``action``, ``state``, and
``next event``.

The ``name`` is arbitrary and is the only connection between the pipeline, the framework and the corresponding
code. This means that there is no way to directly call a function or a class other than by the ``name``
associated with it.

The ``state`` is arbitrary. While not widely used yet, it can be used to control the flow of the
pipeline. For now, it is sufficient to know that once an event is triggered, the special variable ``context.state``
will be set to the value specified in this field.

The ``next event`` array element is used to create automatic chains of events, if that is desired. For example,
if you are creating a basic CCD reduction pipeline, you could write events like this:

.. code-block:: python

 event_table = {
    "correct_bias":    ("subtract_bias", "bias_processing", "correct_overscan"),
    "correct_overscan: ("fit_and_sub_overscan", "overscan_processing", "correct_flat"),
    "correct_flat":    ("fit_and_div_flat", "flat_processing", None)
    }

If ``correct_bias`` is triggered, the framework would automatically proceed to trigger ``correct_overscan``,
and continue with ``correct_flat``. At this point, the framework would encounter the event ``None`` and
would not proceed further.
The variable ``context.state`` would change value from ``bias_processing`` to ``overscan_processing`` to
``flat_processing``.

Actions
-------

The ``Base_pipeline`` offers a method to convert an ``Event`` into an ``Action``.

This operation searches the namespace for classes or functions that match the ``action``
field of the ``event`` that has been triggered, and sends the resulting code to the framework for execution.

The actual execution depends on how the code is defined. If the code is contained in a class the framework
would look for ``pre`` and ``post`` conditions and run the ``apply`` method if it is defined.

See primitives_ for further information.