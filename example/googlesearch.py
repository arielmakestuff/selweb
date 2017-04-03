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
from enum import Enum
from html import unescape
from pathlib import Path
import re
import sys

# Third-party imports
from lxml import html
import pytest
from selenium.webdriver.common.keys import Keys
from yarl import URL

# Local imports
from selenium import webdriver
from selweb.driver import (BrowserDriver, FirefoxDriver, GenericDriver,
                           PhantomJSDriver)
from selweb import (Browser, WebObject, CompositeWebObject, WebPage)
from selweb.util import xpath_clsmatch


# ============================================================================
# Custom driver/browser
# ============================================================================


@BrowserDriver.register
class ChromeDriver(GenericDriver):
    __slots__ = ()

    def __init__(self, *, driver=None):
        options = dict()
        if driver:
            options.update(executable_path=str(driver))
        super().__init__(webdriver.Chrome, **options)


class PhantomJS:

    @staticmethod
    def driver(bindir):
        exe_name = 'phantomjs.exe' if sys.platform == 'win32' else 'phantomjs'
        bin = bindir / exe_name
        driver = PhantomJSDriver(driver=bin)
        return driver


class Chrome:

    @staticmethod
    def driver(bindir):
        exe_name = 'chromedriver.exe' if sys.platform == 'win32' else 'chromedriver'
        bin = bindir / exe_name
        driver = ChromeDriver(driver=bin)
        return driver


class Firefox:

    @staticmethod
    def driver(bindir, *, binary=None):
        exe_name = 'geckodriver.exe' if sys.platform == 'win32' else 'geckodriver'
        bin = bindir / exe_name
        driver = FirefoxDriver(driver=bin, binary=binary)
        return driver


class Driver(Enum):
    chrome = Chrome
    firefox = Firefox
    phantomjs = PhantomJS


@contextmanager
def browser(bindir, driver):
    """Return browser using chrome driver"""
    if not isinstance(driver, Driver):
        errmsg = ('driver arg expected {} object, got {} object instead'.
                  format(Driver.__name__, type(driver).__name__))
        raise TypeError(errmsg)
    with Browser(driver.value.driver(bindir)) as browser:
        yield browser


# ============================================================================
# Google front page
# ============================================================================


class GoogleLogo(WebObject):

    def __init__(self, parent):
        xpath = "//*[@id='hplogo']"
        super().__init__('logo', xpath, parent)


class SearchBar(WebObject):

    def __init__(self, parent):
        xpath = "//input[@name='q']"
        super().__init__('searchbar', xpath, parent)

    def submit_search(self, text):
        """docstring for enter_text"""
        browser = self.browser
        searchbar = browser.element(self.absxpath)

        # The following context block is commented due to a bug in geckdriver
        # with browser.actionchain() as a:
        #     #  Click the search bar, enter search term, and submit
        #     a.move_to_element(searchbar).click().send_keys(text)
        #     a.send_keys(Keys.RETURN)

        # Click the search bar, enter search term, and submit
        searchbar.click()
        searchbar.send_keys(text)
        searchbar.send_keys(Keys.RETURN)

        #  Return the results page
        browser.waitfor.title(f'{text} - Google Search', timeout=5)
        new_url = browser.location
        ret = GoogleResultPage(new_url, browser)
        ret.reload()
        return ret


class GoogleFrontPage(WebPage):

    def __init__(self, browser):
        url = URL('https://www.google.ca')
        super().__init__('google_front', url, browser,
                         reloadcontext=self.reload_context)

    @contextmanager
    def reload_context(self):
        yield

        # Add sub objects
        self.add(GoogleLogo(self))
        self.add(SearchBar(self))

        for c in self.children():
            c.reload()


# ============================================================================
# GoogleSearchResults
# ============================================================================


