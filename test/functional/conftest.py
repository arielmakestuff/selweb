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
import sys

# Third-party imports
import pytest

# Local imports
from selweb import core
from selweb.browserdriver import PhantomJSDriver


# ============================================================================
# Specify selenium driver locations
# ============================================================================


@pytest.fixture(scope='session')
def phantomjs_driver(bindir):
    """Return path to phantomjs selenium driver"""
    exe_name = 'phantomjs.exe' if sys.platform == 'win32' else 'phantomjs'
    return bindir / exe_name


@pytest.fixture(scope='session')
def firefox_driver(bindir):
    """Return path to firefox selenium driver"""
    exe_name = 'geckodriver.exe' if sys.platform == 'win32' else 'geckodriver'
    return bindir / exe_name


# ============================================================================
# default browser
# ============================================================================


@pytest.yield_fixture(scope='session')
def browser(phantomjs_driver):
    """Return browser using phantomjs driver"""
    driver = PhantomJSDriver(driver=phantomjs_driver)
    with core.Browser(driver) as browser:
        yield browser


# ============================================================================
#
# ============================================================================
