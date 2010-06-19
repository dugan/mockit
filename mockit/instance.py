# -*- mode: python -*-
#
# Copyright (c) 2006-2008,2010 rPath, Inc.  All Rights Reserved.
# Copyright (c) 2010 David Christian.  All Rights Reserved.
#
# This file is licensed under the MIT License, which is available from
# http://www.opensource.org/licenses/mit-license.php

import new

from mockit.manager import MockObjectManager
from mockit.mock_object import MockObject

class MockInstanceManager(MockObjectManager):
    def __init__(self, *args, **kwargs):
        self.super_class = kwargs.pop('super_class')
        MockObjectManager.__init__(self, *args, **kwargs)

    def enable_method(self, name):
        self.enable_attrs(self, name)
        func = getattr(self.super_class, name).im_func
        method = new.instancemethod(func, self.mock_object, self.mock_object.__class__)
        object.__setattr__(self.raw, name, method)

class MockInstance(MockObject):
    _mock_manager_class = MockInstanceManager

    def __init__(self, class_, **kwargs):
        kwargs['super_class'] = class_
        MockObject.__init__(self, **kwargs)
