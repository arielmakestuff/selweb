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

# Local imports


# ============================================================================
# Global fixtures
# ============================================================================


@pytest.fixture(scope='session')
def bindir():
    return Path(pytest.config.rootdir) / 'var' / 'bin'


# ============================================================================
#
# ============================================================================
