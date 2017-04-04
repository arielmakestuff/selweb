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
from selweb.driver import BrowserDriver


# ============================================================================
#
# ============================================================================


class FakeDriver(BrowserDriver):

    def __enter__(self):
        pass

    def __exit__(self, exctype, exc, exctb):
        pass

    def mkdriver(self):
        super().mkdriver()

    @property
    def driver(self):
        super().driver


def test_mkdriver_raise_exception():
    """All methods of BrowserDriver ABC raise NotImplementedError"""
    driver = FakeDriver()

    with pytest.raises(NotImplementedError):
        driver.mkdriver()


def test_driver_raise_exception():
    """All methods of BrowserDriver ABC raise NotImplementedError"""
    driver = FakeDriver()

    with pytest.raises(NotImplementedError):
        driver.driver


# ============================================================================
#
# ============================================================================
