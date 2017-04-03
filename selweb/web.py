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
from abc import abstractmethod
from collections import OrderedDict
from contextlib import contextmanager

# Third-party imports
from lxml import html
from yarl import URL

# Local imports
from .core import Browser, CompositePageObject, Page, PageObject
from .util import noop_context


# ============================================================================
# WebObject
# ============================================================================


@PageObject.register
class WebObject:
    """Describes a set of web elements"""
    __slots__ = ('_name', '_xpath', '_parent', '_source', '_reload_context')

    def __init__(self, name, xpath, parent, *, reloadcontext=None):
        errmsg = None
        if not isinstance(xpath, str):
            errmsg = ('{} arg expected {} object, got {} object instead'.
                      format('xpath', str.__name__, type(xpath).__name__))
        elif not xpath.startswith('/'):
            raise ValueError('Given xpath missing leading /')
        elif not isinstance(parent, CompositePageObject):
            errmsg = ('{} arg expected {} object, got {} object instead'.
                      format('parent', CompositePageObject.__name__,
                             type(parent).__name__))
        if errmsg:
            raise TypeError(errmsg)

        self._name = name
        self._xpath = xpath
        self._parent = parent
        self._source = None

        self._reload_context = (noop_context if reloadcontext is None
                                else reloadcontext)

    # --------------------
    # General methods
    # --------------------

    def __bool__(self):
        """Return whether the page object is valid"""
        try:
            return bool(self.browser.element(self.absxpath))
        except:
            return False

    def reload(self):
        """Reload the page object"""
        with self._reload_context():
            parser = self.page.parser
            nodelist = parser.xpath(self.absxpath)
            assert len(nodelist) == 1, ('Expected single element, got {}'.
                                        format(len(nodelist)))
            node = nodelist[0]
            self._source = html.tostring(node).decode('utf-8')

    @property
    def name(self):
        """Retrieve object's name

        This is used as a key on the object's parent

        """
        return self._name

    @property
    def source(self):
        """Retrieve object's source"""
        return self._source

    @property
    def absxpath(self):
        """Calculate and return the xpath to the page object"""
        xpath = []
        cur = self
        while True:
            xpath.append(cur.xpath)
            parent = cur.parent
            if parent is None:
                xpath.reverse()
                return ''.join(xpath)
            cur = parent

    @property
    def xpath(self):
        """Calculate and return the xpath to the page object"""
        return self._xpath

    @property
    def browser(self):
        """Return the browser"""
        return self.page.browser

    @property
    def visible(self):
        """Return True if the page object is visible"""
        return self.browser.element(self.absxpath).is_displayed()

    @property
    @abstractmethod
    def page(self):
        """Return the object's page"""
        cur = self
        while True:
            parent = cur.parent
            if parent is None:
                return cur
            cur = parent

    @property
    def parent(self):
        """Return the parent page object"""
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Set the parent page object"""
        if not isinstance(parent, CompositePageObject):
            errmsg = ('parent arg expected {} object, got {} object instead'.
                      format(CompositePageObject.__name__,
                             type(parent).__name__))
            raise TypeError(errmsg)
        self._parent = parent


# ============================================================================
# CompositeWebObject
# ============================================================================


@CompositePageObject.register
class CompositeWebObject(WebObject):

    __slots__ = ('_objmap', )

    def __init__(self, name, xpath, parent, *, factory=None, reloadcontext=None):
        super().__init__(name, xpath, parent, reloadcontext=reloadcontext)
        self._objmap = OrderedDict() if factory is None else factory()

    @contextmanager
    def unnested_reload_context(self):
        """Ensure no nested reload contexts are run"""
        context = self._reload_context
        with context():
            self._reload_context = noop_context
            try:
                yield
            finally:
                self._reload_context = context

    def __getitem__(self, name):
        """Retrieve a child page object by name"""
        return self._objmap[name]

    def __delitem__(self, name):
        """Remove a chld page object"""
        self._objmap.__delitem__(name)

    def __iter__(self):
        """Iterate over names of child page objects"""
        return iter(self._objmap)

    def __len__(self):
        """Return the number of child page objects"""
        return len(self._objmap)

    def reload(self):
        """Reload the page object"""
        with self.unnested_reload_context():
            super().reload()
            self.clear()

    def add(self, obj):
        """Add a new child page object"""
        if not isinstance(obj, PageObject):
            errmsg = ('obj arg expected {} object, got {} object instead'.
                      format(PageObject.__name__, type(obj).__name__))
            raise TypeError(errmsg)
        self._objmap[obj.name] = obj

    def children(self):
        """Iterator over child page objects"""
        return self._objmap.values()

    def clear(self):
        """Remove all child page objects"""
        self._objmap.clear()


# ============================================================================
# WebPage
# ============================================================================


@Page.register
class WebPage(CompositeWebObject):
    __slots__ = ('_url', '_browser', '_parser')

    def __init__(self, name, url, browser, *, parent=None, factory=None,
                 reloadcontext=None):
        for v, cls in [('url', URL), ('browser', Browser)]:
            val = locals()[v]
            if not isinstance(val, cls):
                errmsg = ('{} arg expected {} object, got {} object instead'.
                          format(v, cls.__name__, type(val).__name__))
                raise TypeError(errmsg)
        xpath = '/html'
        super().__init__(name, xpath, self if parent is None else parent,
                         factory=factory, reloadcontext=reloadcontext)
        if parent is None:
            self._parent = None

        self._url = url
        self._browser = browser
        self._parser = None

    # --------------------
    # Page methods
    # --------------------

    def go(self):
        """Retrieve the page"""
        b = self._browser
        b.go(self._url)
        self.reload()

    @property
    def url(self):
        """Return the current page's location"""
        return self._url

    # --------------------
    # PageObject method'utf-8's
    # --------------------

    def reload(self):
        """Reload the page source"""
        with self._reload_context():
            self._source = s = self.browser.source
            self._parser = html.fromstring(s)
            self.clear()

    @property
    def source(self):
        """Retrieve page source"""
        return self._source

    @property
    def absxpath(self):
        """Calculate and return the xpath to the page object"""
        return self._xpath

    @property
    def browser(self):
        """Return the browser"""
        return self._browser

    @property
    def visible(self):
        """Return True if the page object is visible"""
        return self.browser.selenium_driver.is_displayed()

    @property
    def page(self):
        """Return the object's page"""
        return self

    @property
    def parser(self):
        """Return an lxml html parser"""
        return self._parser


# ============================================================================
#
# ============================================================================
