"""
strec contains a simple test-framework to verify config-files and their expected
replacements.

This module contains unit-tests for that component.
"""
import strec.testing as tst


def test_discovery() -> None:
    """
    Testing that we can discover tests from a given folder.
    """
    discovered_tests = tst.discover("tests/configs")
    assert all([isinstance(item, tst.Test) for item in discovered_tests])


def test_test_names() -> None:
    """
    Ensure that all test have a representative and helpful name
    """
    discovered_tests = tst.discover("tests/configs")
    expected_names = {"test.one", "test.two", "test.failing"}
    discovered_names = {item.name for item in discovered_tests}
    assert discovered_names == expected_names


def test_config_names() -> None:
    """
    Ensure that all test contain the name of the config that we are testing
    """
    discovered_tests = tst.discover("tests/configs")
    expected_configs = {"conf.simple"}
    discovered_configs = {item.config_name for item in discovered_tests}
    assert expected_configs == discovered_configs


def test_passing_runs() -> None:
    """
    Ensure that the "passing" tests can be run and return a proper result
    """
    discovered_tests = tst.discover("tests/configs")
    for test in discovered_tests:
        result = test.run()
        if "failing" in test.name:
            continue
        assert result == tst.Result(tst.State.PASS, "")


def test_failing_runs() -> None:
    """
    Ensure that the "failing" tests can be run and return a useful diff
    """
    discovered_tests = tst.discover("tests/configs")
    for test in discovered_tests:
        result = test.run()
        if "failing" not in test.name:
            continue
        diff = (
            "- the <blue>quick<reset> brown <red>fox<reset> jumps over the lazy dog\n"
            "?     ------     -------       -----   -------\n\n"
            "+ the quick brown fox jumps over the lazy dog"
        )
        assert result == tst.Result(tst.State.FAIL, diff)
