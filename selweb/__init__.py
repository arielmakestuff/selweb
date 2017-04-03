# -*- coding: utf-8 -*-
# selweb/__init__.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""selweb package"""

# ============================================================================
# Globals
# ============================================================================


__author__ = 'Ariel De Ocampo'
__email__ = 'arielmakestuff@gmail.com'
__version__ = '0.1.0'


# ============================================================================
# Imports
# ============================================================================


from .core import (Browser, CompositePageObject, HTMLProperty, Page,
                   PageObject)
from .web import CompositeWebObject, WebObject, WebPage


# ============================================================================
#
# ============================================================================