class SearchItemTitle(WebObject):

    def __init__(self, parent):
        clsname = xpath_clsmatch('r')
        xpath = f'//h3[{clsname}]'
        super().__init__('title', xpath, parent)

        self._bs = None

    @property
    def url(self):
        a = html.fromstring(self.source)[0]
        url = unescape(a.get('href'))

        # Remove the query frag
        frag = '/url?q='
        if url.startswith(frag):
            url = url.replace(frag, '', 1)

        # Remove google added url vars
        regex = '[&]sa[=][a-zA-Z][&]ved[=]'
        match = re.search(regex, url)
        if match:
            url = url[:match.start()]

        # Return an absolute url
        url = URL(url)
        if not url.is_absolute():
            url = self.page.url.join(url)

        # Remove any trailing foreslashes
        parts = url.parts
        if parts[-1] == '':
            new_path = '/'.join(('', ) + url.parts[1:-1])
            url = url.with_path(new_path)
        return url

    @property
    def title(self):
        """Return title text"""
        src = self.source
        parser = html.document_fromstring(src)
        return parser.text_content()

    @property
    def absxpath(self):
        # Possible that a search item can contain child search items (eg top
        # result item), we don't care about those, just the first one
        xpath = self.parent.absxpath
        xpath = ''.join([xpath, self.xpath])
        return f"({xpath})[1]"


class SearchItemLabel(WebObject):

    def __init__(self, parent):
        clsname = xpath_clsmatch('s')
        xpath = f"//div[{clsname}]//cite"
        super().__init__('label', xpath, parent)

    @property
    def label(self):
        """Return label"""
        src = self.source
        parser = html.document_fromstring(src)
        return parser.text_content().strip()

    @property
    def absxpath(self):
        xpath = self.parent.absxpath
        xpath = ''.join([xpath, self.xpath])
        return f"({xpath})[1]"


class SearchItemSummary(WebObject):

    def __init__(self, parent):
        cls_s = xpath_clsmatch('s')
        cls_st = xpath_clsmatch('st')
        xpath = f"//div[{cls_s}]//span[{cls_st}]"
        super().__init__('summary', xpath, parent)

    @property
    def text(self):
        """Return summary text"""
        src = self.source
        parser = html.document_fromstring(src)
        return parser.text_content().strip()

    @property
    def absxpath(self):
        xpath = self.parent.absxpath
        xpath = ''.join([xpath, self.xpath])
        return f"({xpath})[1]"


class SearchItem(CompositeWebObject):

    # the name will be the index number
    def __init__(self, parent, *, index=0):
        if not isinstance(index, int):
            errmsg = ('index arg expected {} object, got {} object instead'.
                      format(int.__name__, type(index).__name__))
            raise TypeError(errmsg)
        elif index < 0:
            errmsg = ('index arg expected to be >= 0, got {} instead'.
                      format(index))
            raise ValueError(errmsg)

        label = SearchItemLabel(self)
        cls_r = xpath_clsmatch('r')
        xpath = f"//h3[{cls_r}]/parent::node()[.{label.xpath}]"
        super().__init__(index, xpath, parent, reloadcontext=self.reload_context)

    @contextmanager
    def reload_context(self):
        yield

        # Run after core reload is done
        title = SearchItemTitle(self)
        label = SearchItemLabel(self)
        summary = SearchItemSummary(self)
        for item in [title, label, summary]:
            self.add(item)
            item.reload()

    @property
    def absxpath_noindex(self):
        """Return the non-indexed xpath"""
        return super().absxpath

    @property
    def absxpath(self):
        xpath = super().absxpath
        return f"({xpath})[{self.name+1}]"


class ResultList(CompositeWebObject):

    def __init__(self, parent):
        xpath = "//div[@id='res']"
        super().__init__('results', xpath, parent,
                         reloadcontext=self.reload_context)

    @contextmanager
    def reload_context(self):
        yield
        # Run after core reload

        # Get lxml.html parser for this object to find sub items
        item = SearchItem(self)
        item_xpath = ''.join([self.xpath, item.xpath])
        src = self.source
        parser = html.fromstring(src)
        results = parser.xpath(item_xpath)

        for i, el in enumerate(results):
            if i > 0:
                item = SearchItem(self, index=i)
            self.add(item)
            try:
                item.reload()
            except Exception as err:
                print('ERROR', item.absxpath, err)
                break


class GoogleResultPage(WebPage):

    def __init__(self, url, browser):
        super().__init__('google_results', url, browser,
                         reloadcontext=self.reload_context)

    @contextmanager
    def reload_context(self):
        yield

        # Run after core reload is done
        results = ResultList(self)
        self.add(results)
        results.reload()


# ============================================================================
#
# ============================================================================
