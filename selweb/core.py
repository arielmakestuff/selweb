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
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from enum import Enum
from functools import partial

# Third-party imports
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from yarl import URL

# Local imports
from .driver import BrowserDriver


# ============================================================================
# Globals
# ============================================================================


class HTMLProperty(Enum):
    inner = 'innerHTML'
    outer = 'outerHTML'


# ============================================================================
# Browser
# ============================================================================


class WaitFor:
    __slots__ = ('_parent', )

    def __init__(self, *, parent=None):
       self._parent = parent

    def __get__(self, obj, type=None):
        """docstring for __get__"""
        return self.__class__(parent=obj)

    def __call__(self, condition_func, *, xpath=None, timeout=1):
        funcarg = [(By.XPATH, xpath)] if xpath is not None else []
        el = WebDriverWait(self._parent.selenium_driver, timeout).until(
            condition_func(*funcarg)
        )
        return el

    def alert(self, *, timeout=1):
        """Wait for an alert to be present"""
        condfunc = ec.alert_is_present
        return self.__call__(condfunc, timeout=timeout)

    def element(self, xpath, *, timeout=1):
        condfunc = ec.presence_of_element_located
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    def allelements(self, xpath, *, timeout=1):
        condfunc = ec.presence_of_all_elements_located
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    def element_text(self, xpath, text, *, timeout=1):
        """Wait for element that has given text"""
        condfunc = partial(ec.text_to_be_present_in_element, (By.XPATH, xpath), text)
        return self.__call__(condfunc, timeout=timeout)

    def element_value(self, xpath, text, *, timeout=1):
        """Wait for element that has given text as the value of its value attribute"""
        condfunc = partial(ec.text_to_be_present_in_element_value, (By.XPATH, xpath), text)
        return self.__call__(condfunc, timeout=timeout)

    def element_clickable(self, xpath, *, timeout=1):
        """Wait for element to be visible and enabled so that it can be clicked"""
        condfunc = ec.element_to_be_clickable
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    def element_invisible(self, xpath, *, timeout=1):
        """Wait for element that is either invisible or not present in the DOM"""
        condfunc = ec.invisibility_of_element_located
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    def element_visible(self, xpath, *, timeout=1):
        """Wait for element to exist and to be visible"""
        condfunc = ec.visibility_of_element_located
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    def allelements_visible(self, xpath, *, timeout=1):
        """Wait for one or more elements to exist and to be visible"""
        condfunc = ec.visibility_of_any_elements_located
        return self.__call__(condfunc, xpath=xpath, timeout=timeout)

    @contextmanager
    def pageload(self, *, timeout=30):
        old_page = self.element('/html')
        yield
        self.stale_element(old_page, timeout=timeout)

    def stale_element(self, element, *, timeout=1):
        """Wait for the given element to no longer attached to the DOM"""
        condfunc = partial(ec.staleness_of, element)
        return self.__call__(condfunc, timeout=timeout)

    def isvisible(self, element, *, timeout=1):
        """Wait for an existing element to become visible"""
        condfunc = partial(ec.visibility_of, element)
        return self.__call__(condfunc, timeout=timeout)

    def title(self, text, *, timeout=1):
        """Wait for the page title to match the given text"""
        condfunc = partial(ec.title_is, text)
        return self.__call__(condfunc, timeout=timeout)

    def title_substring(self, text, *, timeout=1):
        """Wait for the page title to contain the given text"""
        condfunc = partial(ec.title_contains, text)
        return self.__call__(condfunc, timeout=timeout)


