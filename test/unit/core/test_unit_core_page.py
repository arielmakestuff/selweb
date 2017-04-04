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
from selweb.core import Page


# ============================================================================
# Tests
# ============================================================================


@pytest.mark.parametrize('name', ['go'])
def test_notimplemented_method(name, page_class):
    """All methods raise NotImplementedError"""
    t = page_class()
    func = getattr(t, name)
    with pytest.raises(NotImplementedError):
        func()


@pytest.mark.parametrize('name', ['url', 'parser'])
def test_notimplemented_getprop(name, page_class):
    """All get properties raise NotImplementedError"""
    t = page_class()
    with pytest.raises(NotImplementedError):
        getattr(t, name)


# ============================================================================
#
# ============================================================================
