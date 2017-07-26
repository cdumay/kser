.. kser documentation master file, created by
   sphinx-quickstart on Wed Jul 26 12:28:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

********************************
Welcome to kser's documentation!
********************************

Kser is a Kafka lib to serialize and deserialize Message in Kafka.

.. image::
   _static/kser.png

Workflow:

* **1**: A new entry is ack by the consumer
* **2**: Raw data is deserialized as :class:`kser.transport.Message`.
* **3**: Message is routed to the :class:`kser.entry.Entrypoint` set in ``message.entrypoint`` using the :attr:`kser.consumer.Consumer.REGISTRY`.
* **4**: Entrypoint execution return a :class:`kser.result.Result`.
* **5**: Router result may sent the result to Python code (**5a**) or sent it to Kafka via the Producer in a :class:`kser.transport.Message` object (**5b**).

.. toctree::
   :maxdepth: 2
   :caption: API focus:

   consumer
   controller
   transport
   entry
   result
   producer



******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
