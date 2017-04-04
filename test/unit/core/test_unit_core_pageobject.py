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
from selweb.core import PageObject


# ============================================================================
# All methods raise NotImplementedError
# ============================================================================


@pytest.mark.parametrize('name', ['__bool__', 'reload'])
def test_notimplemented_method(name, pageobject_class):
    """All methods raise NotImplementedError"""

    t = pageobject_class()
    func = getattr(t, name)
    with pytest.raises(NotImplementedError):
        func()


@pytest.mark.parametrize('name', [
    'name', 'source', 'xpath', 'absxpath', 'browser', 'visible', 'parent'
])
def test_notimplemented_getprop(name, pageobject_class):
    """All get properties raise NotImplementedError"""
    t = pageobject_class()
    with pytest.raises(NotImplementedError):
        getattr(t, name)


@pytest.mark.parametrize('name', ['parent'])
def test_notimplemented_setprop(name, pageobject_class):
    """All set properties raise NotImplementedError"""
    t = pageobject_class()
    with pytest.raises(NotImplementedError):
        setattr(t, name, 42)


# ============================================================================
#
# ============================================================================
