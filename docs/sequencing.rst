==================
Operation and task
==================

Kser provide a way to create and launch operations. An operation is a list of task executed linearly.

.. note::

    Each operation's task may be executed on different consumer.

---------
API focus
---------

.. py:class:: kser.sequencing.task.Task(uuid=None, params=None, status="PENDING", result=None, metadata=None)

    A task is a :class:`kser.entry.Entrypoint` with additional attributes. To do this, use a database as shared backend.

    :param str uuid: task unique identifier
    :param dict params: task parameter
    :param str status: task status
    :param cdumay_result.Result result: forwarded result from a previous task
    :param dict metadata: task context

    .. py:method:: kser.sequencing.task.Task.log(message, level=logging.INFO, *args, **kwargs)

        Send log entry, prefixing message using the following format::

            {TaskName}.{TaskStatus}: {EntryPointPath}[{TaskUUID}]:

        :param str message: log message
        :param int level: `Logging level <https://docs.python.org/3/library/logging.html#levels>`_
        :param list args: log record arguments
        :param dict kwargs: log record key arguments

.. py:class:: kser.sequencing.operation.Operation(uuid=None, params=None, status="PENDING", result=None, metadata=None)

    In fact it's a :class:`kser.sequencing.task.Task` which has other task as child.

    .. py:classmethod:: kser.sequencing.operation.Operation.new(**kwargs)

        .. warning::

            Deprecated, do not use this method anymore.

        Initialize the operation using a :code:`dict`.

        :param dict kwargs: key arguments
        :return: A new operation
        :rtype: kser.sequencing.operation.Operation

    .. py:classmethod:: kser.sequencing.operation.Operation.parse_inputs(**kwargs)

        .. warning::

            Deprecated, do not use this method anymore.

        Use by :code:`kser.sequencing.operation.Operation.new` to check inputs

        :param dict kwargs: key arguments
        :return: parsed input
        :rtype: dict

    .. py:method:: kser.sequencing.operation.Operation.set_status(status, result=None)

        Update operation status

        :param str status: New status
        :param cdumay_result.Result result: Execution result

    .. py:method:: kser.sequencing.operation.Operation.add_task(task)

        Add task to operation

        :param kser.sequencing.task.Task task: task to add

    .. py:method:: kser.sequencing.operation.Operation.prebuild( **kwargs)

        To implement, perform check before the operation creation

        :param dict kwargs: key arguments

    .. py:method:: kser.sequencing.operation.Operation.next(task)

        Find the next task

        :param kser.sequencing.task.Task task: previous task
        :return: The next task
        :rtype: kser.sequencing.task.Task or None

    .. py:method:: kser.sequencing.operation.Operation.launch_next(task=None, result=None)

        Launch next task or finish operation

        :param kser.sequencing.task.Task task: previous task
        :param cdumay_result.Result result: previous task result
        :return: Execution result
        :rtype: cdumay_result.Result

    .. py:method:: kser.sequencing.operation.Operation.launch()

        Send the first task

        :return: Execution result
        :rtype: cdumay_result.Result

    .. py:method:: kser.sequencing.operation.Operation.finalize()

        To implement, post build actions (database mapping ect...)

        :return: Self return
        :rtype: kser.sequencing.operation.Operation

    .. py:method:: kser.sequencing.operation.Operation.build_tasks(**kwargs)

        Initialize tasks

        :param dict kwargs: tasks parameters (~=context)
        :return: list of tasks
        :rtype: list(kser.sequencing.task.Task)

    .. py:method:: kser.sequencing.operation.Operation.compute_tasks(**kwargs)

        Perfrom checks and build tasks

        :return: list of tasks
        :rtype: list(kser.sequencing.operation.Operation)

    .. py:method:: kser.sequencing.operation.Operation.build(**kwargs)

        Create the operation and associate tasks

        :param dict kwargs: operation data
        :return: The operation
        :rtype: kser.sequencing.operation.Operation

    .. py:method:: kser.sequencing.operation.Operation.send()
        
        To implement, send operation to Kafka

        :return: The operation
        :rtype: kser.sequencing.operation.Operation

.. py:class:: kser.sequencing.registry.OperationRegistry(app=None, controller_class=kser.controller.Controller)

    A which route :class:`kser.schemas.Message` from Kafka to the requested :class:`kser.sequencing.operation.Operation`.

    :param flask.Flask app: Flask application if any
    :param kser.controller.Controller controller_class: Controller to use



    .. py:method:: kser.sequencing.registry.OperationRegistry.subscribe(callback)

        Register an :class:`kser.sequencing.operation.Operation` into the controller. This method is a shortcut to :code:`kser.controller.Controller.register`.

        :param `kser.sequencing.task.Task` callback: Any class which implement `Task`.


    .. py:method:: kser.sequencing.registry.OperationRegistry.load_tasks()

        To implement, load operation tasks

-------
Example
-------

The following example is based on a dice game, player roll tree time dices.

Consumer
========

