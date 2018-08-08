#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import base64
import os
import csodium
import marshmallow

from cdumay_error import ValidationError
from marshmallow import Schema, fields
from kser.schemas import Message


class CryptoSchema(Schema):
    data = fields.String(required=True)
    nonce = fields.String(required=True)

    def encode(self, kmsg):
        """ Encode message using libsodium

        :param kser.schemas.Message kmsg: Kafka message
        :return: the Encoded message
        """
        nonce = csodium.randombytes(csodium.crypto_box_NONCEBYTES)
        return self.dumps(dict(
            nonce=base64.encodebytes(nonce).strip(),
            data=base64.encodebytes(
                csodium.crypto_secretbox(
                    bytes(kmsg.MARSHMALLOW_SCHEMA.dumps(kmsg).data, 'utf-8'),
                    nonce, base64.b64decode(self.context['secretbox_key'])
                )
            ).strip()
        ))

    def decode(self, jdata):
        """ Decode message using libsodium

        :param str jdata: jdata to load
        :return: the Encoded message
        """
        ckmsg = self.loads(jdata)
        return Message.loads(
            csodium.crypto_secretbox_open(
                base64.b64decode(ckmsg["data"]),
                base64.b64decode(ckmsg["nonce"]),
                base64.b64decode(self.context['secretbox_key'])
            ).decode('utf-8')
        )


class CryptoMessage(Message):
    MARSHMALLOW_SCHEMA = CryptoSchema(
        context=dict(secretbox_key=os.getenv("KSER_SECRETBOX_KEY", None))
    )

    @classmethod
    def loads(cls, json_data):
        """description of load"""
        try:
            return cls(**cls.MARSHMALLOW_SCHEMA.decode(json_data))
        except marshmallow.exceptions.ValidationError as exc:
            raise ValidationError("Failed to load message", extra=exc.args[0])
