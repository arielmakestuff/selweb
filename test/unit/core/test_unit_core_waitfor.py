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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import POLL_FREQUENCY

# Local imports
from selweb import core


# ============================================================================
# Test __init__
# ============================================================================


def test_init_noparent():
    """Parent is set to None"""
    w = core.WaitFor()
    assert w._parent is None


def test_init_parent():
    """Parent is set to value of parent arg"""
    w = core.WaitFor(parent=42)
    assert w._parent == 42


# ============================================================================
# Test __get__
# ============================================================================


def test_get_new_instance():
    """Data descriptor creates new instances"""

    class Fake:
        test = core.WaitFor()

    f = Fake()

    # Check parent
    assert Fake.test._parent is None
    assert f.test._parent is f

    # New instance is created
    assert isinstance(f.test, core.WaitFor)
    assert f.test is not Fake.test


# ============================================================================
# Test __call__
# ============================================================================


class FakeWebDriverWait:

    def __init__(self, driver, timeout, poll_frequency=POLL_FREQUENCY,
                 ignored_exceptions=None):
        self.call_args = dict(
            driver=driver,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    def until(self, method, message=''):
        ret = self.__class__(**self.call_args)
        ret.until_args = dict(method=method, message=message)
        return ret


def test_call_default_vals(monkeypatch):
    """Default values passed to __call__"""
    monkeypatch.setattr(core, 'WebDriverWait', FakeWebDriverWait)

    class Parent:
        selenium_driver = 42

    def noop(*args):
        return ('noop_42', args)

    w = core.WaitFor(parent=Parent)
    ret = w.__call__(noop)

    # Was fake class until method called?
    assert isinstance(ret, FakeWebDriverWait)
    until_args = ret.until_args
    assert len(until_args) == 2
    assert until_args['message'] == ''
    assert until_args['method'] == ('noop_42', ())

    # Default WaitFor.__call__ args
    assert ret.call_args == dict(
        driver=42,
        timeout=1,
        poll_frequency=POLL_FREQUENCY,
        ignored_exceptions=None
    )


@pytest.mark.parametrize('timeout', [1, 2, 42, 200, 1000])
def test_call_xpath(monkeypatch, timeout):
    """Condition func is called with xpath locator if xpath is not None"""
    monkeypatch.setattr(core, 'WebDriverWait', FakeWebDriverWait)

    class Parent:
        selenium_driver = 42

    def noop(*args):
        return ('noop_42', list(args))

    w = core.WaitFor(parent=Parent)
    ret = w.__call__(noop, xpath='/answer/42', timeout=timeout)

    # Check xpath locator passed to condition func
    assert ret.until_args['method'] == ('noop_42', [(By.XPATH, '/answer/42')])


@pytest.mark.parametrize('timeout', [1, 2, 42, 200, 1000])
def test_call_timeout(monkeypatch, timeout):
    """timeout value is passed to WebDriverWait"""
    monkeypatch.setattr(core, 'WebDriverWait', FakeWebDriverWait)

    class Parent:
        selenium_driver = 42

    def noop(*args):
        return ('noop_42', list(args))

    w = core.WaitFor(parent=Parent)
    ret = w.__call__(noop, timeout=timeout)

    # Check xpath locator passed to condition func
    assert ret.call_args['timeout'] == timeout


# ============================================================================
# Test wrapper methods
# ============================================================================


class FakeWaitFor(core.WaitFor):

    def __call__(self, condfunc, *, xpath=None, timeout=1):
        self.call_args = dict(
            condition_func=condfunc,
            xpath=xpath,
            timeout=timeout
        )


@pytest.fixture
def common_call_args():
    return dict(xpath=None, timeout=42)


def test_alert_method(common_call_args):
    """Uses condfunc alert_is_present"""
    w = FakeWaitFor()
    w.alert(timeout=42)
    result = dict(condition_func=ec.alert_is_present)
    result.update(common_call_args)
    assert w.call_args == result


def test_element_method(common_call_args):
    """Uses condfunc presence_of_element_located"""
    w = FakeWaitFor()
    w.element('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.presence_of_element_located,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_allelements_method(common_call_args):
    """Uses condfunc presence_of_all_elements_located"""
    w = FakeWaitFor()
    w.allelements('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.presence_of_all_elements_located,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_element_text_method(monkeypatch, common_call_args):
    """Uses condfunc text_to_be_present_in_element"""

    def noop(locator, text):
        return ('noop', locator, text)

    monkeypatch.setattr(ec, 'text_to_be_present_in_element', noop)

    w = FakeWaitFor()
    w.element_text('/xpath/42', 'forty-two', timeout=42)
    assert w.call_args['condition_func']() == ('noop', (By.XPATH, '/xpath/42'),
                                               'forty-two')


def test_element_value_method(monkeypatch, common_call_args):
    """Uses condfunc text_to_be_present_in_element_value"""

    def noop(locator, text):
        return ('noop', locator, text)

    monkeypatch.setattr(ec, 'text_to_be_present_in_element_value', noop)

    w = FakeWaitFor()
    w.element_value('/xpath/42', 'forty-two', timeout=42)
    assert w.call_args['condition_func']() == ('noop', (By.XPATH, '/xpath/42'),
                                               'forty-two')


def test_element_clickable(common_call_args):
    """Uses condfunc element_to_be_clickable"""
    w = FakeWaitFor()
    w.element_clickable('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.element_to_be_clickable,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_element_invisible(common_call_args):
    """Uses condfunc invisibility_of_element_located"""
    w = FakeWaitFor()
    w.element_invisible('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.invisibility_of_element_located,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_element_visible(common_call_args):
    """Uses condfunc visibility_of_element_located"""
    w = FakeWaitFor()
    w.element_visible('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.visibility_of_element_located,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_allelements_visible(common_call_args):
    """Uses condfunc visibility_of_any_elements_located"""
    w = FakeWaitFor()
    w.allelements_visible('/xpath/42', timeout=42)
    result = common_call_args
    result.update(condition_func=ec.visibility_of_any_elements_located,
                  xpath='/xpath/42')
    assert w.call_args == result


def test_stale_element_method(monkeypatch, common_call_args):
    """Uses condfunc staleness_of"""

    def noop(element):
        return ('noop', element)

    monkeypatch.setattr(ec, 'staleness_of', noop)

    w = FakeWaitFor()
    w.stale_element('42', timeout=42)
    assert w.call_args['condition_func']() == ('noop', '42')


def test_isvisible_method(monkeypatch):
    """Uses cond func visibility_of"""

    def noop(element):
        return ('noop', element)

    monkeypatch.setattr(ec, 'visibility_of', noop)

    w = FakeWaitFor()
    w.isvisible('42', timeout=42)
    assert w.call_args['condition_func']() == ('noop', '42')


def test_title_method(monkeypatch):
    """Uses cond func title_is"""

    def noop(text):
        return ('noop', text)

    monkeypatch.setattr(ec, 'title_is', noop)

    w = FakeWaitFor()
    w.title('forty-two', timeout=42)
    assert w.call_args['condition_func']() == ('noop', 'forty-two')


def test_title_substring_method(monkeypatch):
    """Uses cond func title_contains"""

    def noop(text):
        return ('noop', text)

    monkeypatch.setattr(ec, 'title_contains', noop)

    w = FakeWaitFor()
    w.title_substring('forty-two', timeout=42)
    assert w.call_args['condition_func']() == ('noop', 'forty-two')


def test_pageload():
    """Calls element"""

    class FakeWaitFor(core.WaitFor):

        def element(self, xpath):
            self.element_args = (xpath, )
            return 42

        def stale_element(self, element, *, timeout=1):
            self.stale_args = (element, timeout)

    w = FakeWaitFor()
    with w.pageload(timeout=4.2):
        assert w.element_args == ('/html', )
        assert not hasattr(w, 'stale_args')

    assert w.stale_args == (42, 4.2)


# ============================================================================
#
# ============================================================================
