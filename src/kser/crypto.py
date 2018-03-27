#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import base64
import csodium
from marshmallow import Schema, fields
from kser.schemas import Message


class CryptoMessage(Schema):
    data = fields.String(required=True)
    nonce = fields.String(required=True)

    @classmethod
    def encode(cls, kmsg, secretbox_key):
        """ Encode message using libsodium

        :param kser.schemas.Message kmsg: Kafka message
        :param str secretbox_key: Secrebox Key
        :return: the Encoded message
        """
        nonce = csodium.randombytes(csodium.crypto_box_NONCEBYTES)
        return cls().dumps(dict(
            nonce=base64.encodebytes(nonce).strip(),
            data=base64.encodebytes(
                csodium.crypto_secretbox(
                    bytes(kmsg.MARSHMALLOW_SCHEMA.dumps(kmsg).data, 'utf-8'),
                    nonce, base64.b64decode(secretbox_key)
                )
            ).strip()
        ))

    @classmethod
    def decode(cls, jdata, secretbox_key):
        """ Decode message using libsodium

        :param str jdata: jdata to load
        :param str secretbox_key: Secrebox Key
        :return: the Encoded message
        """
        ckmsg = cls().loads(jdata)
        return Message.loads(
            csodium.crypto_secretbox_open(
                base64.b64decode(ckmsg["data"]),
                base64.b64decode(ckmsg["nonce"]),
                base64.b64decode(secretbox_key)
            ).decode('utf-8')
        )
