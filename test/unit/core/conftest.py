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
from selweb.core import CompositePageObject, Page, PageObject


# ============================================================================
# PageObject fixture
# ============================================================================


@pytest.fixture
def pageobject_mixin():
    """Return mixin with concrete implementations of PageObject methods"""

    class Mixin:

        def __bool__(self):
            return super().__bool__()

        def reload(self):
            return super().reload()

        @property
        def name(self):
            return super().name

        @property
        def source(self):
            return super().source

        @property
        def xpath(self):
            return super().xpath

        @property
        def absxpath(self):
            """Calculate and return the absolute xpath to the page object"""
            return super().absxpath

        @property
        def browser(self):
            """Return the browser"""
            return super().browser

        @property
        def visible(self):
            """Return True if the page object is visible"""
            return super().visible

        @property
        def page(self):
            """Return the object's page"""
            return super().page

        @property
        def parent(self):
            """Return the parent page object"""
            return super().parent

        @parent.setter
        def parent(self, parent):
            """Set the parent page object"""
            # Normally this should be super().parent = parent, however due to bug
            # http://bugs.python.org/issue14965, the below workaround is needed
            PageObject.parent.fset(self, parent)

    return Mixin


@pytest.fixture
def pageobject_class(pageobject_mixin):
    """Create concrete implementation of PageObject"""

    class Test(pageobject_mixin, PageObject):
        pass

    return Test


# ============================================================================
# CompositePageObject fixture
# ============================================================================


@pytest.fixture
def compositepageobject_mixin(pageobject_mixin):
    """Return mixin with concrete implementations of CompositePageObject methods"""

    class Mixin(pageobject_mixin):

        def __getitem__(self, name):
            """Retrieve a child page object by name"""
            return super().__getitem__(name)

        def __delitem__(self, name):
            """Remove a child page object by name"""
            super().__delitem__(name)

        def __iter__(self):
            """Iterate over names of child page objects"""
            return super().__iter__()

        def __len__(self):
            """Return the number of child page objects"""
            return super().__len__()

        def add(self, obj):
            """Add a new child page object"""
            super().add(obj)

        def clear(self):
            """Remove all child page objects"""
            super().clear()

        def children(self):
            """Iterator over child page objects"""
            return super().children()

    return Mixin


@pytest.fixture
def compositepageobject_class(compositepageobject_mixin):
    """Create concrete implementation of CompositePageObject"""

    class Test(compositepageobject_mixin, CompositePageObject):
        pass

    return Test


# ============================================================================
# Page fixtures
# ============================================================================


@pytest.fixture
def page_mixin(compositepageobject_mixin):
    """Return mixin with concrete implementations of Page methods"""

    class Mixin(compositepageobject_mixin):

        def go(self):
            """Retrieve the page"""
            return super().go()

        @property
        def url(self):
            """Return the current page's location"""
            return super().url

        @property
        def parser(self):
            """Return an lxml parser"""
            return super().parser

    return Mixin


@pytest.fixture
def page_class(page_mixin):
    """Create concrete implementation of Page"""

    class Test(page_mixin, Page):
        pass

    return Test


# ============================================================================
#
# ============================================================================
