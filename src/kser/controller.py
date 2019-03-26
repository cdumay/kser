#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import os

from cdumay_error import ValidationError
from kser.entry import Entrypoint
from cdumay_result import Result, ResultSchema
from kser.schemas import Message

logger = logging.getLogger(__name__)

os.environ.setdefault("RUNNING_FILE", "/var/run/kser-run.lock")


class BaseController(object):
    @classmethod
    def _onsuccess(cls, kmsg, result):
        """ To execute on execution success

        :param kser.schemas.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.info(
            "{}.Success: {}[{}]: {}".format(
                cls.__name__, kmsg.entrypoint, kmsg.uuid, result
            ),
            extra=dict(
                kmsg=kmsg.dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
        return cls.onsuccess(kmsg, result)

    # noinspection PyUnusedLocal
    @classmethod
    def onsuccess(cls, kmsg, result):
        """ To execute on execution success

        :param kser.schemas.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    @classmethod
    def _onerror(cls, kmsg, result):
        """ To execute on execution failure

        :param kser.schemas.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.error(
            "{}.Failed: {}[{}]: {}".format(
                cls.__name__, kmsg.entrypoint, kmsg.uuid, result
            ),
            extra=dict(
                kmsg=kmsg.dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
        return cls.onerror(kmsg, result)

    # noinspection PyUnusedLocal
    @classmethod
    def onerror(cls, kmsg, result):
        """ To implement

        :param kser.schemas.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    @classmethod
    def _onmessage(cls, kmsg):
        """ Call on received message

        :param kser.schemas.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.schemas.Message
        """
        logger.debug(
            "{}.ReceivedMessage {}[{}]".format(
                cls.__name__, kmsg.entrypoint, kmsg.uuid
            ),
            extra=dict(kmsg=kmsg.dump())
        )
        return cls.onmessage(kmsg)

    @classmethod
    def onmessage(cls, kmsg):
        """ To implement

        :param kser.schemas.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.schemas.Message
        """
        return kmsg


class Controller(BaseController):
    ENTRYPOINTS = dict()
    TRANSPORT = Message

    @classmethod
    def start_processing(cls, kmsg):
        with open(os.environ['RUNNING_FILE'], 'w') as file:
            file.write("{}[{}]".format(kmsg.entrypoint, kmsg.uuid))

    @classmethod
    def stop_processing(cls):
        with open(os.environ['RUNNING_FILE'], 'w') as file:
            file.write("")

    @classmethod
    def register(cls, name, entrypoint):
        """ Register a new entrypoint

        :param str name: Key used by messages
        :param kser.entry.Entrypoint entrypoint: class to load
        :raises ValidationError: Invalid entry
        """
        if not issubclass(entrypoint, Entrypoint):
            raise ValidationError(
                "Invalid type for entry '{}', MUST implement "
                "kser.entry.Entrypoint".format(name),
                extra=dict(entrypoint=name)
            )
        cls.ENTRYPOINTS[name] = entrypoint
        logger.debug("{}.Registered: {}".format(cls.__name__, name))

    @classmethod
    def run(cls, raw_data):
        """description of run"""
        logger.debug("{}.ReceivedFromKafka: {}".format(
            cls.__name__, raw_data
        ))
        try:
            kmsg = cls._onmessage(cls.TRANSPORT.loads(raw_data))
        except Exception as exc:
            logger.error(
                "{}.ImportError: Failed to load data from kafka: {}".format(
                    cls.__name__, exc
                ),
                extra=dict(kafka_raw_data=raw_data)
            )
            return Result.from_exception(exc)

        try:
            cls.start_processing(kmsg)
            if kmsg.entrypoint not in cls.ENTRYPOINTS:
                raise ValidationError(
                    "Entrypoint '{}' not registred".format(kmsg.entrypoint),
                    extra=dict(
                        uuid=kmsg.uuid, entrypoint=kmsg.entrypoint,
                        allowed=list(cls.ENTRYPOINTS.keys())
                    )
                )

            result = cls.ENTRYPOINTS[kmsg.entrypoint].from_Message(
                kmsg
            ).execute()

        except Exception as exc:
            result = Result.from_exception(exc, kmsg.uuid)

        finally:
            cls.stop_processing()
            # noinspection PyUnboundLocalVariable
            if result and result.retcode < 300:
                return cls._onsuccess(kmsg=kmsg, result=result)
            else:
                return cls._onerror(kmsg=kmsg, result=result)
