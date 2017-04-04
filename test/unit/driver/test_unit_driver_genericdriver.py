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
from selweb.driver import (BrowserDriver, FirefoxDriver, GenericDriver,
                           PhantomJSDriver)


# ============================================================================
# Test __init__
# ============================================================================


def test_init_attributes():
    """Expected attributes are set on the object"""
    expected = ['_driveropt', '_drivercls', '_driver']
    driver = GenericDriver(42)

    for name in expected:
        assert hasattr(driver, name)


@pytest.mark.parametrize('optdict', [{}, {'answer': 42}])
def test_init_attrvals(optdict):
    """Attribute values initialized based on args"""
    assert isinstance(optdict, dict)

    clsval = 42
    driver = GenericDriver(clsval, **optdict)

    # Check _driveropt
    assert driver._driveropt is not optdict
    assert driver._driveropt == optdict

    # Check _drivercls
    assert driver._drivercls == clsval

    # Check _driver
    assert driver._driver is None


# ============================================================================
# Test mkdriver()
# ============================================================================


def fake_drivercls(**kwargs):
    ret = [42]
    ret.extend(kwargs.items())
    return ret


def test_mkdriver_create_instance():
    """Create instance of the underlying selenium driver"""
    driver = GenericDriver(fake_drivercls)
    val = driver.mkdriver()

    assert val == [42]


def test_mkdriver_driver_options_used():
    """Driver options used to instantiate driver object"""
    driver = GenericDriver(fake_drivercls, answer=42)
    val = driver.mkdriver()

    assert val == [42, ('answer', 42)]


# ============================================================================
# Test driver
# ============================================================================


class FakeDriverClass:

    def __init__(self, **kwargs):
        pass

    def quit(self):
        print('{} QUIT CALLED'.format(self.__class__.__name__.upper()))


def test_driver_noinstance():
    """driver property is None if not inside of a BrowserDriver context"""
    driver = GenericDriver(FakeDriverClass)
    assert driver.driver is None


def test_driver_instance():
    """driver property inside of BrowserDriver context"""
    driver = GenericDriver(FakeDriverClass)
    with driver as d:
        assert driver.driver is d
        assert isinstance(driver.driver, FakeDriverClass)


# ============================================================================
# Test context
# ============================================================================


class EnterTest(GenericDriver):

    def mkdriver(self):
        print('MKDRIVER CALLED')
        return super().mkdriver()


def test_enter_mkdriver_called(capsys):
    """Entering a driver context calls mkdriver()"""
    driver = EnterTest(FakeDriverClass)
    with driver as d:
        out, err = capsys.readouterr()
        assert out.strip() == 'MKDRIVER CALLED'


def test_exit_quit_called(capsys):
    """Exiting a context calls selenium driver's quit() method"""
    driver = GenericDriver(FakeDriverClass)
    with driver:
        pass
    out, err = capsys.readouterr()
    assert out.strip() == '{} QUIT CALLED'.format(FakeDriverClass.__name__.
                                                  upper())


# ============================================================================
# Test BrowserDriver implementation registrations
# ============================================================================


def test_browserdriver_genericdriver():
    """GenericDriver is registered as implementing BrowserDriver"""
    assert issubclass(GenericDriver, BrowserDriver)


def test_browserdriver_firefox():
    """FirefoxDriver is registered as implementing BrowserDriver"""
    assert issubclass(FirefoxDriver, BrowserDriver)


def test_browserdriver_phantomjs():
    """PhantomJSDriver is registered as implementing BrowserDriver"""
    assert issubclass(PhantomJSDriver, BrowserDriver)


# ============================================================================
#
# ============================================================================
