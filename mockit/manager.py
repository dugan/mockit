# -*- mode: python -*-
#
# Copyright (c) 2006-2008,2010 rPath, Inc.  All Rights Reserved.
# Copyright (c) 2010 David Christian.  All Rights Reserved.
#
# This file is licensed under the MIT License, which is available from
# http://www.opensource.org/licenses/mit-license.php

from mockit.utils import Call

_NO_VALUE = object()

class MockObjectManager(object):

    NO_VALUE = _NO_VALUE

    def __init__(self, mock_object, default_return_value=NO_VALUE):
        self.stats = MockObjectStats()

        self._return_values = []

        self.mock_object = mock_object
        self.raw = RawObject(mock_object)
        self.raw_dict = {}
        self.default_return_value = default_return_value
        self._enabled = set()
        self._error_to_raise = None

    def new_mock(self):
        from mockit.mock_object import MockObject
        return MockObject()

    def add_return_value(self, return_value, *args, **kwargs):
        call = Call(*args, **kwargs)
        self._return_values.append((call, return_value))

    def set_list_items(self, list_items):
        for idx, item in enumerate(list_items):
            self.raw_dict[idx] = item

    def enable_attrs(self, *names):
        self._enabled.update(names)

    def is_enabled(self, attr):
        return attr in self._enabled

    def raise_error_on_access(self, error):
        self._error_to_raise = error

    def _check_error(self):
        if self._error_to_raise is not None:
            err = self._error_to_raise
            self._error_to_raise = None
            raise err

    def set_item(self, key, value):
        self.stats.add_action('setitem', key, value)
        self._check_error()
        return self.raw_dict.setdefault(key, self.new_mock())

    def get_item(self, key):
        self.stats.add_action('getitem', key)
        self._check_error()
        return self.raw_dict.setdefault(key, self.new_mock())

    def set_attr(self, key, value):
        self.stats.add_action('setattr', key, value)
        self._check_error()
        return self.raw.__dict__.setdefault(key, self.new_mock())
    
    def get_attr(self, key):
        if key in self.__class__.__dict__:
            raise RuntimeError('accessing method %r also defined in mock'
                ' object - prepend _mock to access, or enable attribute' % key)
        self.stats.add_action('getattr', key)
        self._check_error()
        return self.raw.__dict__.setdefault(key, self.new_mock())

    def call(self, *args, **kwargs):
        call = Call(*args, **kwargs)
        self.stats.add_action('call', *args, **kwargs)
        self._check_error()
        return_value = [ x[1] for x in self._return_values if x[0] == call ]
        if return_value:
            self._return_values.remove((call, return_value[0]))
            return return_value[0]
        if self.default_return_value != self.NO_VALUE:
            return self.default_return_value

        return_value = self.new_mock()
        self.default_return_value = return_value
        return return_value

    def length(self):
        return len(self.raw_dict)

class RawObject(object):
    def __init__(self, mock_object):
        self.__dict__ = mock_object.__dict__


class MockObjectStats(object):
    def __init__(self):
        self.actions = {'setitem' : [],
                        'getitem' : [],
                        'setattr' : [],
                        'getattr' : [],
                        'call'    : [] }

    def assert_called(self, *args, **kwargs):
        call = Call(*args, **kwargs)
        if call in self.actions['call']:
            return

        if not self.actions['call']:
            got = 'no calls'
        else:
            got = ', '.join(str(x) for x in self.actions['call'])
        raise AssertionError("expected call arguments to be %s, got %s" % (call, got))

    def assert_no_calls(self):
        assert not self.actions['call'], "Invalid assertion: %s call(s) made" % (len(self.actions['call']),)

    def pop_action(self, action_type):
        action =  self.actions[action_type][0]
        self.actions[action_type] = self.actions[action_type][1:]
        return action

    def pop_call(self):
        return self.pop_action('call')

    def add_action(self, action_type, *args, **kwargs):
        call = Call(*args, **kwargs)
        self.actions[action_type].append(call)
