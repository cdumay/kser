Prometheus export
=================

Kser support `prometheus <https://prometheus.io/>`_ metric export.

Install
-------

    $ pip install kser[prometheus]

Configuration
-------------

Configuration is done using environment variable:

.. table:: Configuration variables
   :widths: auto

   ======================= ================
     Environment variable   Default value  
   ======================= ================
     KSER_METRICS_ENABLED   no             
     KSER_METRICS_ADDRESS   0.0.0.0        
     KSER_METRICS_PORT      8888           
   ======================= ================

The exporter has only 2 metrics defined by default, it's just a sample. A good
way to implement your own is to override the triggers methods (prefixed with '_') like the following example:

.. code-block:: python
   :linenos:

    from kser import KSER_METRICS_ENABLED
    from prometheus_client import Counter
    from kser.entry import Entrypoint

    MY_METRIC = Counter('kser_my_metric', 'a usefull metric')


    class MyEntrypoint(Entrypoint):
        def _run(self):
            if KSER_METRICS_ENABLED == "yes":
                MY_METRIC.inc()

            return self.run()

.. seealso::

   `prometheus_client <https://github.com/prometheus/client_python>`_
      Prometheus instrumentation library for Python applications.