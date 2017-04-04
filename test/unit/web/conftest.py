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
# Fixtures
# ============================================================================


@pytest.fixture
def webgroup():
    """docstring for browser_driver"""

    class TestCompositePageObject(CompositePageObject):
        pass

    return TestCompositePageObject


# ============================================================================
#
# ============================================================================
