#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@corp.ovh.com>


"""
import logging
from kser import BaseTransportSerializer
from cdumay_result import Result
from cdumay_rest_client.client import RESTClient

logger = logging.getLogger("kser")


class Producer(BaseTransportSerializer):
    def __init__(self, config):
        """ Create new Producer instance using provided configuration dict.

        :param dict config: configuration
        """
        self.client = RESTClient(
            server=config["bootstrap.servers"],
            username=config["sasl.username"], password=config["sasl.password"],
            timeout=config.get("timeout", 10)
        )

    def send(self, topic, kmsg):
        """ Send the message into the given topic

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsg: Message to serialize
        :return: Execution result
        :rtype: kser.result.Result
        """
        try:
            self.client.do_request(
                method="POST", params=dict(format="raw"),
                path="/topic/{}".format(topic),
                data=kmsg.MARSHMALLOW_SCHEMA.dump(kmsg).data
            )
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
