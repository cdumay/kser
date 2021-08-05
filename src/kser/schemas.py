#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import marshmallow.exceptions
from cdumay_error.types import ValidationError
from cdumay_result import ResultSchema, Result
from marshmallow import Schema, fields, EXCLUDE


class BaseSchema(Schema):
    """Entrypoint schema"""

    class Meta:
        """Meta data"""
        unknown = EXCLUDE

    uuid = fields.String(required=True)
    entrypoint = fields.String(required=True)
    params = fields.Dict(default=dict)


class Base(object):
    """Mother class for entrypoint"""
    MARSHMALLOW_SCHEMA = BaseSchema()

    def __init__(self, uuid, entrypoint, params=None):
        self.uuid = uuid
        self.entrypoint = entrypoint
        self.params = params if params else dict()

    def dump(self):
        """Dump entrypoint into a dict"""
        return self.MARSHMALLOW_SCHEMA.dump(self)

    def dumps(self):
        """Dump entrypoint into a string"""
        return self.MARSHMALLOW_SCHEMA.dumps(self)

    def __str__(self):
        return str(self.dump())


class MessageSchema(BaseSchema):
    """Message schema"""
    result = fields.Nested(ResultSchema, missing=None)
    metadata = fields.Dict()


class Message(Base):
    """Message"""
    MARSHMALLOW_SCHEMA = MessageSchema()

    @classmethod
    def loads(cls, json_data):
        """Load message from a string"""
        try:
            return cls(**cls.MARSHMALLOW_SCHEMA.loads(json_data))
        except marshmallow.exceptions.ValidationError as exc:
            raise ValidationError("Failed to load message", extra=exc.args[0])

    def __init__(self, uuid, entrypoint, params=None, result=None,
                 metadata=None):
        Base.__init__(self, uuid, entrypoint, params)
        if result:
            if isinstance(result, Result):
                self.result = result
            else:
                self.result = Result(**result)
        else:
            self.result = Result(uuid=uuid)
        self.metadata = metadata or dict()

    def __repr__(self):
        """"""
        return "Message<uuid='{}', entrypoint='{}', result={}>".format(
            self.uuid, self.entrypoint, self.result
        )
