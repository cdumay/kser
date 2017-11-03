#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import json

from kafka import KafkaProducer
from kser import BaseTransportSerializer
from cdumay_result import Result


class Producer(BaseTransportSerializer):
    def __init__(self, config):
        """ Create new Producer instance using provided configuration dict.

        :param dict config: configuration
        """
        self.client = KafkaProducer(**config)

    def bulk_send(self, topic, kmsgs, timeout=60):
        """ Send a batch of messages

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsgs: Messages to serialize
        :param int timeout: Timeout in seconds
        :return: Execution result
        :rtype: kser.result.Result
        """

        try:
            for kmsg in kmsgs:
                self.client.send(
                    topic, self._onmessage(kmsg).dumps().encode("UTF-8")
                )
            self.client.flush(timeout=timeout)
            return Result(stdout="{} message(s) sent".format(len(kmsgs)))

        except Exception as exc:
            return Result.fromException(exc)

    def send(self, topic, kmsg, timeout=60):
        """ Send the message into the given topic

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsg: Message to serialize
        :param int timeout: Timeout in seconds
        :return: Execution result
        :rtype: kser.result.Result
        """
        result = Result(uuid=kmsg.uuid)
        try:
            future = self.client.send(
                topic, self._onmessage(kmsg).dumps().encode("UTF-8")
            )
            result.stdout = "Message {}[{}]: {}".format(
                kmsg.entrypoint, kmsg.uuid, future.get(timeout=timeout)
            )

        except Exception as exc:
            result = Result.fromException(exc, kmsg.uuid)

        finally:
            if result.retcode < 300:
                return self._onsuccess(kmsg=kmsg, result=result)
            else:
                return self._onerror(kmsg=kmsg, result=result)
