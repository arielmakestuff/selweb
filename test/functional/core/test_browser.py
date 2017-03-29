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
from pathlib import Path

# Third-party imports
import pytest
from selenium.webdriver.common.keys import Keys
import re
from yarl import URL

# Local imports
from selweb import core


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def local_htmlfile_url():
    """Return URL pointing to a local html file"""
    file = (Path(pytest.config.rootdir) / 'test' / 'data' /
            'functional' / 'core' / 'test_browser.html')
    return URL(f'file:///{file}')


# ============================================================================
# Tests
# ============================================================================


def test_google_search(browser):
    """Click on google's search bar"""
    search_term = 'wikipedia'

    # Go to google search page
    url = URL('https://google.com')
    browser.go(url)

    # CLick on logo, click on search bar, enter search term, and search
    logo = browser.element("//div[@id='hplogo']")
    searchbar = browser.element("//input[@name='q']")
    with browser.actionchain() as a:

        # Click the logo
        a.move_to_element(logo).click()
        a.perform()

        # Click the search bar, enter search term, and submit
        a.move_to_element(searchbar).click().send_keys(search_term)
        a.send_keys(Keys.RETURN)

    # Wait until results are loaded
    browser.waitfor.title(f'{search_term} - Google Search')
    results_div = browser.waitfor.element("//div[@id='resultStats']")
    assert re.match('About [0-9]+(,[0-9][0-9][0-9])* results', results_div.text)

    # Check there exists a cite element containing the wikipedia url
    cite_el = browser.allelements("//div[@id='search']//cite")
    text = 'https://www.wikipedia.org/'
    assert any(el.text.strip() == text for el in cite_el)


@pytest.mark.parametrize('htmlprop,expected', [
    (core.HTMLProperty.outer, '<div id="answer"><span>FORTY-TWO</span></div>'),
    (core.HTMLProperty.inner, '<span>FORTY-TWO</span>')
])
def test_element_html(browser, local_htmlfile_url, htmlprop, expected):
    """Grab element's html source"""
    browser.go(local_htmlfile_url)
    html = browser.element_html("//div[@id='answer']", htmlprop)
    assert html == expected


def test_maximize(browser):
    """Maximizing the browser does not generate an error"""
    browser.maximize()


def test_location(browser, local_htmlfile_url):
    """Return browser url"""
    browser.go(local_htmlfile_url)
    assert browser.location == local_htmlfile_url


def test_title(browser, local_htmlfile_url):
    """Return browser title"""
    browser.go(local_htmlfile_url)
    assert browser.title == 'FIXME'


# ============================================================================
#
# ============================================================================
