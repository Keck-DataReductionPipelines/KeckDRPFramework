Plotting with Bokeh
======================================

Because the framework runs in a thread, it might be diffcult to plot directly with Matplotlib.

A solution is to use Bokeh, which is thread-safe.

An implementation of this solution is offered by the framework using the bokeh_plotting import.

To plot with bokeh, start by adding a special event to your pipeline event table::


 from ..primitives.start_bokeh import start_bokeh

 class mypipeline(BasePipeline):
    """
    Generic pipeline

    """

    event_table = {
        "start_bokeh": ("start_bokeh", None, None)
    }


The special event is described in a primitive that we will call start_bokeh.py::

 from keckdrpframework.primitives.base_primitive import BasePrimitive

 from bokeh.client import push_session
 from bokeh.io import curdoc
 from bokeh.plotting.figure import figure
 from bokeh.layouts import column



 class start_bokeh(BasePrimitive):

     def __init__(self, action, context):
         '''
         Constructor
         '''
         BasePrimitive.__init__(self, action, context)


     def _perform(self):

         self.logger.info("Enabling BOKEH plots")

         self.context.bokeh_session = push_session(curdoc())
         p = figure()
         c = column(children=[p])
         curdoc().add_root(c)
         self.context.bokeh_session.show(c)

This special event can be then triggered immediately by your startup script and added to the high priority queue::

 subprocess.Popen('bokeh serve', shell=True)
 framework.append_event('start_bokeh', None)

Plotting
^^^^^^^^

The actual plotting is performed by the primitives.

As an example::

 from bokeh.plotting import figure
 from bokeh.models import Range1d
 from bokeh.models.markers import X
 from bokeh.io import curdoc
 from bokeh.util.logconfig import basicConfig, bokeh_logger as bl
 from keckdrpframework.core.bokeh_plotting import bokeh_plot

 class make_a_plot(BasePrimitive):

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        basicConfig(level=logging.ERROR)

    def _perform(self):
        # process something and then make a plot
        x = np.arange(10)
        y = x**2
        p = figure(title="Test")
        p.line(x, y)
        bokeh_plot(p)

