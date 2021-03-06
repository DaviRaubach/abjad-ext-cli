import os
import platform
from io import StringIO

import pytest
import uqbar.io

import abjadext.cli


def test_exists(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "test_segment")
    with uqbar.io.RedirectedStreams(stdout=string_io):
        pytest.helpers.create_segment(
            paths.test_directory_path, "test_segment", expect_error=True
        )
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating segment subpackage 'test_segment' ...
            Path exists: test_score/segments/test_segment
        """.replace(
            "/", os.path.sep
        ),
    )


def test_force_replace(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "test_segment")
    with uqbar.io.RedirectedStreams(stdout=string_io):
        pytest.helpers.create_segment(
            paths.test_directory_path, "test_segment", force=True
        )
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating segment subpackage 'test_segment' ...
            Reading test_score/metadata.json ... OK!
            Reading test_score/segments/metadata.json ... OK!
            Created test_score/segments/test_segment/
        """.replace(
            "/", os.path.sep
        ),
    )


def test_internal_path(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageSegmentScript()
    command = ["--new", "test_segment"]
    internal_path = paths.score_path.joinpath("test_score", "builds")
    assert internal_path.exists()
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(str(internal_path)):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating segment subpackage 'test_segment' ...
            Reading test_score/metadata.json ... OK!
            Reading test_score/segments/metadata.json ... JSON does not exist.
            Writing test_score/segments/metadata.json
            Created test_score/segments/test_segment/
        """.replace(
            "/", os.path.sep
        ),
    )


def test_success(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageSegmentScript()
    try:
        names = script._read_segments_list_json(paths.score_path, verbose=False)
        assert names == []
    except SystemExit as exception:
        if exception.code:
            raise RuntimeError("SystemExit")
    command = ["--new", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating segment subpackage 'test_segment' ...
            Reading test_score/metadata.json ... OK!
            Reading test_score/segments/metadata.json ... JSON does not exist.
            Writing test_score/segments/metadata.json
            Created test_score/segments/test_segment/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert paths.segments_path.joinpath("test_segment").exists()
    expected_files = [
        "test_score/test_score/segments/.gitignore",
        "test_score/test_score/segments/__init__.py",
        "test_score/test_score/segments/metadata.json",
        "test_score/test_score/segments/test_segment/__init__.py",
        "test_score/test_score/segments/test_segment/definition.py",
    ]
    if platform.system().lower() == "windows":
        expected_files = [_.replace("/", os.path.sep) for _ in expected_files]
    pytest.helpers.compare_path_contents(
        paths.segments_path, expected_files, paths.test_directory_path
    )
    try:
        names = script._read_segments_list_json(paths.score_path, verbose=False)
        assert names == ["test_segment"]
    except SystemExit as exception:
        if exception.code:
            raise RuntimeError("SystemExit")
