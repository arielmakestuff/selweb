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
from contextlib import contextmanager

# Third-party imports
import pytest
from yarl import URL

# Local imports
import selweb.core as core
from selweb.core import Browser
from selweb.driver import BrowserDriver


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
# Test __init__
# ============================================================================


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_init_badarg(val):
    """Raise error if driver arg is given a non-BrowserDriver object"""
    expected = ('driver arg expected BrowserDriver object, got {} instead'.
                 format(type(val).__name__), )

    with pytest.raises(TypeError) as err:
        Browser(val)

    assert err.value.args == expected

def test_init_driver_value(browser_driver):
    """value of driver arg is saved on the Browser object"""

    @browser_driver.register
    class Driver:
        pass

    driver = Driver()
    b = Browser(driver)
    assert hasattr(b, '_driver')
    assert b._driver is driver


# ============================================================================
# Test context methods
# ============================================================================


def test_context_driver_context(browser_driver):
    """Enters underlying driver's context"""
    val = []

    @browser_driver.register
    class Test:

        def __enter__(self):
            val.append(0)
            return 42

        def __exit__(self, exctype, exc, exctb):
            val.append(1)

    context = Test()
    b = Browser(context)
    browser_context = b.__enter__()
    assert browser_context is b
    assert val == [0]


def test_context_exit_driver_context(browser_driver):
    """Exit underlying driver's context"""
    val = []

    @browser_driver.register
    class Test:

        def __enter__(self):
            val.append(0)
            return 42

        def __exit__(self, exctype, exc, exctb):
            val.append(1)

    context = Test()
    b = Browser(context)
    with Browser(context) as b:
        assert val == [0]

    assert val == [0, 1]


# ============================================================================
# Test actionchain
# ============================================================================


def test_actionchain_return_actionchain(monkeypatch, browser_driver):
    """Entering context creates a selenium ActionChains object"""

    store = []
    class FakeActionChains:

        def __init__(self, driver):
            self.driver = driver
            store.append('INIT')

        def perform(self):
            store.append('PERFORM')

    @browser_driver.register
    class FakeDriver:
        driver = 42

    monkeypatch.setattr(core, 'ActionChains', FakeActionChains)

    # Check ActionChains is instantiated with the value from browser's
    # selenium_driver property
    browser = Browser(FakeDriver())
    with browser.actionchain() as val:
        assert isinstance(val, FakeActionChains)
        assert store == ['INIT']
        assert val.driver == FakeDriver.driver


def test_actionchain_perform_actions(monkeypatch, browser_driver):
    """Actions are performed when leaving actionchain context"""

    store = []
    class FakeActionChains:

        def __init__(self, driver):
            self.driver = driver
            store.append('INIT')

        def perform(self):
            store.append('PERFORM')

    @browser_driver.register
    class FakeDriver:
        driver = 42

    monkeypatch.setattr(core, 'ActionChains', FakeActionChains)

    # Check ActionChains is instantiated with the value from browser's
    # selenium_driver property
    browser = Browser(FakeDriver())
    with browser.actionchain():
        pass

    assert store == ['INIT', 'PERFORM']


# ============================================================================
# Test allelements
# ============================================================================


def test_allelements_calls_selenium_method(browser_driver):
    """Calls find_elements_by_xpath"""

    called = []
    class FakeSeleniumDriver:

        def find_elements_by_xpath(self, xpath):
            called.append(xpath)
            return 42

    @browser_driver.register
    class FakeDriver:

        @property
        def driver(self):
            return FakeSeleniumDriver()

    b = Browser(FakeDriver())
    assert b.allelements(0) == 42
    assert called == [0]


# ============================================================================
# Test element
# ============================================================================


def test_element_calls_selenium_method(browser_driver):
    """Calls find_element_by_xpath"""

    called = []
    class FakeSeleniumDriver:

        def find_element_by_xpath(self, xpath):
            called.append(xpath)
            return 42

    @browser_driver.register
    class FakeDriver:

        @property
        def driver(self):
            return FakeSeleniumDriver()

    b = Browser(FakeDriver())
    assert b.element(0) == 42
    assert called == [0]


# ============================================================================
# Test element_html
# ============================================================================

@pytest.mark.parametrize('val', [42, 4.2, ['42']])
def test_element_html_badarg_el_or_xpath(val, browser_driver):
    """Raise error if el_or_xpath arg given non-str non-WebElement"""
    @browser_driver.register
    class FakeDriver:
        pass

    expected = ('el_or_xpath expected str or WebElement object, got '
                f'{type(val).__name__} object instead', )
    b = Browser(FakeDriver())
    with pytest.raises(TypeError) as err:
        b.element_html(val)

    assert err.value.args == expected


@pytest.mark.parametrize('val', [42, 4.2, ['42']])
def test_element_html_badarg_htmlproperty(val, browser_driver):
    """Raise error if htmlproperty arg given non-HTMLProperty"""

    @browser_driver.register
    class FakeDriver:
        pass

    expected = ('htmlproperty expected HTMLProperty object, got '
                f'{type(val).__name__} object instead', )
    b = Browser(FakeDriver())
    with pytest.raises(TypeError) as err:
        b.element_html('hello', val)

    assert err.value.args == expected


