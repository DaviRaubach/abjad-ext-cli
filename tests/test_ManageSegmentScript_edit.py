import os
from io import StringIO

import pytest
import uqbar.io

import abjadext.cli


def test_success(paths, call_subprocess_mock):
    string_io = StringIO()
    call_subprocess_mock.return_value = 0
    pytest.helpers.create_score(paths.test_directory_path)
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    script = abjadext.cli.ManageSegmentScript()
    command = ["--edit", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Edit candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        """.replace(
            "/", os.path.sep
        ),
    )
    definition_path = segment_path.joinpath("definition.py")
    command = "{} {!s}".format(abjadext.cli.get_text_editor(), definition_path)
    call_subprocess_mock.assert_called_with(command)
