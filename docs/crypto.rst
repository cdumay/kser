:mod:`kser.crypto` --- Message encryption
==========================================

This module allow you to encrypt and decrypt messages in kafka

Install
-------

    pip install kser-crypto[pykafka]

API focus
---------

.. py:class:: kser.crypto.CryptoMessage(context):

    It's a container which includes the original message as well as the nonce
    required by the consumer to decipher the content

    :param dict context: We use marshmallow context to store the secretbox_key

   .. py:method:: kser.crypto.CryptoMessage.decode(jdata)

       Encode message using libsodium

       :param kser.schemas.Message kmsg: Kafka message
       :return: the Encoded message

   .. py:method:: kser.crypto.CryptoMessage.encode(kmsg)

       Decode message using libsodium

       :param str jdata: jdata to load
       :return: the Encoded message


Example
-------

For this example, we'll use `kafka-python <https://github.com/dpkp/kafka-python>`_ as kafka backend.

.. note::

   Make sure to have the environment variable **KSER_SECRETBOX_KEY** definded.

**Consumer example**:

.. code-block:: python
   :linenos:

    from kser_crypto.python_kafka.consumer import CryptoConsumer

    consumer = CryptoConsumer(config=dict(...), topics=[...])
    consumer.run()

**Producer example**:

.. code-block:: python
   :linenos:

    import time
    from uuid import uuid4
    from kser.schemas import Message
    from kser_crypto.python_kafka.producer import CryptoProducer

    producer = CryptoProducer(config=dict(...))
    producer.send("test", Message(uuid=str(uuid4()), entrypoint="myTest"))
    time.sleep(1)
