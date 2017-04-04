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
from selenium import webdriver

# Local imports
from selweb.driver import GenericDriver, PhantomJSDriver


# ============================================================================
# Test init
# ============================================================================


class InitMixin(GenericDriver):

    def __init__(self, drivercls, **options):
        self.args = (drivercls, options)


class InitFakePhantomDriver(PhantomJSDriver, InitMixin):
    pass


def test_init_no_options():
    """Options kwarg is empty if driver is None"""
    driver = InitFakePhantomDriver()
    cls, options = driver.args
    assert not options
    assert cls is webdriver.PhantomJS


def test_init_executable_path():
    """Driver is passed via executable_path kwarg"""
    driver = InitFakePhantomDriver(driver=42)
    cls, options = driver.args
    assert options == dict(executable_path='42')
    assert cls is webdriver.PhantomJS


# ============================================================================
#
# ============================================================================
