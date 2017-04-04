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

# Local imports
from selweb.core import CompositePageObject, PageObject
from selweb.util import noop_context
import selweb.web as web
from selweb.web import CompositeWebObject


# ============================================================================
# Test types
# ============================================================================


@pytest.mark.parametrize('cls', [PageObject, CompositePageObject])
def test_types(webgroup, cls):
    """Is an instance of PageObject and CompositePageObject"""

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = CompositeWebObject(name, xpath, parent)
    isinstance(w, cls)


# ============================================================================
# Test __init__
# ============================================================================


def test_init_initializes_webobject(webgroup):
    """Initializes as a webobject"""

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = CompositeWebObject(name, xpath, parent)

    # Check initialized via WebObject
    assert w.name == name
    assert w.xpath == xpath
    assert w.parent is parent
    assert w.source is None
    assert w._reload_context is noop_context

    # Check objmap attr
    assert isinstance(w._objmap, OrderedDict)
    assert not w._objmap


def test_init_factory_func(webgroup):
    """Initializes internal objmap via factory arg"""

    def testfunc():
        return 42

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = CompositeWebObject(name, xpath, parent, factory=testfunc)
    assert w._objmap == 42


# ============================================================================
# Test unnested_reload_context
# ============================================================================


def test_unnested_reload_context(webgroup):
    """Run _reload_context once"""
    called = []

    @contextmanager
    def rcontext():
        called.append('enter rcontext')
        yield
        called.append('exit rcontext')

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = CompositeWebObject(name, xpath, parent, reloadcontext=rcontext)
    with w.unnested_reload_context():
        with w._reload_context():
            pass

    # Check rcontext only entered once and exited once
    assert called == ['enter rcontext', 'exit rcontext']


# ============================================================================
# Test mapping methods
# ============================================================================


def test_map_methods(webgroup):
    """Map methods behave as expected"""

    def func():
        return dict(answer=42)

    @webgroup.register
    class Fake:
        name = 'fake'

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = CompositeWebObject(name, xpath, parent, factory=func)
    assert len(w) == 1
    assert list(w) == ['answer']
    assert w['answer'] == 42
    assert list(w.children()) == [42]
    del w['answer']
    assert len(w) == 0

    f = Fake()
    w.add(f)
    assert len(w) == 1
    assert list(w.children()) == [f]
    assert w['fake'] == f

    w.clear()
    assert len(w) == 0


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_add_arg_obj_badtype(webgroup, val):
    """Raise error if obj arg given non-PageObject value"""

    @webgroup.register
    class TestParent:
        pass

    name = 'name'
    xpath = '/hello'
    parent = TestParent()
    expected = ('obj arg expected PageObject object, '
                f'got {type(val).__name__} object instead', )

    w = CompositeWebObject(name, xpath, parent)
    with pytest.raises(TypeError) as err:
        w.add(val)


# ============================================================================
# Test reload
# ============================================================================


def test_reload_uses_unnested_reload_context(monkeypatch, webgroup):
    """Reloads under context"""

    def fake_tostring(n):
        return b'42'

    monkeypatch.setattr(web.html, 'tostring', fake_tostring)

    called = []

    class TestComposite(CompositeWebObject):

        @contextmanager
        def unnested_reload_context(self):
            called.append('enter context')
            yield
            called.append('exit context')

    @webgroup.register
    class TestParent:
        xpath = '/html'
        parent = None

        class parser:
            @staticmethod
            def xpath(p):
                called.append('called xpath')
                return ['42']

    @webgroup.register
    class Fake:
        name = 'fake'

    name = 'name'
    xpath = '/hello'
    parent = TestParent()

    w = TestComposite(name, xpath, parent)
    w.add(Fake())

    w.reload()

    # Clear was called
    assert len(w) == 0

    # Reload happened under context
    assert called == ['enter context', 'called xpath', 'exit context']


# ============================================================================
#
# ============================================================================
