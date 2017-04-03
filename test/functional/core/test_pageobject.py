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
import re
import sys

# Third-party imports
import pytest

# Local imports


# ============================================================================
# Fixtures
# ============================================================================


@pytest.yield_fixture(scope='module')
def google():
    """Add googlesearch example module"""
    exampledir = str(pytest.config.rootdir / 'example')
    sys.path.insert(0, exampledir)
    import googlesearch
    yield googlesearch
    if 'googlesearch' in sys.modules:
        sys.modules.pop('googlesearch')
    sys.path.remove(exampledir)


# ============================================================================
# Tests
# ============================================================================


def test_tmp(google, bindir):
    """docstring for test_tmp"""
    with google.browser(bindir, google.Driver.firefox) as browser:
        browser.maximize()
        goog = google.GoogleFrontPage(browser)
        goog.go()

        #  print(len(goog))
        search_term = 'wikipedia'
        results_page = goog['searchbar'].submit_search(search_term)
        print(results_page.url)
        print('========')
        for r in results_page['results'].children():
            print(r['title'].title)
            print(r['label'].label)
            print(r['title'].url)
            print(r['summary'].text)
            print()
        #  print(len(results_page['results']))

        #  # Wait until results are loaded
        #  browser.waitfor.title(f'{search_term} - Google Search')
        #  results_div = browser.waitfor.element("//div[@id='resultStats']")
        #  assert re.match('About [0-9]+(,[0-9][0-9][0-9])* results', results_div.text)

        #  # Check there exists a cite element containing the wikipedia url
        #  cite_el = browser.allelements("//div[@id='search']//cite")
        #  text = 'https://www.wikipedia.org/'
        #  assert any(el.text.strip() == text for el in cite_el)


# ============================================================================
#
# ============================================================================
