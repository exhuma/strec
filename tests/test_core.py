from io import StringIO
from unittest.mock import Mock, patch

import strec.core as core


def test_process_lines() -> None:
    source = StringIO("hello-world")
    colorizer = Mock()
    core.process_lines(source, colorizer)
    colorizer.feed.assert_called_with("hello-world")  # type: ignore


def test_create_stdin() -> None:
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("ls")
    assert source == sys.stdin  # type: ignore


def test_create_stdin_noconfig() -> None:
    """
    When reading from stdin, we don't know the command and must require a
    config
    """
    with patch("strec.core.sys") as sys:
        core.create_stdin("")
    sys.exit.assert_called_with(9)  # type: ignore