class Browser:
    __slots__ = ('_driver', )

    # Data descriptors
    waitfor = WaitFor()

    def __init__(self, driver):
        if not isinstance(driver, BrowserDriver):
            msg = ('driver arg expected {} object, got {} instead'.
                   format(BrowserDriver.__name__, type(driver).__name__))
            raise TypeError(msg)
        self._driver = driver

    def __enter__(self):
        self._driver.__enter__()
        return self

    def __exit__(self, exctype, exc, exctb):
        return self._driver.__exit__(exctype, exc, exctb)

    @contextmanager
    def actionchain(self):
        """Perform a series of browser actions"""
        actions = ActionChains(self.selenium_driver)
        yield actions
        actions.perform()

    def allelements(self, xpath):
        """Return list of selenium elements representing xpath"""
        return self.selenium_driver.find_elements_by_xpath(xpath)

    def element(self, xpath):
        """Return selenium element representing xpath"""
        return self.selenium_driver.find_element_by_xpath(xpath)

    def element_html(self, el_or_xpath, htmlproperty=HTMLProperty.inner):
        """Return either the innerHTML or outerHTML value of an element"""
        errmsg = None
        if not isinstance(el_or_xpath, (str, WebElement)):
            errmsg = ('el_or_xpath expected {} or {} object, got {} object instead'.
                      format('str', WebElement.__name__, type(el_or_xpath).__name__))
        elif not isinstance(htmlproperty, HTMLProperty):
            errmsg = ('htmlproperty expected {} object, got {} object instead'.
                      format(HTMLProperty.__name__, type(htmlproperty).__name__))
        if errmsg:
            raise TypeError(errmsg)

        el = el_or_xpath
        if isinstance(el, str):
            el = self.element(el)
        return el.get_attribute(htmlproperty.value)

    def go(self, url, *, timeout=1):
        """Visit a url"""
        if not isinstance(url, URL):
            msg = ('url arg expected {} object, got {} object instead'.
                   format(URL.__name__, type(url).__name__))
            raise TypeError(msg)
        with self.waitfor.pageload(timeout=timeout):
            self.selenium_driver.get(str(url))

    def maximize(self):
        """Maximize the browser window"""
        self.selenium_driver.maximize_window()

    def switch(self, iframe=None):
        """Switch context"""
        switch = self.selenium_driver.switch_to
        if iframe is None:
            switch.default_content()
        else:
            switch.frame(iframe.element)

    @property
    def driver(self):
        """Return BrowserDriver object associated with this Browser"""
        return self._driver

    @property
    def location(self):
        """Return browser's current url"""
        return URL(self.selenium_driver.current_url)

    @property
    def selenium_driver(self):
        """Return underlying selenium WebDriver object"""
        return self._driver.driver

    @property
    def title(self):
        """Page title"""
        return self.selenium_driver.title

    @property
    def source(self):
        """Retrieve page source"""
        return self.selenium_driver.page_source


# ============================================================================
# Context
# ============================================================================


class PageObject(metaclass=ABCMeta):
    """Describes a set of web elements"""

    # --------------------
    # General methods
    # --------------------

    @abstractmethod
    def __bool__(self):
        """Return whether the page object is valid"""
        raise NotImplementedError

    @abstractmethod
    def reload(self):
        """Reload the page object"""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        """Retrieve object's name

        This is used as a key on the object's parent

        """
        raise NotImplementedError

    @property
    @abstractmethod
    def source(self):
        """Retrieve object's source"""
        raise NotImplementedError

    @property
    @abstractmethod
    def xpath(self):
        """Calculate and return the xpath to the page object"""
        raise NotImplementedError

    @property
    @abstractmethod
    def absxpath(self):
        """Calculate and return the absolute xpath to the page object"""
        raise NotImplementedError

    @property
    @abstractmethod
    def browser(self):
        """Return the browser"""
        raise NotImplementedError

    @property
    @abstractmethod
    def visible(self):
        """Return True if the page object is visible"""
        raise NotImplementedError

    @property
    @abstractmethod
    def page(self):
        """Return the object's page"""
        raise NotImplementedError

    @property
    @abstractmethod
    def parent(self):
        """Return the parent page object"""
        raise NotImplementedError

    @parent.setter
    @abstractmethod
    def parent(self, parent):
        """Set the parent page object"""
        raise NotImplementedError


# ============================================================================
# Container
# ============================================================================


class CompositePageObject(PageObject):

    # --------------------
    # Container methods
    # --------------------

    @abstractmethod
    def __getitem__(self, name):
        """Retrieve a child page object by name"""
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, name):
        """Remove a child page object by name"""
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        """Iterate over names of child page objects"""
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        """Return the number of child page objects"""
        raise NotImplementedError

    @abstractmethod
    def add(self, obj):
        """Add a new child page object"""
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """Remove all child page objects"""
        raise NotImplementedError

    @abstractmethod
    def children(self):
        """Iterator over child page objects"""
        raise NotImplementedError


class Page(CompositePageObject):

    @abstractmethod
    def go(self):
        """Retrieve the page"""
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self):
        """Return the current page's location"""
        raise NotImplementedError

    @property
    @abstractmethod
    def parser(self):
        """Return an lxml parser"""
        raise NotImplementedError


# ============================================================================
#
# ============================================================================
