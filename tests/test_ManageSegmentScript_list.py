import os
from io import StringIO

import pytest
import uqbar.io

import abjadext.cli


def test_list_segments(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "segment_one")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_two")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_three")
    script = abjadext.cli.ManageSegmentScript()
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=2)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available segments:
            Reading test_score/segments/metadata.json ... OK!
            segment_one   [1]
            segment_two   [2]
            segment_three [3]
        """.replace(
            "/", os.path.sep
        ),
    )


def test_list_segments_no_segments(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageSegmentScript()
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=2)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available segments:
            Reading test_score/segments/metadata.json ... JSON does not exist.
            No segments available.
        """.replace(
            "/", os.path.sep
        ),
    )


def test_list_segments_unstaged(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "segment_one")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_two")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_three")
    script = abjadext.cli.ManageSegmentScript()
    segment_names = script._read_segments_list_json(paths.score_path, verbose=False)
    segment_names.remove("segment_two")
    script._write_segments_list_json(
        segment_names, score_path=paths.score_path, verbose=False
    )
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=2)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available segments:
            Reading test_score/segments/metadata.json ... OK!
            segment_one   [1]
            segment_three [2]
            segment_two
        """.replace(
            "/", os.path.sep
        ),
    )
