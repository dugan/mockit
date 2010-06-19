# -*- mode: python -*-
#
# Copyright (c) 2010 David Christian.  All Rights Reserved.
#
# This file is licensed under the MIT License, which is available from
# http://www.opensource.org/licenses/mit-license.php

class Call(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = tuple(sorted(kwargs.items()))

    def __eq__(self, other):
        return other.__class__ == Call and self.args == other.args and self.kwargs == other.kwargs

    def __str__(self):
        return self._format_call_arguments()

    def __repr__(self):
        return 'Call%s' % (self._format_call_arguments(),)

    def _format_call_arguments(self):
        out = []
        if self.args:
            fmt_args = ', '.join(repr(x) for x in self.args)
            out.append(fmt_args)
        if self.kwargs:
            fmt_kwargs = ', '.join('%s=%r' % (x, y) for (x, y) in self.kwargs)
            out.append(fmt_kwargs)
        return '(' + (', '.join(out)) + ')'
