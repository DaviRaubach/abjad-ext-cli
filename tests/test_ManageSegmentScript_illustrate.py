import os
import platform
from io import StringIO

import abjadext.cli
import pytest
import uqbar.io
from uqbar.strings import normalize


def test_lilypond_error(paths):
    r"""
    Handle failing LilyPond rendering.
    """
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    definition_path = segment_path.joinpath("definition.py")
    with open(str(definition_path), "w") as file_pointer:
        file_pointer.write(
            normalize(
                r"""
        import abjad


        class FaultySegmentMaker(abjad.SegmentMaker):

            def run(
                paths,
                metadata=None,
                previous_metadata=None,
                ):
                paths._metadata = metadata
                lilypond_file = abjad.lilypondfile.LilyPondFile.new(
                    abjad.core.Staff("c'4 ( d'4 e'4 f'4 )")
                    )
                lilypond_file.items.append(r'\this-does-not-exist')
                return lilypond_file

        segment_maker = FaultySegmentMaker()
        """
            )
        )
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/test_segment/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/test_segment/metadata.json ... JSON does not exist.
            Importing test_score.segments.test_segment.definition
            Writing test_score/segments/test_segment/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/test_segment/illustration.ly ... OK!
            Writing test_score/segments/test_segment/illustration.pdf ... Failed!
        """.replace(
            "/", os.path.sep
        ),
    )
    illustration_ly_path = segment_path.joinpath("illustration.ly")
    assert illustration_ly_path.exists()
    pytest.helpers.compare_lilypond_contents(
        illustration_ly_path,
        normalize(
            r"""
        \language "english" %! LilyPondFile

        \header { %! LilyPondFile
            tagline = ##f
        } %! LilyPondFile

        \layout {}

        \paper {}

        \score { %! LilyPondFile
            \new Staff
            {
                c'4
                (
                d'4
                e'4
                f'4
                )
            }
        } %! LilyPondFile

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
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    definition_path = segment_path.joinpath("definition.py")
    definition_path.unlink()
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/test_segment/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/test_segment/metadata.json ... JSON does not exist.
            Importing test_score.segments.test_segment.definition
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
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    definition_path = segment_path.joinpath("definition.py")
    with open(str(definition_path), "w") as file_pointer:
        file_pointer.write(
            normalize(
                r"""
        import abjad


        class FaultySegmentMaker(abjad.SegmentMaker):

            def __call__(
                paths,
                metadata=None,
                previous_metadata=None,
                ):
                raise TypeError('This is intentionally broken.')

        segment_maker = FaultySegmentMaker()
        """
            )
        )
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/test_segment/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/test_segment/metadata.json ... JSON does not exist.
            Importing test_score.segments.test_segment.definition
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
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    definition_path = segment_path.joinpath("definition.py")
    with open(str(definition_path), "a") as file_pointer:
        file_pointer.write("\n\nfailure = 1 / 0\n")
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command, expect_error=True)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/test_segment/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/test_segment/metadata.json ... JSON does not exist.
            Importing test_score.segments.test_segment.definition
        """.replace(
            "/", os.path.sep
        ),
    )


def test_success_all_segments(paths, open_file_mock):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "segment_one")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_two")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_three")
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "*"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: '*' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/segment_one/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/segment_one/metadata.json ... JSON does not exist.
            Importing test_score.segments.segment_one.definition
            Writing test_score/segments/segment_one/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/segment_one/illustration.ly ... OK!
            Writing test_score/segments/segment_one/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/segment_one/
        Illustrating test_score/segments/segment_two/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/segment_one/metadata.json ... OK!
            Reading test_score/segments/segment_two/metadata.json ... JSON does not exist.
            Importing test_score.segments.segment_two.definition
            Writing test_score/segments/segment_two/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/segment_two/illustration.ly ... OK!
            Writing test_score/segments/segment_two/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/segment_two/
        Illustrating test_score/segments/segment_three/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/segment_two/metadata.json ... OK!
            Reading test_score/segments/segment_three/metadata.json ... JSON does not exist.
            Importing test_score.segments.segment_three.definition
            Writing test_score/segments/segment_three/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/segment_three/illustration.ly ... OK!
            Writing test_score/segments/segment_three/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/segment_three/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert paths.segments_path.joinpath("segment_one", "illustration.pdf").exists()
    assert paths.segments_path.joinpath("segment_two", "illustration.pdf").exists()
    assert paths.segments_path.joinpath("segment_three", "illustration.pdf").exists()


def test_success_filtered_segments(paths, open_file_mock):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "segment_one")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_two")
    pytest.helpers.create_segment(paths.test_directory_path, "segment_three")
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "segment_t*"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'segment_t*' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/segment_two/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/segment_one/metadata.json ... JSON does not exist.
            Reading test_score/segments/segment_two/metadata.json ... JSON does not exist.
            Importing test_score.segments.segment_two.definition
            Writing test_score/segments/segment_two/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/segment_two/illustration.ly ... OK!
            Writing test_score/segments/segment_two/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/segment_two/
        Illustrating test_score/segments/segment_three/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/segment_two/metadata.json ... OK!
            Reading test_score/segments/segment_three/metadata.json ... JSON does not exist.
            Importing test_score.segments.segment_three.definition
            Writing test_score/segments/segment_three/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/segment_three/illustration.ly ... OK!
            Writing test_score/segments/segment_three/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/segment_three/
        """.replace(
            "/", os.path.sep
        ),
    )
    assert not paths.segments_path.joinpath("segment_one", "illustration.pdf").exists()
    assert paths.segments_path.joinpath("segment_two", "illustration.pdf").exists()
    assert paths.segments_path.joinpath("segment_three", "illustration.pdf").exists()


