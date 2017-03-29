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
from time import sleep

# Third-party imports
from pathlib import Path
import pytest

# Local imports
from selweb.browserdriver import FirefoxDriver, PhantomJSDriver


# ============================================================================
#
# ============================================================================


@pytest.mark.skipif(True, reason='dev')
def test_firefox(bindir):
    """docstring for test_tmp"""
    b = Path('c:/users/deocampo/opt/PortableApps/FirefoxPortable/App/Firefox64/firefox.exe')
    assert b.is_file()

    g = bindir / 'geckodriver.exe'
    driver = FirefoxDriver(driver=g, binary=b)
    with driver:
        print('DID FIREFOX START?')
        sleep(1)
    assert True


@pytest.mark.skipif(True, reason='dev')
def test_phantomjs(bindir):
    """docstring for test_phantomjs"""

    seldriver = bindir / 'phantomjs.exe'
    driver = PhantomJSDriver(driver=seldriver)
    with driver:
        print('DID THE BROWSER START?')
    assert True


# ============================================================================
#
# ============================================================================
