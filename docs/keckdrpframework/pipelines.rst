Pipelines
=========
Through the creation of a pipeline, you can make the code that is contained in the primitives available to the framework
so that it can be applied to specific arguments.

Pipelines are created by subclassing the ``Base_pipeline`` class and adding an event table.
In its basic implementation, a pipeline would look like this::

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
should be set to ``my_state``. After the execution of the code, the framework would go on to trigger ``my_next_event``
which is currently not defined.
