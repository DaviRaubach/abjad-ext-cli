import os
import platform
from io import StringIO

import pytest
import uqbar.io
from uqbar.strings import normalize

import abjadext.cli


def test_lilypond_error(paths):
    """
    Handle failing LilyPond rendering.
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with open(str(definition_path), "w") as file_pointer:
        file_pointer.write(
            normalize(
                r"""
        import abjad


        test_material = abjad.lilypondfile.LilyPondFile.new()
        test_material.items.append(r'\this-does-not-exist')
        """
            )
        )
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_material' ...
        Illustrating test_score/materials/test_material/
            Importing test_score.materials.test_material.definition
                Abjad runtime: ... second...
            Writing test_score/materials/test_material/illustration.ly ... OK!
            Writing test_score/materials/test_material/illustration.pdf ... Failed!
        """.replace(
            "/", os.path.sep
        ),
    )
    illustration_ly_path = material_path.joinpath("illustration.ly")
    assert illustration_ly_path.exists()
    pytest.helpers.compare_lilypond_contents(
        illustration_ly_path,
        normalize(
            r"""
        \language "english" %! abjad.LilyPondFile._get_format_pieces()

        \header { %! abjad.LilyPondFile._get_formatted_blocks()
            tagline = ##f
        } %! abjad.LilyPondFile._get_formatted_blocks()

        \layout {}

        \paper {}

        \this-does-not-exist
        """
        ),
    )


def test_missing_definition(paths):
    """
    Handle missing definition.
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    definition_path.unlink()
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
            Illustration candidates: 'test_material' ...
            Illustrating test_score/materials/test_material/
                Importing test_score.materials.test_material.definition
        """.replace(
            "/", os.path.sep
        ),
    )


def test_python_cannot_illustrate(paths):
    """
    Handle un-illustrables.
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with open(str(definition_path), "w") as file_pointer:
        file_pointer.write(
            normalize(
                r"""
        test_material = None
        """
            )
        )
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_material' ...
        Illustrating test_score/materials/test_material/
            Importing test_score.materials.test_material.definition
            Cannot illustrate material of type NoneType.
        """.replace(
            "/", os.path.sep
        ),
    )


def test_python_error_on_illustrate(paths):
    """
    Handle exceptions inside the Python module on __call__().
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with open(str(definition_path), "w") as file_pointer:
        file_pointer.write(
            normalize(
                r"""
        class Foo:
            def __illustrate__(paths):
                raise TypeError('This is fake.')

        test_material = Foo()
        """
            )
        )
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_material' ...
        Illustrating test_score/materials/test_material/
            Importing test_score.materials.test_material.definition
        """.replace(
            "/", os.path.sep
        ),
    )


def test_python_error_on_import(paths):
    """
    Handle exceptions inside the Python module on import.
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with open(str(definition_path), "a") as file_pointer:
        file_pointer.write("\n\nfailure = 1 / 0\n")
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_material' ...
        Illustrating test_score/materials/test_material/
            Importing test_score.materials.test_material.definition
        """.replace(
            "/", os.path.sep
        ),
    )


def test_success_all_materials(paths, open_file_mock):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "material_one")
    pytest.helpers.create_material(paths.test_directory_path, "material_two")
    pytest.helpers.create_material(paths.test_directory_path, "material_three")
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "*"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: '*' ...
        Illustrating test_score/materials/material_one/
            Importing test_score.materials.material_one.definition
                Abjad runtime: ... second...
            Writing test_score/materials/material_one/illustration.ly ... OK!
            Writing test_score/materials/material_one/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/material_one/
        Illustrating test_score/materials/material_three/
            Importing test_score.materials.material_three.definition
                Abjad runtime: ... second...
            Writing test_score/materials/material_three/illustration.ly ... OK!
            Writing test_score/materials/material_three/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/material_three/
        Illustrating test_score/materials/material_two/
            Importing test_score.materials.material_two.definition
                Abjad runtime: ... second...
            Writing test_score/materials/material_two/illustration.ly ... OK!
            Writing test_score/materials/material_two/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/material_two/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert (paths.materials_path / "material_one" / "illustration.pdf").exists()
    assert (paths.materials_path / "material_two" / "illustration.pdf").exists()
    assert (paths.materials_path / "material_three" / "illustration.pdf").exists()


def test_success_filtered_materials(paths, open_file_mock):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "material_one")
    pytest.helpers.create_material(paths.test_directory_path, "material_two")
    pytest.helpers.create_material(paths.test_directory_path, "material_three")
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "material_t*"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'material_t*' ...
        Illustrating test_score/materials/material_three/
            Importing test_score.materials.material_three.definition
                Abjad runtime: ... second...
            Writing test_score/materials/material_three/illustration.ly ... OK!
            Writing test_score/materials/material_three/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/material_three/
        Illustrating test_score/materials/material_two/
            Importing test_score.materials.material_two.definition
                Abjad runtime: ... second...
            Writing test_score/materials/material_two/illustration.ly ... OK!
            Writing test_score/materials/material_two/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/material_two/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert not (paths.materials_path / "material_one" / "illustration.pdf").exists()
    assert (paths.materials_path / "material_two" / "illustration.pdf").exists()
    assert (paths.materials_path / "material_three" / "illustration.pdf").exists()


def test_success_one_material(paths, open_file_mock):
    expected_files = [
        "test_score/test_score/materials/.gitignore",
        "test_score/test_score/materials/__init__.py",
        "test_score/test_score/materials/test_material/__init__.py",
        "test_score/test_score/materials/test_material/definition.py",
        "test_score/test_score/materials/test_material/illustration.ly",
        "test_score/test_score/materials/test_material/illustration.pdf",
    ]
    if platform.system().lower() == "windows":
        expected_files = [_.replace("/", os.path.sep) for _ in expected_files]
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_material(paths.test_directory_path, "test_material")
    script = abjadext.cli.ManageMaterialScript()
    command = ["--illustrate", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_material' ...
        Illustrating test_score/materials/test_material/
            Importing test_score.materials.test_material.definition
                Abjad runtime: ... second...
            Writing test_score/materials/test_material/illustration.ly ... OK!
            Writing test_score/materials/test_material/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/materials/test_material/
        """.replace(
            "/", os.path.sep
        ),
    )
    pytest.helpers.compare_path_contents(
        paths.materials_path, expected_files, paths.test_directory_path
    )
    illustration_path = paths.materials_path.joinpath(
        "test_material", "illustration.ly"
    )
    pytest.helpers.compare_lilypond_contents(
        illustration_path,
        normalize(
            r"""
            \language "english" %! abjad.LilyPondFile._get_format_pieces()

            \header { %! abjad.LilyPondFile._get_formatted_blocks()
                tagline = ##f
            } %! abjad.LilyPondFile._get_formatted_blocks()

            \layout {}

            \paper {}

            \markup { "An example illustrable material." }
            """
        ),
    )
