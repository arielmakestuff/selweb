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
from selweb.util import noop_context, xpath_clsmatch


# ============================================================================
#
# ============================================================================


@pytest.mark.parametrize('val', ['hello', 'world', '42'])
def test_arg_clsname_str(val):
    """Return expected output when given a single string"""
    expected = f"contains(concat(' ', normalize-space(@class), ' '), ' {val} ')"
    assert xpath_clsmatch(val) == expected


@pytest.mark.parametrize('val', [[ 'hello' ], [ 'world' ], [ '42' ]])
def test_arg_clsname_single_element_sequence(val):
    """Return expected output when given a sequence with single string"""
    expected = ("contains(concat(' ', normalize-space(@class), ' '), "
                f"' {val[0]} ')")
    assert xpath_clsmatch(val) == expected


@pytest.mark.parametrize('val', ['hello', 'world', '42'])
def test_arg_clsname_sequence_with_other(val):
    """Raise error if clsname is a sequence and values are passed via other"""
    with pytest.raises(ValueError):
        xpath_clsmatch(['42'], val)


@pytest.mark.parametrize('val', list(range(5)))
def test_arg_clsname_multi_element_sequence(val):
    """Return expected output when given a sequence with multiple strings"""
    frag = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')"
    names = list(range(val))
    expected = ' and '.join([frag.format(v) for v in names])
    assert xpath_clsmatch(names) == expected


@pytest.mark.parametrize('val', [42, 4.2])
def test_arg_clsname_nonstr_nonseq(val):
    """Return expected output when given non-str non-Sequence value"""
    expected = ("contains(concat(' ', normalize-space(@class), ' '), "
                f"' {val} ')")
    assert xpath_clsmatch(val) == expected


@pytest.mark.parametrize('val,other', [(42, 1)])
def test_arg_clsname_other_nonstr_nonseq(val, other):
    """Return expected output when given non-str non-seq values"""
    frag = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')"
    names = list(range(val))
    expected = ' and '.join([frag.format(v) for v in [val, other]])
    assert xpath_clsmatch(val, other) == expected


# ============================================================================
# Test noop_context
# ============================================================================


def test_noop_context_noerrors():
    """noop_context is a noop"""

    with noop_context():
        pass


# ============================================================================
#
# ============================================================================
