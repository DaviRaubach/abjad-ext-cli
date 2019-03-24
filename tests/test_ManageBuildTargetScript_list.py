from io import StringIO

import pytest

import abjadext.cli
import uqbar.io


def test_list(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageBuildTargetScript()
    command = ["--new", "big-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        try:
            script(command)
        except SystemExit as exception:
            if exception.code:
                raise RuntimeError("SystemExit")
    command = ["--new", "medium-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        try:
            script(command)
        except SystemExit as exception:
            if exception.code:
                raise RuntimeError("SystemExit")
    command = ["--new", "small-version"]
    with uqbar.io.DirectoryChange(paths.score_path):
        try:
            script(command)
        except SystemExit as exception:
            if exception.code:
                raise RuntimeError("SystemExit")
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            try:
                script(command)
            except SystemExit as exception:
                if exception.code:
                    raise RuntimeError("SystemExit")
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available build targets:
            big-version
            medium-version
            small-version
        """,
    )
