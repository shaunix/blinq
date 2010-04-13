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

class ExtensionPoint (object):
    _disabled = []

    @classmethod
    def get_extensions (cls):
        extensions = []
        for subcls in cls.__subclasses__():
            if subcls not in cls._disabled:
                extensions.append (subcls)
            extensions = extensions + subcls.get_extensions()
        return extensions

    @classmethod
    def disable_extension (cls, ext):
        cls._disabled.append (ext)


def import_extensions (base, domain):
    plugdir = os.path.dirname (base.__file__)
    for pkg in os.listdir (plugdir):
        if os.path.isdir (os.path.join (plugdir, pkg)):
            try:
                __import__ (base.__name__ + '.' + pkg + '.' + domain)
            except ImportError:
                pass
