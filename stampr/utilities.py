from __future__ import absolute_import, unicode_literals, print_function, division

import sys

if sys.version_info[0] >= 3:
    string = (str, bytes)
else:
    string = basestring


def bad_attribute(attribute, values):
    '''Error message when trying to set a attribute incorrectly'''

    return "%s must be one of %s" % (attribute, ", ".join(repr(v) for v in values))

