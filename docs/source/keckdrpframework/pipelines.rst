.. _pipelines:

Pipelines
=========
Through the creation of a pipeline, you can make the code that is contained in the primitives available to the framework
so that it can be applied to specific arguments.

Pipelines are created by subclassing the ``Base_pipeline`` class and adding an event table.
In its basic implementation, a pipeline would look like this:

.. code-block:: python

 class MyPipeline(Base_pipeline):
   """
   My own pipeline
   """

   event_table = {
       "my_event_name": ("my_primitive", "my_state", "my_next_event")
       }

   def __init__(self):
       """
       Constructor
       """
       Base_pipeine.__init__(self)

This simple construction tells the framework that there is either a class or a function called ``my_primitive``, and
that it should be run when ``my_event_name`` is triggered. When that code is running, the state of the framework
will be set to ``my_state``. After the execution of the code, the framework would go on to trigger ``my_next_event``
which is currently not defined.

The ``event_table`` is the core of the pipeline: it makes all the code in your primitives available to the
framework through the concept of ``events`` which we will describe in more detail later.

There is a pre-defined event table that is built into the base pipeline class: it contains the operations
that the framework should be doing if no event is present in the execution queue, essentially implementing
the infinite loop that the framework executes while waiting for events.

As an example of a more realistic pipeline, here are some examples taken from the KCWI pipeline:

.. code-block:: python

 event_table = {
        "next_file": ("ingest_file", "file_ingested", "file_ingested"),
        "file_ingested": ("action_planner", None, None),
        # BIAS
        "process_bias": ("process_bias", None, None),
        # CONTBARS PROCESSING
        "process_contbars": ("process_contbars", "contbars_processing_started", "contbar_subtract_overscan"),
        "contbar_subtract_overscan": ("subtract_overscan", "subtract_overscan_started", "contbar_trim_overscan"),
        "contbar_trim_overscan": ("trim_overscan", "trim_overscan_started", "contbar_correct_gain"),
        "contbar_correct_gain": ("correct_gain", "gain_correction_started", "contbar_find_bars"),
        "contbar_find_bars": ("find_bars", "find_bars_started", "contbar_trace_bars"),
        "contbar_trace_bars": ("trace_bars", "trace_bars_started", None),
        # ARCS PROCESSING
        "process_arc": ("process_arc", "arcs_processing_started", "arcs_subtract_overscan"),
        "arcs_subtract_overscan": ("subtract_overscan", "subtract_overscan_started", "arcs_trim_overscan"),
        "arcs_trim_overscan": ("trim_overscan", "trim_overscan_started", "arcs_correct_gain"),
        "arcs_correct_gain": ("correct_gain", "gain_correction_started", "arcs_extract_arcs"),
        "arcs_extract_arcs": ("extract_arcs", "extract_arcs_started", "arcs_arc_offsets"),
        "arcs_arc_offsets":  ("arc_offsets", "arc_offset_started", "arcs_calc_prelim_disp"),
        "arcs_calc_prelim_disp": ("calc_prelim_disp", "prelim_disp_started", "arcs_read_atlas"),
        "arcs_read_atlas": ("read_atlas", "read_atlas_started", "arcs_fit_center"),
        "arcs_fit_center": ("fit_center", "fit_center_started", None)
        }

 def action_planner (self, action, context):
        if action.args.imtype == "BIAS":
            bias_args = Arguments(name="bias_args",
                                  groupid = groupid,
                                  want_type="BIAS",
                                  new_type="MASTER_BIAS",
                                  min_files=context.config.instrument.bias_min_nframes,
                                  new_file_name="master_bias_%s.fits" % groupid)
            context.push_event("process_bias", bias_args)
        elif "CONTBARS" in action.args.imtype:
            context.push_event("process_contbars", action.args)
        elif "FLAT" in action.args.imtype:
            context.push_event("process_flat", action.args)
        elif "ARCLAMP" in action.args.imtype:
            context.push_event("process_arc", action.args)
        elif "OBJECT" in action.args.imtype:
            context.push_event("process_object", action.args)

The ``next_file`` event is triggered when a new file is generated (the description of how to
trigger events will be provided later). This triggers the ``ingest_file`` function, followed by
``action_planner``. Note that ``action planner`` is defined right here, inside the definition of the
pipeline itself. This is another option available to users to define functions (see the primitives section):
the ``action_planner`` function has the only purpose of deciding which event should be triggered based on the
image type, and as such is logically connected with the initial steps of the pipeline. For this reason,
this user found it useful to define it here, rather than in its own library file. From an execution point of
view, this makes no difference.

A pipeline definition file should also import the framework package and all the primitives that the user
has defined. For example, in the case of KCWI and having created a directory called ``primitives``,
the import section might look like this:

.. code-block:: python

 from keckdrpframework.pipelines.base_pipeline import Base_pipeline

 from ..primitives.kcwi_primitives import *

The relative import of the primitives is based on a specific directory structure which will be discussed later.
Any directory structure or packaging system can be used. As long as there is a way to add the primitives to
the namespace, they will be used.