def test_element_html_convert_str(monkeypatch, browser_driver):
    """Converts str el_or_xpath to WebElement"""

    called = []
    class FakeWebElement:

        def get_attribute(self, val):
            called.append(('get_attribute', val))
            return 42

    class FakeSeleniumDriver:

        def find_element_by_xpath(self, xpath):
            called.append(('find_element_by_xpath', xpath))
            return FakeWebElement()

    @browser_driver.register
    class FakeDriver:

        @property
        def driver(self):
            return FakeSeleniumDriver()

    # This is needed to pass type checks in element_html()
    monkeypatch.setattr(core, 'WebElement', FakeWebElement)

    b = Browser(FakeDriver())
    retval = b.element_html('/hello', core.HTMLProperty.outer)
    assert retval == 42
    assert called == [
        ('find_element_by_xpath', '/hello' ),
        ('get_attribute', core.HTMLProperty.outer.value)
    ]


def test_element_html_call_get_attribute(monkeypatch, browser_driver):
    """Calls el_or_xpath WebElement attr get_attribute"""

    called = []
    class FakeWebElement:

        def get_attribute(self, val):
            called.append(('get_attribute', val))
            return 42

    @browser_driver.register
    class FakeDriver:
        pass

    # This is needed to pass type checks in element_html()
    monkeypatch.setattr(core, 'WebElement', FakeWebElement)

    b = Browser(FakeDriver())
    fake_el = FakeWebElement()
    retval = b.element_html(fake_el, core.HTMLProperty.outer)
    assert retval == 42
    assert called == [
        ('get_attribute', core.HTMLProperty.outer.value)
    ]


# ============================================================================
# Test go
# ============================================================================


@pytest.mark.parametrize('val', [42, '42', 4.2])
def test_go_badarg_url(val, browser_driver):
    """Raise error if url arg is given a non yarl.URL object"""
    @browser_driver.register
    class FakeDriver:
        pass

    expected = (f'url arg expected URL object, got {type(val).__name__} '
                'object instead', )
    b = Browser(FakeDriver())
    with pytest.raises(TypeError) as err:
        b.go(val)

    assert err.value.args == expected


def test_go_waitfor_pageload_context_get(browser_driver):
    """Calls selenium get() method under pageload context"""
    called = []

    class TestWaitFor:

        @contextmanager
        def pageload(self, *, timeout=1):
            """docstring for pageload"""
            called.append(('entered pageload', timeout))
            yield
            called.append('exiting pageload')

    class FakeSeleniumDriver:

        def get(self, url):
            called.append(('get', url))

    @browser_driver.register
    class FakeDriver:
        driver = FakeSeleniumDriver()

    class TestBrowser(Browser):
        waitfor = TestWaitFor()

    url = URL('https://google.ca')
    b = TestBrowser(FakeDriver())
    b.go(url, timeout=42)

    assert called == [
        ('entered pageload', 42),
        ('get', str(url)),
        'exiting pageload'
    ]


# ============================================================================
# Test maximze
# ============================================================================


def test_maximize_calls_selenium_method(browser_driver):
    """Calls selenium maximize()"""
    called = []

    class FakeSeleniumDriver:

        def maximize_window(self):
            called.append('maximize_window')

    @browser_driver.register
    class FakeDriver:
        driver = FakeSeleniumDriver()

    b = Browser(FakeDriver())
    b.maximize()

    assert called == ['maximize_window']


# ============================================================================
# Test switch
# ============================================================================


def test_switch_noiframe(browser_driver):
    """Switch to default content if nothing passed to iframe arg"""

    called = []

    class FakeSwitch:

        def default_content(self):
            called.append('default_content')

    class FakeSeleniumDriver:
        switch_to = FakeSwitch()

    @browser_driver.register
    class FakeDriver:
        driver = FakeSeleniumDriver()

    b = Browser(FakeDriver())
    b.switch()
    assert called == ['default_content']


def test_switch_with_iframe(browser_driver):
    """Switch to iframe's element"""

    called = []

    class FakeElement:
        element = 42

    class FakeSwitch:

        def frame(self, el):
            called.append(('frame', el))

    class FakeSeleniumDriver:
        switch_to = FakeSwitch()

    @browser_driver.register
    class FakeDriver:
        driver = FakeSeleniumDriver()

    b = Browser(FakeDriver())
    b.switch(FakeElement())
    assert called == [('frame', 42)]


# ============================================================================
# Test driver
# ============================================================================


def test_driver_saved_driver(browser_driver):
    """driver property returns saved browser driver object"""

    @browser_driver.register
    class FakeDriver:
        pass

    driver = FakeDriver()
    b = Browser(driver)
    assert b.driver is driver


# ============================================================================
# Test location
# ============================================================================


def test_location(browser_driver):
    """Returns a URL object"""

    @browser_driver.register
    class FakeDriver:
        class driver:
            current_url = 'https://google.ca'

    b = Browser(FakeDriver())
    loc = b.location
    assert isinstance(loc, URL)
    assert str(loc) == 'https://google.ca'


# ============================================================================
# Test selenium_driver
# ============================================================================


def test_selenium_driver(browser_driver):
    """Returns underlying selenium driver"""

    @browser_driver.register
    class FakeDriver:
        driver = 42

    b = Browser(FakeDriver())
    assert b.selenium_driver == 42


# ============================================================================
# Test title
# ============================================================================


def test_title(browser_driver):
    """Returns title reported by selenium"""

    @browser_driver.register
    class FakeDriver:
        class driver:
            title = 42

    b = Browser(FakeDriver())
    assert b.title == 42


# ============================================================================
# Test source
# ============================================================================


def test_source(browser_driver):
    """Returns page source reported by selenium"""

    @browser_driver.register
    class FakeDriver:
        class driver:
            page_source = 42

    b = Browser(FakeDriver())
    assert b.source == 42


# ============================================================================
#
# ============================================================================
