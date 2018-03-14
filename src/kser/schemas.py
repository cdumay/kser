#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from cdumay_error import ValidationError
import marshmallow.exceptions
from marshmallow import Schema, fields
from cdumay_result import ResultSchema, Result


class BaseSchema(Schema):
    uuid = fields.String(required=True)
    entrypoint = fields.String(required=True)
    params = fields.Dict(default=dict)


class Base(object):
    MARSHMALLOW_SCHEMA = BaseSchema()

    def __init__(self, uuid, entrypoint, params=None):
        self.uuid = uuid
        self.entrypoint = entrypoint
        self.params = params if params else dict()

    def dump(self):
        """description of dump"""
        return self.MARSHMALLOW_SCHEMA.dump(self)

    def dumps(self):
        """description of dumps"""
        return self.MARSHMALLOW_SCHEMA.dumps(self)

    def __str__(self):
        return str(self.dump())


class RouteSchema(BaseSchema):
    onerror = fields.String()


class Route(Base):
    MARSHMALLOW_SCHEMA = RouteSchema()

    def __init__(self, uuid, entrypoint, params=None, onerror=None):
        Base.__init__(self, uuid, entrypoint, params)
        self.onerror = onerror or entrypoint

    def __repr__(self):
        """"""
        return "Route<uuid='{}', entrypoint='{}', onerror={}>".format(
            self.uuid, self.entrypoint, self.onerror
        )


class MessageSchema(BaseSchema):
    result = fields.Nested(ResultSchema, missing=None)
    route = fields.Nested(RouteSchema, missing=None)


class Message(Base):
    MARSHMALLOW_SCHEMA = MessageSchema()

    @classmethod
    def loads(cls, json_data):
        """description of load"""
        try:
            return cls(**cls.MARSHMALLOW_SCHEMA.loads(json_data))
        except marshmallow.exceptions.ValidationError as exc:
            raise ValidationError("Failed to load message", extra=exc.args[0])

    def __init__(self, uuid, entrypoint, params=None, result=None, route=None):
        Base.__init__(self, uuid, entrypoint, params)
        if result:
            if isinstance(result, Result):
                self.result = result
            else:
                self.result = Result(**result)
        else:
            self.result = Result(uuid=uuid)

        if route:
            if isinstance(route, Route):
                self.route = route
            else:
                self.route = Route(**route)
        else:
            self.route = None

    def __repr__(self):
        """"""
        return "Message<uuid='{}', entrypoint='{}', result={}>".format(
            self.uuid, self.entrypoint, self.result
        )
