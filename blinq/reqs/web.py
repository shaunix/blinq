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

import cgi
import Cookie
import os
import sys

import blinq.reqs
import blinq.utils


class WebException (Exception):
    def __init__ (self, title, desc):
        self.title = title
        self.desc = desc


class WebRequest (blinq.reqs.Request):
    def __init__ (self, **kw):
        self.http = kw.pop ('http', True)
        self.path_info = kw.pop ('path_info', None)
        self.query_string = kw.pop ('query_string', None)
        self.stdin = kw.pop ('stdin', sys.stdin)
        cookies = kw.pop('http_cookie', None)

        super (WebRequest, self).__init__(**kw)

        if self.path_info is None:
            self.path_info = self.getenv ('PATH_INFO')
        if self.query_string is None:
            self.query_string = self.getenv ('QUERY_STRING')
        if cookies is None:
            cookies = self.getenv('HTTP_COOKIE') or ''

        self.path = []
        if self.path_info is not None:
            path = blinq.utils.utf8dec (self.path_info).split ('/')
            for part in path:
                if part != '':
                    self.path.append (part)

        self.post_data = {}
        if self.getenv('REQUEST_METHOD') == 'POST':
            environ = self.environ.copy()
            environ.pop('QUERY_STRING')
            data = cgi.parse(fp=self.stdin, environ=environ)
            for key in data.keys():
                self.post_data[key] = blinq.utils.utf8dec(data[key][0])

        self.query = {}
        if self.query_string is not None:
            query = cgi.parse_qs (self.query_string, True)
            for key in query.keys():
                self.query[key] = blinq.utils.utf8dec (query[key][0])

        self.cookies = Cookie.SimpleCookie ()
        self.cookies.load (cookies)


class WebResponse (blinq.reqs.Response):
    def __init__ (self, request, **kw):
        super (WebResponse, self).__init__ (request, **kw)
        self.http_content_disposition = None
        self._http_status = None
        self._location = None
        self._cookies = []

    def _get_http_status (self):
        if self._http_status is not None:
            return self._http_status
        elif self.payload is not None and hasattr(self.payload, 'http_status'):
            return self.payload.http_status
        else:
            return None
    def _set_http_status (self, http_status):
        self._http_status = http_status
    http_status = property (_get_http_status, _set_http_status)

    def _get_return_code (self):
        if self.http_status in (None, 200, 301):
            return 0
        else:
            return self.http_status
    def _set_return_code (self, code):
        self.http_status = code
    return_code = property (_get_return_code, _set_return_code)

    def redirect (self, location):
        self.http_status = 301
        self._location = location
        self.payload = None

    def set_cookie (self, cookie, value):
        self._cookies.append ((cookie, value))

    def get_response (self):
        status = '200 OK'
        headers = []
        if self.http_status == 404:
            status = '404 Not found'
        elif self.http_status == 500:
            status = '500 Internal server error'
        if self.http_status == 301:
            status = '301 Moved permanently'
            headers.append(('Location', self._location or blinq.config.web_root_url))
        else:
            headers.append(('Content-type', self.content_type))
            if self.http_content_disposition is not None:
                headers.append(('Content-disposition', self.http_content_disposition))
        for cookie, value in self._cookies:
            ck = Cookie.SimpleCookie()
            ck[cookie] = value
            nohttp = blinq.config.web_root_url
            nohttp = nohttp[nohttp.find('://') + 3:]
            ck[cookie]['domain'] = nohttp[:nohttp.find('/')]
            ck[cookie]['path'] = nohttp[nohttp.find('/'):]
            headers.append(('Set-Cookie', ck.output(header='')))
        return (status, headers)

    def output (self, fp=None):
        self._fp = fp
        if self._fp is None:
            self._fp = sys.stdout
        if self.request.http:
            (status, headers) = self.get_response()
            if self.http_status != 200:
                self.write('Status: %s \n' % status)
            for header in headers:
                self.write('%s: %s\n' % header)
            self.write('\n')
        self.output_payload (fp=fp)

    def output_payload (self, fp=None):
        self._fp = fp
        if self._fp is None:
            self._fp = sys.stdout
        if self.payload is not None:
            self.payload.output (self)

    def write (self, txt):
        if isinstance (txt, blinq.reqs.Payload):
            txt.output (self)
            return
        if isinstance(txt, unicode):
            txt = txt.encode ('utf-8')
        self._fp.write (txt)


class TextPayload (blinq.reqs.Payload):
    """Payload for plain text"""
    def __init__ (self, **kw):
        super (TextPayload, self).__init__ (**kw)
        self.content_type = 'text/plain'
        self._text_content = ''

    def set_content (self, content):
        self._text_content = content

    def add_content (self, content):
        self._text_content += content

    def output (self, res):
        res.write (self._text_content)


class JsonPayload (blinq.reqs.Payload):
    """Payload for JSON data"""
    def __init__ (self, **kw):
        super (JsonPayload, self).__init__(**kw)
        self.content_type = 'application/json'
        self._data = None

    def set_data (self, data):
        self._data = data

    def output (self, res):
        import json
        res.write (json.dumps (self._data))


class HtmlPayload (blinq.reqs.Payload):
    """Payload for HTML content"""
    def __init__ (self, **kw):
        super (HtmlPayload, self).__init__(**kw)
        self.content_type = 'text/html; charset=utf-8'

    @staticmethod
    def escape (obj):
        class escdict (dict):
            def __init__ (self, *args):
                dict.__init__ (self, *args)
            def __getitem__ (self, key):
                return HtmlPayload.escape(dict.__getitem__(self, key))
        if isinstance (obj, HtmlPayload):
            return obj
        elif isinstance (obj, unicode):
            return cgi.escape (obj, True).encode('utf-8')
        elif isinstance (obj, basestring):
            return cgi.escape (obj, True)
        elif isinstance (obj, tuple):
            return tuple (map (HtmlPayload.escape, obj))
        elif isinstance (obj, dict):
            return escdict (obj)
        else:
            return obj
