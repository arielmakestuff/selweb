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

# Local imports
from selweb.core import CompositePageObject
from selweb.util import noop_context
import selweb.web as web
from selweb.web import WebObject


# ============================================================================
# Test __init__
# ============================================================================


@pytest.mark.parametrize('val', [42, 4.2, ['42']])
def test_init_arg_xpath_nonstr(val):
    """Raise error if xpath arg is not a string"""
    expected = (f'xpath arg expected str object, got {type(val).__name__} '
                'object instead', )
    with pytest.raises(TypeError) as err:
        WebObject('hello', val, parent=None)

    assert err.value.args == expected


@pytest.mark.parametrize('val', ['hello'])
def test_init_arg_xpath_badval(val):
    """Raise error if xpath arg does not start with a foreslash"""
    expected = ('Given xpath missing leading /', )
    with pytest.raises(ValueError) as err:
        WebObject('hello', val, parent=None)

    assert err.value.args == expected


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_init_arg_parent_badtype(val):
    """Raise error if parent arg given non-CompositePageObject object"""
    expected = ('parent arg expected CompositePageObject object, '
                f'got {type(val).__name__} object instead', )
    with pytest.raises(TypeError) as err:
        WebObject('hello', '/hello', val)

    assert err.value.args == expected


def test_init_default_attr_values(webgroup):
    """Private attrs are set to default values"""

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)
    assert w.name == name
    assert w.xpath == xpath
    assert w.parent is parent
    assert w.source is None
    assert w._reload_context is noop_context


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_init_arg_reloadcontext(webgroup, val):
    """Value passed via reloadcontext arg is saved"""

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent, reloadcontext=val)
    assert w._reload_context == val


# ============================================================================
# Test __bool__
# ============================================================================


@pytest.mark.parametrize('val', [True, False, None, 42])
def test_bool_evaluate_existing_element(webgroup, val):
    """Returns whether element exists"""

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class browser:
            @staticmethod
            def element(xpath):
                return val

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)
    assert w.__bool__() == bool(val)


def test_bool_error_is_false(webgroup):
    """Returns False if an error occurred trying to retrieve the element"""

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class browser:
            @staticmethod
            def element(xpath):
                raise RuntimeError

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)
    assert w.__bool__() is False


# ============================================================================
# Test reload
# ============================================================================


@pytest.mark.parametrize('val', [[], [1, 2], list(range(10))])
def test_reload_must_find_one_element(webgroup, val):
    """Raise AssertionError if absxpath returns value < 1 or > 1"""

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class parser:
            @staticmethod
            def xpath(p):
                return val

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    expected = (f'Expected single element, got {len(val)}', )
    w = WebObject(name, xpath, parent)
    with pytest.raises(AssertionError) as err:
        w.reload()

    assert err.value.args == expected


def test_reload_runs_context(monkeypatch, webgroup):
    """Runs reload under context given via reloadcontext init arg"""

    def fake_tostring(n):
        return b'42'

    monkeypatch.setattr(web.html, 'tostring', fake_tostring)

    called = []

    @contextmanager
    def rcontext():
        called.append('enter rcontext')
        yield
        called.append('exit rcontext')

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class parser:
            @staticmethod
            def xpath(p):
                called.append('called xpath')
                return ['42']

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent, reloadcontext=rcontext)
    w.reload()

    # Check that action is done under the given context
    assert called == ['enter rcontext', 'called xpath', 'exit rcontext']


# ============================================================================
# Test absxpath
# ============================================================================


def test_absxpath_parent_is_page(webgroup):
    """Return absxpath where parent is the page"""

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)

    assert w.absxpath == '/html/hello'


def test_absxpath_multi_ancestors(webgroup):
    """Return absxpath where there are multiple ancestors"""

    @webgroup.register
    class TestAncestor0:
        xpath = '/html'
        parent = None

    @webgroup.register
    class TestAncestor1:
        xpath = '/one'
        parent = TestAncestor0()

    @webgroup.register
    class TestParent:
        xpath = '/two'
        parent = TestAncestor1()

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)

    assert w.absxpath == '/html/one/two/hello'


# ============================================================================
# Test visible
# ============================================================================


def test_visible_finds_element(webgroup):
    """Finds the selenium element"""
    called = []

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class browser:
            @staticmethod
            def element(xpath):
                called.append('called element')

                class Test:
                    def is_displayed(self):
                        pass

                return Test()


    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)
    w.visible
    assert called == ['called element']


def test_visible_calls_selenium_is_displayed(webgroup):
    """Finds the selenium element"""
    called = []

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class browser:
            @staticmethod
            def element(xpath):

                class Test:
                    def is_displayed(self):
                        called.append('called is_displayed')

                return Test()


    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)
    w.visible
    assert called == ['called is_displayed']


# ============================================================================
# Test parent
# ============================================================================


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_parent_set_badvalue(webgroup, val):
    """Raise error if trying to set non-CompositePageObject object"""
    expected = ('parent arg expected CompositePageObject object, '
                f'got {type(val).__name__} object instead', )

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = WebObject(name, xpath, parent)

    with pytest.raises(TypeError) as err:
        w.parent = val

    assert err.value.args == expected


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_parent_set_goodvalue(webgroup, val):
    """Raise error if trying to set non-CompositePageObject object"""
    expected = ('parent arg expected CompositePageObject object, '
                f'got {type(val).__name__} object instead', )

    @webgroup.register
    class TestParent0:
        parent = None
        xpath = '/hello'

    @webgroup.register
    class TestParent1:
        parent = None
        xpath = '/world'

    name = 'name'
    xpath = '/hello'
    parent = TestParent0()

    w = WebObject(name, xpath, parent)
    w.parent = TestParent1()
    assert w.absxpath == '/world/hello'


# ============================================================================
#
# ============================================================================
