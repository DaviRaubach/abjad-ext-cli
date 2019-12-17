from io import StringIO

import pytest
import uqbar.io

import abjadext.cli


def test_list(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageBuildTargetScript()
    command = ["--new", "big-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        pytest.helpers.run_script(script, command)
    command = ["--new", "medium-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        pytest.helpers.run_script(script, command)
    command = ["--new", "small-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        pytest.helpers.run_script(script, command)
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available build targets:
            big-version
            medium-version
            small-version
        """,
    )
