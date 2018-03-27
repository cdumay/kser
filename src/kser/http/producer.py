#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from kser.controller import BaseController
from cdumay_result import Result
from cdumay_rest_client.client import RESTClient


class Producer(BaseController):
    def __init__(self, config):
        """ Create new Producer instance using provided configuration dict.

        :param dict config: configuration
        """
        self.client = RESTClient(
            server=config["bootstrap_servers"],
            username=config["sasl_plain_username"],
            password=config["sasl_plain_password"],
            timeout=config.get("timeout", 10)
        )

    def bulk_send(self, topic, kmsgs):
        """ Send a batch of messages

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsgs: Messages to serialize
        :return: Execution result
        :rtype: kser.result.Result
        """

        try:
            self.client.do_request(
                method="POST", path="/topic/{}".format(topic), data=[
                    dict(Value=k.MARSHMALLOW_SCHEMA.dump(k)) for k in kmsgs
                ]
            )
            return Result(stdout="{} message(s) sent".format(len(kmsgs)))

        except Exception as exc:
            return Result.from_exception(exc)

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
                data=kmsg.MARSHMALLOW_SCHEMA.dump(kmsg)
            )
            result = Result(
                uuid=kmsg.uuid, stdout="Message sent: {} ({})".format(
                    kmsg.uuid, kmsg.entrypoint
                )
            )

        except Exception as exc:
            result = Result.from_exception(exc, kmsg.uuid)

        finally:
            # noinspection PyUnboundLocalVariable
            if result.retcode < 300:
                return self._onsuccess(kmsg=kmsg, result=result)
            else:
                return self._onerror(kmsg=kmsg, result=result)
