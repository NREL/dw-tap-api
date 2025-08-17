# -*- coding: utf-8 -*-
""" Code for raising custom exceptions.

Define a class for custom exception handling. This class helps avoid "leaking"
code when something breaks -- this is a recommended way in development
of pubic-facing APIs.

Example:
    try:
        ...
    except ValueError:
        raise InvalidUsage("Problem!...")
"""


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
