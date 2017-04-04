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
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# Local imports
from selweb.driver import GenericDriver, FirefoxDriver


# ============================================================================
# Test init
# ============================================================================


class InitMixin(GenericDriver):

    def __init__(self, drivercls, **options):
        self.args = (drivercls, options)


class InitFakeFirefoxDriver(FirefoxDriver, InitMixin):
    pass


def test_init_no_options():
    """Options kwarg is empty if driver and binary args are both None"""
    driver = InitFakeFirefoxDriver()
    cls, options = driver.args
    assert not options
    assert cls is webdriver.Firefox


def test_init_executable_path():
    """Driver is passed via executable_path kwarg"""
    driver = InitFakeFirefoxDriver(driver=42)
    cls, options = driver.args
    assert options == dict(executable_path='42')
    assert cls is webdriver.Firefox


def test_init_firefox_binary(bindir):
    """Firefox executable path passed via firefox_binary kwarg"""
    # This path is NOT to a firefox executable, it's only used to test what
    # value is passed to GenericDriver
    path = bindir / 'geckodriver.exe'
    driver = InitFakeFirefoxDriver(binary=path)
    cls, options = driver.args
    assert len(options) == 1
    driver_bin = options['firefox_binary']
    assert isinstance(driver_bin, FirefoxBinary)
    assert driver_bin._start_cmd == str(path)
    assert cls is webdriver.Firefox


def test_init_allopt(bindir):
    """Driver and binary values passed to GenericDriver via kwargs"""
    # This path is NOT to a firefox executable, it's only used to test what
    # value is passed to GenericDriver
    path = bindir / 'geckodriver.exe'
    driver = InitFakeFirefoxDriver(driver=42, binary=path)
    cls, options = driver.args
    assert len(options) == 2
    assert options['executable_path'] == '42'
    driver_bin = options['firefox_binary']
    assert isinstance(driver_bin, FirefoxBinary)
    assert driver_bin._start_cmd == str(path)
    assert cls is webdriver.Firefox



# ============================================================================
#
# ============================================================================
