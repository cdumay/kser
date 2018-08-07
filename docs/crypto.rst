:mod:`kser.crypto` --- Message encryption
==========================================

.. py:class:: CryptoMessage(context):

    It's a container which includes the original message as well as the nonce
    required by the consumer to decipher the content

    :param dict context: We use marshmallow context to store the secretbox_key

.. py:method:: CryptoMessage.decode(jdata)

    Encode message using libsodium

    :param kser.schemas.Message kmsg: Kafka message
    :return: the Encoded message

.. py:method:: CryptoMessage.encode(kmsg)

    Decode message using libsodium

    :param str jdata: jdata to load
    :return: the Encoded message


Example usage
-------------

For this example, we'll use `kafka-python <https://github.com/dpkp/kafka-python>`_ as kafka backend.

**Install**:

.. code-block::

    pip install kser[pykafka,crypto]

**Consumer example**:

.. code-block:: python
   :linenos:

    from kser.controller import Controller
    from kser.crypto import CryptoMessage
    from kser.python_kafka.consumer import Consumer


    class CryptoController(Controller):
        TRANSPORT = CryptoMessage


    class CryptoConsumer(Consumer):
        REGISTRY = CryptoController


    if __name__ == '__main__':
        consumer = CryptoConsumer(config=dict(...), topics=list(...))
        consumer.run()

**Producer example**:

.. code-block:: python
   :linenos:

    import os
    from uuid import uuid4

    from cdumay_result import Result
    from kser.crypto import CryptoSchema
    from kser.python_kafka.producer import Producer
    from kser.schemas import Message


    class CryptoProducer(Producer):
        # noinspection PyUnusedLocal
        def send(self, topic, kmsg, timeout=60):
            result = Result(uuid=kmsg.uuid)
            try:
                self.client.send(topic, CryptoSchema(context=dict(
                    secretbox_key=os.getenv("KSER_SECRETBOX_KEY", None)
                )).encode(self._onmessage(kmsg)).encode("UTF-8"))

                result.stdout = "Message {}[{}] sent in {}".format(
                    kmsg.entrypoint, kmsg.uuid, topic
                )
                self.client.flush()

            except Exception as exc:
                result = Result.from_exception(exc, kmsg.uuid)

            finally:
                if result.retcode < 300:
                    return self._onsuccess(kmsg=kmsg, result=result)
                else:
                    return self._onerror(kmsg=kmsg, result=result)


    if __name__ == '__main__':
        producer = CryptoProducer(config=dict(...))
        producer.send("my.topic", Message(uuid=str(uuid4()), entrypoint="myTest"))
