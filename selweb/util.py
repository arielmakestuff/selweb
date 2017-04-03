# Module:
# Submodules:
# Created:
# Copyright (C) <date> <fullname>
#
# This module is part of the <project name> project and is released under
# the MIT License: http://opensource.org/licenses/MIT
"""
"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
from collections.abc import Sequence
from contextlib import contextmanager

# Third-party imports

# Local imports


# ============================================================================
# Helpers
# ============================================================================


# The below is a helper in constructing xpath queries.
# For example:
#
#     clsname = xpath_clsmatch('hello')
#     xpath = '//div[{clsname}]'.format(clsname=clsname)
#
# The above will have xpath contain:
#
#     //div[contains(concat(' ', normalize-space(@class), ' '), ' hello ')]
def xpath_clsmatch(clsname, *other):
    if isinstance(clsname, str):
        clsnames = [clsname] + list(other)
    elif isinstance(clsname, Sequence):
        if other:
            raise ValueError()
        clsnames = clsname
    else:
        clsnames = [str(clsname)] + list(other)

    item = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')"
    allcfunc = [item.format(n) for n in clsnames]
    return ' and '.join(allcfunc)


@contextmanager
def noop_context():
    """A do nothing context"""
    yield


# ============================================================================
#
# ============================================================================