def test_success_one_segment(paths, open_file_mock):
    string_io = StringIO()
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.create_segment(paths.test_directory_path, "test_segment")
    script = abjadext.cli.ManageSegmentScript()
    command = ["--illustrate", "test_segment"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(paths.score_path):
            pytest.helpers.run_script(script, command)
    pytest.helpers.compare_strings(
        actual=string_io.getvalue(),
        expected=r"""
        Illustration candidates: 'test_segment' ...
            Reading test_score/segments/metadata.json ... OK!
        Illustrating test_score/segments/test_segment/
            Reading test_score/segments/metadata.json ... OK!
            Reading test_score/segments/test_segment/metadata.json ... JSON does not exist.
            Importing test_score.segments.test_segment.definition
            Writing test_score/segments/test_segment/metadata.json
                Abjad runtime: ... second...
            Writing test_score/segments/test_segment/illustration.ly ... OK!
            Writing test_score/segments/test_segment/illustration.pdf ... OK!
                LilyPond runtime: ... second...
            Illustrated test_score/segments/test_segment/
        """.replace(
            "/", os.path.sep
        ),
    )
    expected_files = [
        "test_score/test_score/segments/.gitignore",
        "test_score/test_score/segments/__init__.py",
        "test_score/test_score/segments/metadata.json",
        "test_score/test_score/segments/test_segment/__init__.py",
        "test_score/test_score/segments/test_segment/definition.py",
        "test_score/test_score/segments/test_segment/illustration.ly",
        "test_score/test_score/segments/test_segment/illustration.pdf",
        "test_score/test_score/segments/test_segment/metadata.json",
    ]
    if platform.system().lower() == "windows":
        expected_files = [_.replace("/", os.path.sep) for _ in expected_files]
    pytest.helpers.compare_path_contents(
        paths.segments_path, expected_files, paths.test_directory_path
    )
    illustration_path = paths.segments_path.joinpath("test_segment", "illustration.ly")
    pytest.helpers.compare_lilypond_contents(
        illustration_path,
        normalize(
            r"""
            \language "english" %! LilyPondFile

            \include "../../stylesheets/stylesheet.ily" %! LilyPondFile

            \header { %! LilyPondFile
                tagline = ##f
            } %! LilyPondFile

            \layout {}

            \paper {}

            \score { %! LilyPondFile
                \context Score = "Example_Score"
                <<
                    \context Staff = "Example_Staff"
                    {
                        \context Voice = "Example_Voice"
                        {
                            c'4
                            (
                            d'4
                            e'4
                            f'4
                            )
                        }
                    }
                >>
            } %! LilyPondFile
        """
        ),
    )
