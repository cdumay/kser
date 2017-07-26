#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from cdumay_rest_client.exceptions import HTTPException
from kser import random_uuid
from marshmallow import Schema, fields


class ResultSchema(Schema):
    uuid = fields.String()
    retcode = fields.Integer(default=0)
    stdout = fields.String(default="")
    stderr = fields.String(default="")
    retval = fields.Dict()


class Result(object):
    def __init__(self, retcode=0, stdout="", stderr="", retval=None, uuid=None):
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr
        self.retval = retval or dict()
        self.uuid = uuid if uuid else random_uuid()

    def print(self, data):
        """Store text in result's stdout

        :param Any data: Any printable data
        """
        self.stdout += "{}\n".format(data)

    def print_err(self, data):
        """Store text in result's stderr

        :param Any data: Any printable data
        """
        self.stderr += "{}\n".format(data)

    @staticmethod
    def fromException(exc, uuid=None):
        """ Serialize an exception into a result

        :param Exception exc: Exception raised
        :param str uuid: Current Kafka :class:`kser.transport.Message` uuid
        :rtype: :class:`kser.result.Result`
        """
        if isinstance(exc, HTTPException):
            return Result(
                uuid=exc.extra.get("uuid", uuid or random_uuid()),
                retcode=exc.code, stderr=exc.message, retval=exc.extra
            )
        else:
            return Result(
                uuid=uuid or random_uuid(), retcode=500, stderr=str(exc)
            )

    def __str__(self):
        return str(ResultSchema().dump(self).data)

    def __repr__(self):
        """"""
        return "Result<retcode='{}'>".format(self.retcode)
