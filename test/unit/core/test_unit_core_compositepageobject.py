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

# Third-party imports
import pytest

# Local imports
from selweb.core import CompositePageObject


# ============================================================================
#
# ============================================================================


@pytest.mark.parametrize('name', [
    '__getitem__', '__delitem__', '__iter__', '__len__', 'add', 'clear',
    'children'
])
def test_notimplemented_method(name, compositepageobject_class):
    """All methods raise NotImplementedError"""
    one_arg = set(['__getitem__', '__delitem__', 'add'])

    args = (42, ) if name in one_arg else ()
    t = compositepageobject_class()
    func = getattr(t, name)
    with pytest.raises(NotImplementedError):
        func(*args)


# ============================================================================
#
# ============================================================================