.. code-block:: python
   :linenos:

    import logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s"
    )

    import random

    from cdumay_result import Result
    from kser.sequencing.operation import Operation
    from kser.sequencing.registry import OperationRegistry
    from kser.sequencing.task import Task

    oregistry = OperationRegistry()


    @oregistry.subscribe
    class DiceRoll(Task):
        def run(self):
            launch = random.randint(1, 6)
            return Result(uuid=self.uuid, stdout="You made a {}".format(launch))


    @oregistry.subscribe
    class DiceLaunch(Operation):
        def build_tasks(self, **kwargs):
            return [DiceRoll(), DiceRoll(), DiceRoll()]


    if __name__ == '__main__':
        from flask import Flask
        from kser.python_kafka.consumer import Consumer

        app = Flask(__name__)
        oregistry.init_app(app)
        cons = Consumer(...)
        cons.REGISTRY = oregistry.controller
        cons.run()

**Explanations**:

* **line 13**: We initialize the registry
* **line 16/23**: We subscribe the task/operation into the registry
* **line 35-37**: We start the consumer

Producer
========

Producer has nothing special for this feature.

.. code-block:: python
   :linenos:

    import logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s"
    )

    import uuid
    from kser.python_kafka.producer import Producer
    from kser.schemas import Message

    pro = Producer(...)
    pro.send('...', Message(uuid=str(uuid.uuid4()), entrypoint="__main__.DiceRoll"))

**Explanations**:

* **line 10**: We initialize the producer
* **line 11**: We send a Message with the entrypoint `__main__.DiceRoll` that matches our Task registred

Execution
=========

**Producer console output**::

    2018-08-10 18:46:20,082 INFO     <BrokerConnection host=************/************ port=9093>: Authenticated as admin
    2018-08-10 18:46:20,549 INFO     Broker version identifed as 0.10
    2018-08-10 18:46:20,550 INFO     Set configuration api_version=(0, 10) to skip auto check_version requests on startup
    2018-08-10 18:46:20,711 INFO     <BrokerConnection host=************/************ port=9093>: Authenticated as admin
    2018-08-10 18:46:20,731 INFO     Producer.Success: __main__.DiceRoll[872c3be0-51ac-457f-a4d9-12c2f7667b80]: Message __main__.DiceRoll[872c3be0-51ac-457f-a4d9-12c2f7667b80] sent in *****
    2018-08-10 18:46:20,731 INFO     Closing the Kafka producer with 999999999 secs timeout.
    2018-08-10 18:46:20,741 INFO     Kafka producer closed

**Consumer console output**::

    2018-08-10 18:44:42,355 INFO     Operation registry: loaded __main__.DiceRoll
    2018-08-10 18:44:42,355 INFO     Operation registry: loaded __main__.DiceLaunch
    2018-08-10 18:44:42,696 INFO     <BrokerConnection host=************/************ port=9093>: Authenticated as admin
    2018-08-10 18:44:43,163 INFO     Broker version identifed as 0.10
    2018-08-10 18:44:43,163 INFO     Set configuration api_version=(0, 10) to skip auto check_version requests on startup
    2018-08-10 18:44:43,164 INFO     Updating subscribed topics to: ['*****']
    2018-08-10 18:44:43,165 INFO     Consumer.Starting...
    2018-08-10 18:44:43,182 INFO     Group coordinator for ***** is BrokerMetadata(nodeId=114251126, host='************', port=9093, rack=None)
    2018-08-10 18:44:43,182 INFO     Discovered coordinator 114251126 for group *****
    2018-08-10 18:44:43,182 INFO     Revoking previously assigned partitions set() for group *****
    2018-08-10 18:44:43,182 INFO     (Re-)joining group *****
    2018-08-10 18:44:46,230 INFO     Skipping heartbeat: no auto-assignment or waiting on rebalance
    2018-08-10 18:44:46,249 INFO     Joined group '*****' (generation 2) with member_id kafka-python-1.3.1-db5cdcc7-3be9-4cf6-a4e7-06a97cc69120
    2018-08-10 18:44:46,249 INFO     Elected group leader -- performing partition assignments using range
    2018-08-10 18:44:46,268 INFO     Successfully joined group ***** with generation 2
    2018-08-10 18:44:46,268 INFO     Updated partition assignment: [TopicPartition(topic='*****', partition=0), TopicPartition(topic='*****', partition=1), TopicPartition(topic='*****', partition=2)]
    2018-08-10 18:44:46,269 INFO     Setting newly assigned partitions {TopicPartition(topic='*****', partition=0), TopicPartition(topic='*****', partition=1), TopicPartition(topic='*****', partition=2)} for group *****
    2018-08-10 18:46:20,750 INFO     DiceRoll.Success: __main__.DiceRoll[872c3be0-51ac-457f-a4d9-12c2f7667b80]: You made a 1
    2018-08-10 18:46:20,751 INFO     Controller.Success: __main__.DiceRoll[872c3be0-51ac-457f-a4d9-12c2f7667b80]: You made a 1

As we can see, the task __main__.DiceRoll is sent by the producer and executed by the consumer with the stdout "You made a 1"