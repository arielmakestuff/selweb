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
from collections import OrderedDict
from contextlib import contextmanager

# Third-party imports
import pytest
from yarl import URL

# Local imports
from selweb.core import Browser, CompositePageObject, Page, PageObject
from selweb.driver import BrowserDriver
from selweb.util import noop_context
import selweb.web as web
from selweb.web import WebPage


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def browser_driver():
    """docstring for browser_driver"""

    class TestBrowserDriver(BrowserDriver):
        pass

    return TestBrowserDriver


# ============================================================================
# Test types
# ============================================================================


@pytest.mark.parametrize('cls', [PageObject, CompositePageObject, Page])
def test_types(browser_driver, cls):
    """Is an instance of PageObject, CompositePageObject, and Page"""

    @browser_driver.register
    class Driver:
        pass

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = Browser(driver)
    w = WebPage(name, url, browser)
    isinstance(w, cls)


# ============================================================================
# Test __init__
# ============================================================================


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_init_arg_url_badtype(val):
    """Raise error if url arg given non-URL object"""
    expected = ('url arg expected URL object, got '
                f'{type(val).__name__} object instead', )

    with pytest.raises(TypeError) as err:
        WebPage('name', url=val, browser=None)

    assert err.value.args == expected


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_init_arg_browser_badtype(val):
    """Raise error if url arg given non-Browser object"""
    expected = ('browser arg expected Browser object, got '
                f'{type(val).__name__} object instead', )
    url = URL('https://google.ca')

    with pytest.raises(TypeError) as err:
        WebPage('name', url, browser=val)

    assert err.value.args == expected


def test_init_default_vals(browser_driver):
    """Initializes as a CompositeWebObject"""

    @browser_driver.register
    class Driver:
        pass

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = Browser(driver)

    w = WebPage(name, url, browser)

    # Check initialized via CompositeWebObject
    assert w.name == name
    assert w.xpath == '/html'
    assert w.absxpath == '/html'
    assert w.parent is None
    assert w.source is None
    assert w.parser is None
    assert w.page is w
    assert w._reload_context is noop_context
    assert w.url == url
    assert w.browser is browser

    # Check objmap attr
    assert isinstance(w._objmap, OrderedDict)
    assert not w._objmap


def test_init_set_parent(webgroup, browser_driver):
    """Assign a parent to a web page (eg iframe)"""

    @webgroup.register
    class TestParent:
        pass

    @browser_driver.register
    class Driver:
        pass

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = Browser(driver)
    parent = TestParent()

    w = WebPage(name, url, browser, parent=parent)
    assert w.parent is parent


# ============================================================================
# Test go
# ============================================================================


def test_go_calls_browser_go(browser_driver):
    """Calls the browser's go() method"""
    called = []

    @browser_driver.register
    class Driver:
        pass

    class TestBrowser(Browser):

        def go(self, url):
            called.append(('called browser.go', url))

    class TestWebPage(WebPage):

        def reload(self):
            pass

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = TestBrowser(driver)

    w = TestWebPage(name, url, browser)
    w.go()

    assert called == [('called browser.go', url)]


def test_go_calls_reload(browser_driver):
    """Calls reload after going to the page's url"""
    called = []

    @browser_driver.register
    class Driver:
        pass

    class TestBrowser(Browser):

        def go(self, url):
            called.append(('called browser.go', url))

    class TestWebPage(WebPage):

        def reload(self):
            called.append('called page.reload')

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = TestBrowser(driver)

    w = TestWebPage(name, url, browser)
    w.go()

    assert called == [('called browser.go', url), 'called page.reload']


# ============================================================================
# Test reload
# ============================================================================


def test_reload_under_context(monkeypatch, browser_driver):
    """docstring for test_reload_under_context"""
    called = []

    def fake_fromstring(n):
        called.append(('fromstring', n))
        return 42

    monkeypatch.setattr(web.html, 'fromstring', fake_fromstring)

    @contextmanager
    def rcontext():
        called.append('enter rcontext')
        yield
        called.append('exit rcontext')

    @browser_driver.register
    class Driver:
        pass

    class TestBrowser(Browser):
        @property
        def source(self):
            called.append('browser.source')
            return 9001

    class TestWebPage(WebPage):

        def clear(self):
            called.append('called clear')

    name = 'name'
    url = URL('https://google.ca')
    driver = Driver()
    browser = TestBrowser(driver)

    w = TestWebPage(name, url, browser, reloadcontext=rcontext)
    w.reload()

    # Note: this is not to check that specific actions are taken, only that
    # reload actions happen within a reload context
    assert called == ['enter rcontext', 'browser.source', ('fromstring', 9001),
                      'called clear', 'exit rcontext']


# ============================================================================
#
# ============================================================================
