from io import StringIO

import abjadext.cli
import pytest
import uqbar.io


def test_list_materials(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "foo")
    pytest.helpers.create_material(paths.test_directory_path, "bar")
    pytest.helpers.create_material(paths.test_directory_path, "baz")
    pytest.helpers.create_material(paths.test_directory_path, "quux")
    script = abjadext.cli.ManageMaterialScript()
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=2)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available materials:
            Markup:
                bar [Markup]
                baz [Markup]
                foo [Markup]
                quux [Markup]
        """,
    )


def test_list_materials_no_materials(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageMaterialScript()
    command = ["--list"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=2)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Available materials:
            No materials available.
        """,
    )
