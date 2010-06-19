#!/usr/bin/env python

try:
    import coverage
except ImportError:
    coverage = None
if coverage:
    coverage.erase()
    coverage.start()

import mockit
import os
import unittest

class MockitTestCase(unittest.TestCase):

    def tearDown(self):
        mockit.unmock_all()
        return unittest.TestCase.tearDown(self)

    def test_attributes(self):
        m = mockit.MockObject()
        m.bar = 3
        assert(m._mock.raw.bar)
        assert(m.bar != 3)
        assert(m.bar is m.bar)
        m.bar.bam = 4
        # raw attributes
        assert(m.bar != m.bar.bam)
        assert(m.bar.bam == m.bar.bam)

    def test_raw(self):
        m = mockit.MockObject()
        m._mock.raw.bar = 3
        assert(m.bar == 3)

    def test_enable(self):
        m = mockit.MockObject()
        m._mock.enable_attrs('foo')
        try:
            m.foo
            assert(0)
        except AttributeError:
            pass
        assert(not hasattr(m, 'foo'))
        m.foo = 4
        assert(m.foo == 4)

    def test_calls(self):
        m = mockit.MockObject()
        assert(isinstance(m.foo('abc'), mockit.MockObject))
        m.blah._mock.default_return_value = 43
        assert(m.blah() == 43)
        m._mock.add_return_value(54, 3, 4, a=23)
        m._mock.add_return_value(42, 3, 4, a=23)
        m._mock.default_return_value = 12
        assert(m(3,4, a=23) == 54)
        assert(m(3,4, a=23) == 42)
        assert(m(3,4, a=23) == 12)
        assert(m(32) == 12)

    def test_dict(self):
        m = mockit.MockObject()
        assert(len(m) == 0)
        m['foo'] = 12
        m['bar'] = 13
        assert(m['foo'] != 12)
        assert(m['foo'] is m['foo'])
        assert(len(m) == 2)

    def test_raise_error(self):
        m = mockit.MockObject()
        error = RuntimeError('foo')
        m._mock.raise_error_on_access(error)
        try:
            m.foo
            assert(0)
        except RuntimeError, e:
            assert(error == e)
        m._mock.raise_error_on_access(error)
        try:
            m()
            assert(0)
        except RuntimeError, e:
            assert(error == e)
        m._mock.raise_error_on_access(error)
        try:
            m[0] = 3
            assert(0)
        except RuntimeError, e:
            assert(error == e)
        m._mock.raise_error_on_access(error)
        try:
            m[0]
            assert(0)
        except RuntimeError, e:
            assert(error == e)

    def test_bad_attr(self):
        m = mockit.MockObject()
        try:
            m.raise_error_on_access('foo')
            assert(0)
        except RuntimeError, e:
            assert(str(e) == 'accessing method %r also defined in mock object - prepend'
                             ' _mock to access, or enable attribute' % ('raise_error_on_access', ))

    def test_record(self):
        m = mockit.MockObject()
        m.foo._mock.record.assert_no_calls()
        try:
            m.foo._mock.record.assert_called('a', b='c', d='e')
            assert(0)
        except AssertionError, e:
            self.assertEquals(str(e), "expected call arguments to be ('a', b='c', d='e'), got no calls")

        m.foo('a', b='c', d='e')
        m.foo._mock.record.assert_called('a', b='c', d='e')
        try:
            m.foo._mock.record.assert_called('a', b='1', d='2')
            assert(0)
        except AssertionError, e:
            self.assertEquals(str(e), "expected call arguments to be ('a', b='1', d='2'), got ('a', b='c', d='e')")
        try:
            m.foo._mock.record.assert_no_calls()
            assert(0)
        except AssertionError, e:
            assert(str(e) == 'Invalid assertion: 1 call(s) made')
        call = m.foo._mock.record.pop_call()
        self.assertEquals(call.args, ('a',))
        self.assertEquals(call.kwargs, (('b','c'), ('d', 'e')))

    def test_call_repr(self):
        call = mockit.Call('a', 'b', foo='bar')
        assert(repr(call) == "Call('a', 'b', foo='bar')")
        assert(str(call) == "('a', 'b', foo='bar')")

    def test_list(self):
        m = mockit.MockObject()
        m._mock.set_list_items([1,2,3,4])
        assert(m[0] == 1)
        assert(m[3] == 4)
        assert(len(m) == 4)


    def test_mock_instance(self):
        class Foo(object):
            def __init__(self):
                # NOTE: this initialization is not called by default with the mock
                # object.
                self.one = 'a'
                self.two = 'b'

            def method(self, param):
                # this method is enabled by calling _mock.enableMethod
                param.bar('print some data')
                self.print_me('some other data', self.one)
                return self.two

            def print_me(self, otherParam):
                # this method is not enabled and so is stubbed out in the MockInstance.
                print otherParam

        m = mockit.MockInstance(Foo)
        m._mock.raw.two = 123
        m._mock.enable_method('method')
        param = mockit.MockObject()
        rv = m.method(param)
        self.assertEquals(rv, 123) #m.two is returned
        # note that param.bar is created on the fly as it is accessed, and 
        # stores how it was called.
        param.bar._mock.record.assert_called('print some data')
        # m.one and m.print_me were created on the fly as well
        # m.print_me remembers how it was called.
        m.print_me._mock.record.assert_called('some other data', m.one)
        # attribute values are generated on the fly but are retained between
        # accesses.
        assert(m.foo is m.foo)

    def test_mock(self):
        path = '/tmp/thisfiledefinitely/doesntexist'
        assert(not os.path.exists(path))
        mockit.mock(os.path, 'exists')
        os.path.exists._mock.default_return_value = True
        assert(os.path.exists(path))

        old_stat = os.stat
        mockit.mock(os, 'stat')
        os.stat = old_stat
        mockit.unmock_all()
        assert(not os.path.exists(path))

    def test_mock_method(self):
        class Foo(object):
            def method(self, a, b):
                return True
        foo_instance = Foo()
        mockit.mock_method(foo_instance.method)
        # normally would give an error.
        results = foo_instance.method()


if __name__ == '__main__':
    unittest.main()
    if coverage:
        coverage.stop()
