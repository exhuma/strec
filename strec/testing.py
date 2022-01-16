"""
This module contains the implementation for running tests of config-files
"""
import sys
import textwrap
from dataclasses import dataclass
from difflib import ndiff
from enum import Enum, auto
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, Optional

from strec.colorizers.base import Colorizer
from tests.conftest import Colors


class State(Enum):
    """
    The result state of a test
    """

    PASS = auto()
    FAIL = auto()


@dataclass
class Result:
    """
    The end-result of a test-case
    """

    state: State
    """
    Either "PASS" or "FAIL"
    """
    diff: str
    """
    An empty string if all went well. If a test failed, this contains a
    human-readable text showing the difference between the actual result and
    expected result.
    """


class Test:
    """
    The core implementation of a test-execution for config-files

    :param config_path: The root folder containing configuration files
    :param stream_input: The sample input used for testing
    :param expected_output: The result that we want to see
    """

    def __init__(
        self, config_path: Path, stream_input: Path, expected_output: Path
    ) -> None:
        self.config_path = config_path
        self.stream_input = stream_input
        self.expected_output = expected_output
        self.name = stream_input.name
        self.config_name = stream_input.parent.name

    def run(self) -> Result:
        """
        Execute ``strec`` against the sample test-input and compoare against the
        expected result.
        """
        config = self.config_path / self.config_name
        output = StringIO()
        colorizer = Colorizer.from_config_filename(
            str(config.absolute()), output, Colors
        )
        for line in self.stream_input.open():
            colorizer.feed(line)

        result = output.getvalue()
        expected_content = self.expected_output.read_text()
        if result == expected_content:
            return Result(State.PASS, "")
        diff = ndiff(
            result.splitlines(),
            expected_content.splitlines(),
        )
        return Result(State.FAIL, "\n".join(diff))


def discover(config_path: str) -> Iterable[Test]:
    """
    Search *config_path* for test-files and return test-objects for those that
    match.
    """
    path = Path(config_path)
    expected_filenames: Dict[Path, Optional[Path]] = {}
    for filename in sorted(path.glob("**/test.*")):
        if not filename.name.endswith(".expected"):
            expected_filenames[filename] = None
        else:
            expected_filenames[
                filename.parent / filename.name.rpartition(".")[0]
            ] = filename

    for stream_input, expected in expected_filenames.items():
        if expected is None:
            print(
                f"WARNING: No '.expected' file found for {stream_input}",
                file=sys.stderr,
            )
            continue
        yield Test(path, stream_input, expected)


def run(config_path: str) -> None:
    """
    Run all the tests discovered in *config_path*
    """
    for test in discover(config_path):
        result = test.run()
        print(f"{test.stream_input}\t{result.state.name}")
        if result.state == State.FAIL:
            print(textwrap.indent(result.diff, " │   "))
