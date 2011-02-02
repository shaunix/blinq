# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010  Shaun McCance  <shaunm@gnome.org>
#
# Blinq is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Blinq is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with Blinq; if not, write to the Free Software Foundation, 59 Temple Place,
# Suite 330, Boston, MA  0211-1307  USA.
#

import os
import os.path

import blinq.ext


class Request (object):
    """Abstract base class for all requests"""
    def __init__ (self, **kw):
        self.environ = kw.pop('environ', os.environ).copy()
        super (Request, self).__init__(**kw)
        self._data = {}

    def getenv (self, key):
        return self.environ.get (key)

    def set_data (self, key, val):
        self._data[key] = val

    def get_data (self, key, default=None):
        return self._data.get (key, default)


class Response (object):
    """Abstract base class for all responses"""
    def __init__ (self, request, **kw):
        super (Response, self).__init__(**kw)
        self.request = request
        self.return_code = 0
        self.payload = None
        self._content_type = None

    def _get_content_type (self):
        if self._content_type is not None:
            return self._content_type
        elif self.payload is not None:
            return self.payload.content_type
        else:
            return None
    def _set_content_type (self, content_type):
        self._content_type = content_type
    content_type = property (_get_content_type, _set_content_type)
        
    def output (self, fp):
        self.payload.output (self)

    def write (self, txt):
        raise NotImplementedError ('%s does not provide the write method.'
                                   % self.__class__.__name__)


class Payload (object):
    """Abstract base class for all response payloads"""
    def __init__ (self, **kw):
        super (Payload, self).__init__(**kw)
        self.content_type = None

    def output (self, res):
        raise NotImplementedError ('%s does not provide the output method.'
                                   % self.__class__.__name__)


class TextPayload (Payload):
    """Simple payload for plain text"""
    def __init__ (self, **kw):
        super (TextPayload, self).__init__(**kw)
        self.content_type = 'text/plain; charset=utf-8'
        self._content = ''

    def __iadd__ (self, txt):
        self._content += str(txt)
        return self

    def output (self, res):
        res.write (self._content)


class Responder (blinq.ext.ExtensionPoint):
    @classmethod
    def respond (cls, request):
        raise NotImplementedError ('%s does not provide the respond method.'
                                   % cls.__name__)
