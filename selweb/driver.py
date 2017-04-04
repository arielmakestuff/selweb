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
from abc import abstractmethod
from contextlib import AbstractContextManager, contextmanager

# Third-party imports
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# Local imports


# ============================================================================
# Drivers
# ============================================================================


class BrowserDriver(AbstractContextManager):

    @abstractmethod
    def mkdriver(self):
        """Return an instance of a selenium web driver"""
        raise NotImplementedError

    @property
    @abstractmethod
    def driver(self):
        """Return the underlying selenium webdriver object"""
        raise NotImplementedError


@BrowserDriver.register
class GenericDriver:
    __slots__ = ('_driveropt', '_drivercls', '_driver')

    def __init__(self, drivercls, **options):
        self._driveropt = options
        self._drivercls = drivercls
        self._driver = None

    def __enter__(self):
        self._driver = driver = self.mkdriver()
        return driver

    def __exit__(self, exctype, exc, exctb):
        self._driver.quit()
        self._driver = None

    def mkdriver(self):
        """Create an instance of the firefox webdriver"""
        return self._drivercls(**self._driveropt)

    @property
    def driver(self):
        """Return the underlying webdriver object"""
        return self._driver


class PhantomJSDriver(GenericDriver):
    __slots__ = ()

    def __init__(self, *, driver=None):
        options = dict()
        if driver:
            options.update(executable_path=str(driver))
        super().__init__(webdriver.PhantomJS, **options)


class FirefoxDriver(GenericDriver):
    __slots__ = ()

    def __init__(self, *, driver=None, binary=None):
        options = dict()
        if binary:
            binary = FirefoxBinary(str(binary))
            options.update(firefox_binary=binary)
        if driver:
            options.update(executable_path=str(driver))
        super().__init__(webdriver.Firefox, **options)


# ============================================================================
#
# ============================================================================
