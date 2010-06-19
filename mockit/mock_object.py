# -*- mode: python -*-
#
# Copyright (c) 2006-2008,2010 rPath, Inc.  All Rights Reserved.
# Copyright (c) 2010 David Christian.  All Rights Reserved.
#
# This file is licensed under the MIT License, which is available from
# http://www.opensource.org/licenses/mit-license.php


from mockit.manager import MockObjectManager

class MockObject(object):

    _mock_manager_class = MockObjectManager

    def __init__(self, **kwargs):
        self._mock = self._mock_manager_class(self, **kwargs)

    def __getattr__(self, key):
        if self._mock.is_enabled(key):
            return object.__getattribute__(self, key)
        m = self._mock.get_attr(key)
        self.__dict__[key] = m
        return m

    def __setattr__(self, key, value):
        if key == '_mock' or self._mock.is_enabled(key):
            object.__setattr__(self, key, value)
        else:
            self._mock.set_attr(key, value)

    def __setitem__(self, key, value):
        return self._mock.set_item(key, value)

    def __getitem__(self, key):
        return self._mock.get_item(key)

    def __len__(self):
        return self._mock.length()

    def __nonzero__(self):
        return True

    def __call__(self, *args, **kwargs):
        return self._mock.call(*args, **kwargs)



