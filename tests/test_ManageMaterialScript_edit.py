from io import StringIO

import abjadext.cli
import pytest
import uqbar.io

import abjad


def test_success(paths, call_subprocess_mock):
    string_io = StringIO()
    call_subprocess_mock.return_value = 0
    pytest.helpers.create_score(paths.test_directory_path)
    material_path = pytest.helpers.create_material(
        paths.test_directory_path, "test_material"
    )
    script = abjadext.cli.ManageMaterialScript()
    command = ["--edit", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""Edit candidates: 'test_material' ...""",
    )
    definition_path = material_path.joinpath("definition.py")
    command = "{} {!s}".format(
        abjad.abjad_configuration.get_text_editor(), definition_path
    )
    call_subprocess_mock.assert_called_with(command)
