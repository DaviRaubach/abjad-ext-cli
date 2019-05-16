import json

import pytest


def test_1(paths, open_file_mock):
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.install_fancy_segment_maker(paths.test_directory_path)
    path_1 = pytest.helpers.create_segment(paths.test_directory_path, "segment_one")
    path_2 = pytest.helpers.create_segment(paths.test_directory_path, "segment_two")
    path_3 = pytest.helpers.create_segment(paths.test_directory_path, "segment_three")
    pytest.helpers.illustrate_segments(paths.test_directory_path)
    with open(str(path_1.joinpath("metadata.json")), "r") as file_pointer:
        metadata_1 = json.loads(file_pointer.read())
    with open(str(path_2.joinpath("metadata.json")), "r") as file_pointer:
        metadata_2 = json.loads(file_pointer.read())
    with open(str(path_3.joinpath("metadata.json")), "r") as file_pointer:
        metadata_3 = json.loads(file_pointer.read())
    assert metadata_1 == {
        "first_bar_number": 1,
        "measure_count": 1,
        "segment_count": 3,
        "segment_number": 1,
    }
    assert metadata_2 == {
        "first_bar_number": 2,
        "measure_count": 1,
        "segment_count": 3,
        "segment_number": 2,
    }
    assert metadata_3 == {
        "first_bar_number": 3,
        "measure_count": 1,
        "segment_count": 3,
        "segment_number": 3,
    }


def test_2(paths, open_file_mock):
    pytest.helpers.create_score(paths.test_directory_path)
    pytest.helpers.install_fancy_segment_maker(paths.test_directory_path)
    segment_path = pytest.helpers.create_segment(
        paths.test_directory_path, "test_segment"
    )
    pytest.helpers.illustrate_segment(paths.test_directory_path, "test_segment")
    illustration_path = segment_path.joinpath("illustration.ly")
    pytest.helpers.compare_lilypond_contents(
        illustration_path,
        r"""
        \language "english" %! abjad.LilyPondFile
        <BLANKLINE>
        \include "../../stylesheets/stylesheet.ily" %! abjad.LilyPondFile
        <BLANKLINE>
        \header { %! abjad.LilyPondFile
            tagline = ##f
        } %! abjad.LilyPondFile
        <BLANKLINE>
        \layout {}
        <BLANKLINE>
        \paper {}
        <BLANKLINE>
        \score { %! abjad.LilyPondFile
            \context Score = "String_Quartet_Score" %! abjad.StringQuartetScoreTemplate
            <<                                      %! abjad.StringQuartetScoreTemplate
                \context StaffGroup = "String_Quartet_Staff_Group" %! abjad.StringQuartetScoreTemplate
                <<                                                 %! abjad.StringQuartetScoreTemplate
                    \tag #'first-violin
                    \context Staff = "First_Violin_Staff" %! abjad.StringQuartetScoreTemplate
                    {                                     %! abjad.StringQuartetScoreTemplate
                        \context Voice = "First_Violin_Voice" %! abjad.StringQuartetScoreTemplate
                        {                                     %! abjad.StringQuartetScoreTemplate
                            {
                                \time 4/4
                                \clef "treble" %! abjad.ScoreTemplate.attach_defaults
                                c'1
                                \bar "|." %! SCORE_1
                            }
                        } %! abjad.StringQuartetScoreTemplate
                    } %! abjad.StringQuartetScoreTemplate
                    \tag #'second-violin
                    \context Staff = "Second_Violin_Staff" %! abjad.StringQuartetScoreTemplate
                    {                                      %! abjad.StringQuartetScoreTemplate
                        \context Voice = "Second_Violin_Voice" %! abjad.StringQuartetScoreTemplate
                        {                                      %! abjad.StringQuartetScoreTemplate
                            {
                                \time 4/4
                                \clef "treble" %! abjad.ScoreTemplate.attach_defaults
                                c'1
                                \bar "|." %! SCORE_1
                            }
                        } %! abjad.StringQuartetScoreTemplate
                    } %! abjad.StringQuartetScoreTemplate
                    \tag #'viola
                    \context Staff = "Viola_Staff" %! abjad.StringQuartetScoreTemplate
                    {                              %! abjad.StringQuartetScoreTemplate
                        \context Voice = "Viola_Voice" %! abjad.StringQuartetScoreTemplate
                        {                              %! abjad.StringQuartetScoreTemplate
                            {
                                \time 4/4
                                \clef "alto" %! abjad.ScoreTemplate.attach_defaults
                                c'1
                                \bar "|." %! SCORE_1
                            }
                        } %! abjad.StringQuartetScoreTemplate
                    } %! abjad.StringQuartetScoreTemplate
                    \tag #'cello
                    \context Staff = "Cello_Staff" %! abjad.StringQuartetScoreTemplate
                    {                              %! abjad.StringQuartetScoreTemplate
                        \context Voice = "Cello_Voice" %! abjad.StringQuartetScoreTemplate
                        {                              %! abjad.StringQuartetScoreTemplate
                            {
                                \time 4/4
                                \clef "bass" %! abjad.ScoreTemplate.attach_defaults
                                c'1
                                \bar "|." %! SCORE_1
                            }
                        } %! abjad.StringQuartetScoreTemplate
                    } %! abjad.StringQuartetScoreTemplate
                >> %! abjad.StringQuartetScoreTemplate
            >> %! abjad.StringQuartetScoreTemplate
        } %! abjad.LilyPondFile
        """,
    )
