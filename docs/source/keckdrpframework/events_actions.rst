.. _events_actions:

Events and Actions
==================

Events
^^^^^^

As described in the previous section, a pipeline is defined by creating an event table, linking ``events`` to
the corresponding class or code.

To define an event, you need to specify the following four elements: ``name``, ``action``, ``state``, and
``next event``.

The ``name`` is arbitrary and is the only connection between the pipeline, the framework and the corresponding
code. This means that there is no way to directly call a function or a class other than by the ``name``
associated with it. For specific purposes, different names can be associated with the same function, by
creating two or more different events: in this case, the ``action`` would be the same, but the ``name`` would be
different. The ``state`` and ``next event`` could either be the same or be different.

The ``state`` is arbitrary. While not fully implemented yet, it can be used to control the flow of the
pipeline. For now, it is sufficient to know that once an event is triggered, the special variable ``context.state``
will be set to the value specified in this field.

The ``next event`` is used to create automatic chains of events, if that is desired. For example,
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
^^^^^^^

One of the basic functions of the ``Base_pipeline`` is to offer a method to convert an ``Event`` into
an ``Action``.

This operation is the one that searches the namespace for classes or functions that match the ``action``
field of the ``event`` that has been triggered, and sends the resulting code to the framework for execution.

The actual execution depends on how the function was declared, but in the most general form the framework
would look for ``pre`` and ``post`` conditions and run the ``apply`` method if it is defined.

