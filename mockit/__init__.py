# -*- mode: python -*-
#
# Copyright (c) 2006-2008,2010 rPath, Inc.  All Rights Reserved.
# Copyright (c) 2010 David Christian.  All Rights Reserved.
#
# This file is licensed under the MIT License, which is available from
# http://www.opensource.org/licenses/mit-license.php

from mockit.mock_object import MockObject
from mockit.instance import MockInstance
from mockit.utils import Call

__all__ = [ 'MockObject', 'MockInstance', 'Call', 'mock_method', 'mock' ]

class MockObjectRegistry(object):
    def __init__(self):
        self._mocked = []
    
    def replace(self, object, attr_name, options=None):
        self._mocked.append((object, attr_name))
        new_value = MockObject()
        if options is not None:
            new_value._mock.options = options
        old_value = getattr(object, attr_name)
        new_value._mock.orig_value = old_value
        setattr(object, attr_name, new_value)
        return new_value

    def unmock_all(self):
        for obj, attr in self._mocked:
            if not hasattr(getattr(obj, attr, None), '_mock'):
                continue
            setattr(obj, attr, getattr(obj, attr)._mock.orig_value)
        self._mocked = []

registry = MockObjectRegistry()

def unmock_all():
    return registry.unmock_all()

def mock_method(method, **options):
    return registry.replace(method.im_self, method.__name__, options=options)

def mock(object, attr, **options):
    return registry.replace(object, attr, options=options)
