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

"""Various utility functions"""

import codecs

def utf8dec (s):
    """
    Decode a string to UTF-8, or don't if it already is
    """
    if isinstance(s, str):
        return codecs.getdecoder('utf-8')(s, 'replace')[0]
    else:
        return s

def utf8enc (s):
    """
    Encode a unicode object to UTF-8, or don't if it already is
    """
    if isinstance(s, unicode):
        return codecs.getencoder('utf-8')(s)[0]
    else:
        return s

def attrsorted (lst, *attrs):
    """
    Sort a list of objects based on given object attributes

    The list is first sorted by comparing the value of the first attribute
    for each object.  When the values for two objects are equal, they are
    sorted according to the second attribute, third attribute, and so on.

    An attribute may also be a tuple or list.  In this case, the value to
    be compared for an object is obtained by successively extracting the
    attributes.  For example, an attribute of ('foo', 'bar') would use the
    value of obj.foo.bar for the object obj.

    All string comparisons are case-insensitive.
    """
    def attrget (obj, attr):
        """Get an attribute or list of attributes from an object"""
        if isinstance (attr, tuple) or isinstance (attr, list):
            if len(attr) > 1:
                return attrget (attrget (obj, attr[0]), attr[1:])
            else:
                return attrget (obj, attr[0])
        elif isinstance (obj, dict):
            return obj.get (attr)
        elif isinstance (attr, basestring):
            if attr.startswith('[') and attr.endswith(']'):
                return obj[attr[1:-1]]
            return getattr (obj, attr)
        elif isinstance (attr, int):
            return obj.__getitem__ (attr)
        elif isinstance (obj, basestring):
            return obj.lower()
        else:
            return obj

    def lcmp (val1, val2):
        """Compare two objects, case-insensitive if strings"""
        if isinstance (val1, unicode):
            v1 = val1.lower()
        elif isinstance (val1, basestring):
            v1 = val1.decode('utf-8').lower()
        else:
            v1 = val1
        if isinstance (val2, unicode):
            v2 = val2.lower()
        elif isinstance (val1, basestring):
            v2 = val2.decode('utf-8').lower()
        else:
            v2 = val2
        return cmp (v1, v2)

    def attrcmp (val1, val2, attrs):
        """Compare two objects based on some attributes"""
        attr = attrs[0]
        try:
            attrf = attr[0]
        except:
            attrf = None
        if attrf == '-':
            attr = attr[1:]
            cmpval = lcmp (attrget(val2, attr), attrget(val1, attr))
        else:
            cmpval = lcmp (attrget(val1, attr), attrget(val2, attr))
        if cmpval == 0 and len(attrs) > 1:
            return attrcmp (val1, val2, attrs[1:])
        else:
            return cmpval

    return sorted (lst, lambda val1, val2: attrcmp (val1, val2, attrs))
