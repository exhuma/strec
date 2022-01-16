import re
from io import StringIO
from textwrap import dedent

import strec.colorizers.garabik as garabik
from tests.conftest import Colors


def test_color_list():
    input_data = "the quick brown fox jumps over the lazy dog"
    expected = (
        "the <blue>quick<reset> brown <red>fox<reset> jumps over the lazy dog"
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(quick) brown (fox)\b"),
            ["blue", "red"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_color_list2():
    """
    What happens if the beginning of the string does not start with a matching
    group?
    """
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"this is a \b(hello) something (world)\b"),
            ["blue", "red"],
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_more():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(hello)\b"),
            ["blue"],
            count=garabik.Count.MORE,
        ),
        garabik.Rule(
            re.compile(r"\b(world)\b"),
            ["red"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_stop():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something world string"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(hello)\b"),
            ["blue"],
            count=garabik.Count.STOP,
        ),
        garabik.Rule(
            re.compile(r"\b(world)\b"),
            ["red"],
            count=garabik.Count.STOP,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_once():
    input_data = "hello world hello world hello world"
    expected = "hello <blue>world<reset> hello world hello world"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(world)\b"),
            ["blue"],
            count=garabik.Count.ONCE,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_block():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        first line
        <blue>second line<reset>
        <blue>third line
        <reset><reset>fourth line<reset>
        fifth line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(second line)\b"),
            ["blue"],
            count=garabik.Count.BLOCK,
        ),
        garabik.Rule(
            re.compile(r"\b(fourth line)\b"),
            ["default"],
            count=garabik.Count.UNBLOCK,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_skip():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        first line
        second line
        fourth line
        fifth line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(third line)\b"),
            ["blue"],
            count=garabik.Count.BLOCK,
            skip=True,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_replace():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        <yellow>hello<reset> first <blue>world<reset> line
        <yellow>hello<reset> second <blue>world<reset> line
        <yellow>hello<reset> third <blue>world<reset> line
        <yellow>hello<reset> fourth <blue>world<reset> line
        <yellow>hello<reset> fifth <blue>world<reset> line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(\w+) line\b"),
            ["blue"],
            count=garabik.Count.MORE,
            replace=r"hello \1 world line",
        ),
        garabik.Rule(
            re.compile(r"\b(hello)\b"),
            ["yellow"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    print(result)
    assert result == expected


def test_ungrouped_text():
    """
    If a regex contains ungrouped text, this text should be copied unmodified to
    the output.
    """
    line = "the quick brown fox"
    expected = "the quick <blue>brown<reset> fox"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"quick (\w+) fox"),
            ["blue"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_parse_config_multiple():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = dedent(
        r"""# Regular Up
        regexp=\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)
        colours=green,bold green, bold green
        -
        # users
        regexp=\b(\d+) users?
        colours=yellow,bold yellow
        -
        # load average
        regexp=load average: (\d+[\.,]\d+),\s(\d+[\.,]\d+),\s(\d+[\.,]\d+)
        colours=default,bright_cyan,cyan,dark cyan
        -
        # W Command section
        # Title
        regexp=^USER.*$
        colours=bold
        skip=false
        count=more
        """
    )
    rules = list(garabik.parse_config(config_content))
    expected = [
        garabik.Rule(
            re.compile(r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)"),
            ["green", "bold green", "bold green"],
        ),
        garabik.Rule(
            re.compile(r"\b(\d+) users?"),
            ["yellow", "bold yellow"],
        ),
        garabik.Rule(
            re.compile(
                r"load average: (\d+[\.,]\d+),\s(\d+[\.,]\d+),\s(\d+[\.,]\d+)"
            ),
            ["default", "bright_cyan", "cyan", "dark cyan"],
        ),
        garabik.Rule(re.compile(r"^USER.*$"), ["bold"]),
    ]
    assert rules == expected


def test_parse_config_single():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = dedent(
        r"""# Regular Up
        regexp=\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)
        colours=green,bold green, bold green
        """
    )
    rules = list(garabik.parse_config(config_content))
    expected = [
        garabik.Rule(
            re.compile(r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)"),
            ["green", "bold green", "bold green"],
        ),
    ]
    assert rules == expected


def test_parse_config_empty():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = ""
    rules = list(garabik.parse_config(config_content))
    expected = []
    assert rules == expected


def test_unmatched_regex_group():
    """
    If a rule regex has a capturing group, but that group does not match on a
    given line, the output should not be moodified for that group.
    """
    line = "-rw-rw-r-- 1 streamer streamer  344 Nov  7 17:52 CHANGELOG.rst\n"
    rule = garabik.Rule(
        regex=re.compile(
            "([A-Z][a-z]{2})\\s([ 1-3]\\d)\\s(?:([0-2]?\\d):([0-5]\\d)(?=[\\s,]|$)|\\s*(\\d{4}))"
        ),
        colors=["cyan", "cyan", "cyan", "cyan", "bold magenta"],
        count=garabik.Count.MORE,
        skip=False,
        replace="",
    )
    expected = (
        "-rw-rw-r-- 1 streamer streamer  344 <cyan>Nov<reset> <cyan> 7<reset> "
        "<cyan>17<reset>:<cyan>52<reset> CHANGELOG.rst\n"
    )
    output = StringIO()
    rules = [rule]
    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(line)
    assert output.getvalue() == expected


def test_lookbehind():
    """
    If an earlier rule adds color-codes, lookbehinds should not break

    This is a behaviour of the old "grc" and should not be broken if we want to
    keep the config compatible.
    """
    line = "the quick brown fox jumps over the lazy dog"
    rules = garabik.parse_config(
        dedent(
            r"""
            regexp=brown (fox)
            colours=blue
            ---
            regexp=(?<=fox)\s(jumps)
            colours=cyan
            """
        )
    )
    output = StringIO()
    parser = garabik.GarabikColorizer(rules, output, Colors)
    parser.feed(line)
    result = output.getvalue()
    expected = (
        "the quick brown <blue>fox<reset> <cyan>jumps<reset> over the lazy dog"
    )
    assert result == expected
