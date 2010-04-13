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

import optparse
import os.path
import sys

import blinq.reqs
import blinq.utils


class CmdRequest (blinq.reqs.Request):
    def __init__ (self, **kw):
        self.argv = kw.pop ('argv', sys.argv[1:])
        super (CmdRequest, self).__init__ (**kw)
        self._common_parser = OptionParser (formatter=OptionParser.CommonFormatter())
        self._common_parser.disable_interspersed_args ()
        self._common_parser.remove_option ('-h')
        self._common_parser.add_option ('-h', '--help',
                                        dest='_is_help_request',
                                        action='store_true',
                                        default=False,
                                        help='print this help message and exit')
        self._tool_parser = OptionParser (formatter=OptionParser.ToolFormatter())
        self._tool_parser.remove_option ('-h')
        self._tool = None
        self._common_options = {}
        self._common_args = []
        self._tool_options = {}
        self._tool_args = []
        self._responders = []

    def set_usage (self, usage):
        self._common_parser.set_usage (usage)

    def add_common_option (self, *args, **kw):
        self._common_parser.add_option (*args, **kw)

    def add_tool_option (self, *args, **kw):
        self._tool_parser.add_option (*args, **kw)

    def parse_common_options (self):
        (self._common_options, args) = self._common_parser.parse_args (self.argv)
        if len(args) > 0:
            self._tool = args[0]
            self._common_args = args[1:]

    def parse_tool_options (self):
        (self._tool_options, self._tool_args) = self._tool_parser.parse_args (self._common_args)

    def is_help_request (self):
        return self._common_options._is_help_request

    def print_help (self):
        self._common_parser.print_help (self)
        if self._tool is not None:
            self._tool_parser.print_help (self)

    def get_tool_name (self):
        return self._tool

    def get_common_option (self, option, default=None):
        try:
            return getattr (self._common_options, option)
        except:
            return default

    def get_tool_option (self, option, default=None):
        try:
            return getattr (self._tool_options, option)
        except:
            return default

    def get_tool_args (self):
        return self._tool_args

    def add_tool_responder (self, responder):
        self._responders.append (responder)

    def get_tool_responders (self):
        return blinq.utils.attrsorted (self._responders, 'command')


class CmdResponse (blinq.reqs.Response):
    def __init__ (self, request, **kw):
        super (CmdResponse, self).__init__ (request, **kw)
        self._error_text = None

    def get_error (self):
        return self._error_text

    def set_error (self, code, error):
        self.return_code = code
        self._error_text = error

    def print_error (self, text):
        print >>sys.stderr, text


class CmdErrorResponse (CmdResponse):
    def __init__ (self, request, error, **kw):
        super (CmdErrorResponse, self).__init__ (request, **kw)
        self._error_text = error
        self.return_code = 1


class CmdResponder (blinq.reqs.Responder):
    @classmethod
    def respond (self, request):
        tool = request.get_tool_name ()

        responder = None
        if tool is not None:
            for res in request.get_tool_responders ():
                if res.command == tool:
                    responder = res
                    break

        if responder is None and tool is not None:
            return CmdErrorResponse (request, '%s is not a valid command.' % tool)

        if responder is not None:
            try:
                responder.set_usage (request)
                responder.add_tool_options (request)
            except NotImplementedError:
                pass

        if request.is_help_request():
            request.print_help()
            return CmdResponse (request)

        if responder is None:
            request.print_help()
            return CmdErrorResponse (request, 'You must specify a command.')

        request.parse_tool_options ()
        response = responder.respond (request)
        return response


class OptionParser (optparse.OptionParser):
    class CommonFormatter (optparse.IndentedHelpFormatter):
        def format_heading (self, heading):
            return 'Common Options:\n'

    class ToolFormatter (optparse.IndentedHelpFormatter):
        def format_usage (self, usage):
            return ''
        def format_heading (self, heading):
            return 'Command Options:\n'

    def print_help (self, request, formatter=None):
        tool = request.get_tool_name()
        if tool is None:
            self.set_usage ('%prog [common options] <command> [command arguments]')
            optparse.OptionParser.print_help (self, formatter)
            tools = request.get_tool_responders ()
            if len(tools) > 0:
                print '\nCommands:'
                maxlen = max([len(tool.command) for tool in tools]) + 2
                for tool in tools:
                    line = '  ' + tool.command
                    line += ' ' * (maxlen - len(tool.command))
                    line += tool.synopsis
                    print line
        else:
            optparse.OptionParser.print_help (self, formatter)
