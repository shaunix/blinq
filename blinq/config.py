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

import ConfigParser

class Config (object):
    def __init__ (self):
        self._options = {}
        self._config = ConfigParser.RawConfigParser()
        self._filename = None

    def init (self, filename):
        self._filename = filename
        try:
            fp = open(self._filename)
            self._config.readfp (fp)
            fp.close()
        except:
            pass

    def option (self, func):
        """Decorator to register an option with this Config object."""
        self._options[func.__name__] = func

    def get_options (self):
        """
        Get a list of registered options as pairs containing the option
        name and the option documentation.
        """
        options = []
        for key in sorted (self._options.keys()):
            func = self._options[key]
            options.append ((key, func.__doc__))
        return options

    def save (self):
        import os
        filedir = os.path.dirname (self._filename)
        if not os.path.exists (filedir):
            os.makedirs (filedir)
        fp = open(self._filename, 'w')
        self._config.write(fp)
        fp.close()

    def get_raw_option (self, name):
        try:
            return self._config.get ('config', name)
        except:
            return None

    def __getattr__ (self, name):
        try:
            func = self._options[name]
            return func (self.get_raw_option (name))
        except:
            raise AttributeError ('This \'Config\' object has no attribute \'%s\'' % name)

    def __setattr__ (self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            if not self._config.has_section('config'):
                self._config.add_section ('config')
            self._config.set ('config', name, value)
        
config = Config ()

@config.option
def mail_server (val):
    """The SMTP server to send mail through"""
    return (val is not None) and val or 'localhost'

@config.option
def mail_port (val):
    """The port to use to connec to the SMTP server"""
    if val is not None:
        return val
    elif config.mail_encryption == 'ssl':
        return '465'
    else:
        return '25'

@config.option
def mail_encryption (val):
    """Type of encryption to use for SMTP; one of 'none', 'ssl', or 'tsl'"""
    return (val in ('ssl', 'tsl')) and val or None

@config.option
def mail_username (val):
    """The username to connect to the SMTP server, or 'none' for no authenticaion"""
    return (val not in (None, 'none', 'None')) and val or None

@config.option
def mail_password (val):
    """The password to connect to the SMTP server"""
    return val

@config.option
def mail_from (val):
    """The email address to send mail from"""
    return (val is not None) and val or 'nobody@localhost'


@config.option
def web_root_url (url):
    """The root URL for this site"""
    if url is None:
        return 'http://127.0.0.1/'
    elif url.endswith ('/'):
        return url
    else:
        return url + '/'

import sys
sys.modules[__name__] = config
