:mod:`kser.entry` --- Entries
=============================

.. py:class:: kser.entry.Entrypoint(uuid=None, params=None, result=None)

    An entrypoint is the code which will be registred in the controller to
    handle execution.

    :param str uuid: An unique identifier.
    :param dict params: Entrypoint parameters
    :param cdumay_result.Result result: previous task result

   .. py:attribute:: kser.entry.Entrypoint.REQUIRED_FIELDS

       Tuple or list of keys required by the entrypoint.

   .. py:method:: kser.entry.Entrypoint.check_required_params()

       Perform a self test. It can be used to check params received, states...
       By default, this method check the presence of each item stored in
       :py:attr:`kser.entry.Entrypoint.REQUIRED_FIELDS` in the `kser.entry.Entrypoint.params` dictionnary.

   .. py:method:: kser.entry.Entrypoint.execute(result=None)

       The main method used to launch the entrypoint execution. This method is
       execption safe. To execute an entrypoint without catching execption uses :py:meth:`kser.entry.Entrypoint.unsafe_execute`.

       :param cdumay_result.Result result: Previous task result
       :return: The execution result
       :rtype: cdumay_result.Result

   .. py:classmethod:: kser.entry.Entrypoint.from_Message(kmsg)

       Initialize the entrypoint from a :class:`kser.schemas.Message`

       :param kser.schemas.Message kmsg: A message received from Kafka.
       :return: The entrypoint
       :rtype: kser.entry.Entrypoint

   .. py:method:: kser.entry.Entrypoint.log(message, level=logging.INFO, *args, **kwargs)

       Adds entrypoint information to the message and sends the result to `logging.log <https://docs.python.org/3.5/library/logging.html?#logging.Logger.log>`_.

       :param str message: message content
       :param int level: `Logging Level <https://docs.python.org/3.5/library/logging.html?#logging-levels>`_
       :param list args: Arguments which are merged into msg using the string formatting operator.
       :param dict kwargs: Keyword arguments.

   .. py:method:: kser.entry.Entrypoint.onerror(result)

       Trigger call on execution error.

       :param cdumay_result.Result result: Current execution result that led to the error.
       :return: Return back the result
       :rtype: cdumay_result.Result

   .. py:method:: kser.entry.Entrypoint.onsuccess(result)

       Trigger call on execution success.

       :param cdumay_result.Result result: Current execution result that led to the success.
       :return: Return back the result
       :rtype: cdumay_result.Result

   .. py:method:: kser.entry.Entrypoint.postinit()

       Trigger call on execution post initialization.

       :param cdumay_result.Result result: Current execution result that led to the success.
       :return: Return back the result
       :rtype: cdumay_result.Result

   .. py:method:: kser.entry.Entrypoint.postrun(result)

       Trigger call on execution post run. This trigger is called regardless of execution result.

       :param cdumay_result.Result result: Current execution result.
       :return: Return back the result
       :rtype: cdumay_result.Result

   .. py:method:: kser.entry.Entrypoint.prerun()

       Trigger call before the execution.

   .. py:method:: kser.entry.Entrypoint.run()

       The entrypoint body intended to be overwrite.

   .. py:method:: kser.entry.Entrypoint.to_Message(result=None)

       Serialize an entrypoint into a :class:`kser.schemas.Message`.

       :param cdumay_result.Result result: Execution result.
       :return: Return a message.
       :rtype: kser.schemas.Message

   .. py:method:: kser.entry.Entrypoint.unsafe_execute(result=None)

       Unlike :py:meth:`kser.entry.Entrypoint.execute` this method launch the entrypoint execution without catching execption.

       :param cdumay_result.Result result: Previous task result
       :return: The execution result
       :rtype: cdumay_result.Result

Example usage
-------------

Let's define a basic entrypoint:

.. code-block:: python
   :linenos:

     import logging
     from kser.entry import Entrypoint
     from cdumay_result import Result

     logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s"
     )
     
     class Hello(Entrypoint):
         REQUIRED_FIELDS = ['name']

         def run(self):
             return Result(
                 uuid=self.uuid, stdout="Hello {name} !".format_map(self.params)
             )

Execution result:

.. code-block:: python

    >>> Hello(params=dict(name="Cedric")).execute()
    2018-02-21 18:26:46,762 DEBUG    Hello.PreRun: __main__.Hello[d455cba6-b329-4d2d-a4e5-1fc2a0ff2781]
    2018-02-21 18:26:46,762 DEBUG    Hello.Run: __main__.Hello[d455cba6-b329-4d2d-a4e5-1fc2a0ff2781]
    2018-02-21 18:26:46,762 DEBUG    Hello.PostRun: __main__.Hello[d455cba6-b329-4d2d-a4e5-1fc2a0ff2781]
    2018-02-21 18:26:46,763 INFO     Hello.Success: __main__.Hello[d455cba6-b329-4d2d-a4e5-1fc2a0ff2781]: Hello Cedric !

Has we can see there is a required parameter `name`. Let's see what's happen if we didn't set it:

.. code-block:: python

    >>> Hello().execute()
    2018-02-21 18:35:47,493 DEBUG    Hello.PreRun: __main__.Hello[f581fb61-0de1-489c-a0df-2c03ce1d35b4]
    2018-02-21 18:35:47,495 ERROR    Hello.Failed: __main__.Hello[f581fb61-0de1-489c-a0df-2c03ce1d35b4]: Missing parameter: name

What's happen if we uses :py:meth:`kser.entry.Entrypoint.unsafe_execute` instead of :py:meth:`kser.entry.Entrypoint.execute`:

.. code-block:: python

    >>> Hello().unsafe_execute()
    2018-02-21 18:39:23,522 DEBUG    Hello.PreRun: __main__.Hello[6aa38be5-cd82-441b-8853-318545a053ad]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/opt/kser/src/kser/entry.py", line 220, in unsafe_execute
        self._prerun()
      File "/opt/kser/src/kser/entry.py", line 147, in _prerun
        self.check_required_params()
      File "/opt/kser/src/kser/entry.py", line 54, in check_required_params
        raise ValidationError("Missing parameter: {}".format(param))
    cdumay_rest_client.exceptions.ValidationError: Error 400: Missing parameter: name (extra={})

.. seealso::

    `cdumay-result <https://github.com/cdumay/cdumay-result>`_
        A basic lib to serialize exception results.

    `cdumay-rest-client <https://github.com/cdumay/cdumay-rest-client>`_
        A basic REST client library.
