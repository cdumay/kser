#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from confluent_kafka import Producer as ConfluentProducer
from kser import BaseTransportSerializer
from cdumay_result import Result

logger = logging.getLogger("kser")


class Producer(BaseTransportSerializer):
    def __init__(self, config):
        """ Create new Producer instance using provided configuration dict.

        :param dict config: configuration
        """
        cfg = {
            'ssl.ca.location': '/etc/ssl/certs',
            'security.protocol': 'sasl_ssl',
            'api.version.request': True,
            'sasl.mechanisms': "PLAIN"
        }
        cfg.update(config or dict())
        self.client = ConfluentProducer(cfg)

    def send(self, topic, kmsg):
        """ Send the message into the given topic

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsg: Message to serialize
        :return: Execution result
        :rtype: kser.result.Result
        """
        try:
            self.client.produce(topic, self._onmessage(kmsg).dumps())
            self.client.flush()

            result = Result(
                uuid=kmsg.uuid, stdout="Message sent: {} ({})".format(
                    kmsg.uuid, kmsg.entrypoint
                )
            )

        except Exception as exc:
            result = Result.fromException(exc, kmsg.uuid)

        finally:
            if result.retcode < 300:
                return self._onsuccess(kmsg=kmsg, result=result)
            else:
                return self._onerror(kmsg=kmsg, result=result)
