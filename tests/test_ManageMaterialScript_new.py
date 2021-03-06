import os
import platform
from io import StringIO

import pytest
import uqbar.io

import abjadext.cli


def test_exists(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "test_material")
    with uqbar.io.RedirectedStreams(stdout=string_io):
        pytest.helpers.create_material(
            paths.test_directory_path, "test_material", expect_error=True
        )
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating material subpackage 'test_material' ...
            Path exists: test_score/materials/test_material
        """.replace(
            "/", os.path.sep
        ),
    )


def test_force_replace(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "test_material")
    with uqbar.io.RedirectedStreams(stdout=string_io):
        pytest.helpers.create_material(
            paths.test_directory_path, "test_material", force=True
        )
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating material subpackage 'test_material' ...
            Reading test_score/metadata.json ... OK!
            Created test_score/materials/test_material/
        """.replace(
            "/", os.path.sep
        ),
    )


def test_internal_path(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageMaterialScript()
    command = ["--new", "test_material"]
    internal_path = paths.score_path.joinpath("test_score", "builds")
    assert internal_path.exists()
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(internal_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating material subpackage 'test_material' ...
            Reading test_score/metadata.json ... OK!
            Created test_score/materials/test_material/
        """.replace(
            "/", os.path.sep
        ),
    )


def test_success(paths):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    script = abjadext.cli.ManageMaterialScript()
    command = ["--new", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Creating material subpackage 'test_material' ...
            Reading test_score/metadata.json ... OK!
            Created test_score/materials/test_material/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert paths.materials_path.joinpath("test_material").exists()
    expected_files = [
        "test_score/test_score/materials/.gitignore",
        "test_score/test_score/materials/__init__.py",
        "test_score/test_score/materials/test_material/__init__.py",
        "test_score/test_score/materials/test_material/definition.py",
    ]
    if platform.system().lower() == "windows":
        expected_files = [_.replace("/", os.path.sep) for _ in expected_files]
    pytest.helpers.compare_path_contents(
        paths.materials_path, expected_files, paths.test_directory_path
    )
