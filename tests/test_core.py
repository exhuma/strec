from io import StringIO
from unittest.mock import Mock, patch

import pytest

import strec.core as core


def test_process_lines():
    source = StringIO("hello-world")
    colorizer = Mock()
    core.process_lines(source, colorizer)
    colorizer.feed.assert_called_with("hello-world")


def test_create_stdin():
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("ls")
    assert source == sys.stdin


def test_create_stdin_noconfig():
    """
    When reading from stdin, we don't know the command and must require a
    config
    """
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("")
    sys.exit.assert_called_with(9)
