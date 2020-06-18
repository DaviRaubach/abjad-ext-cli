import os

import abjad


def get_text_editor():
    text_editor = abjad.configuration["text_editor"]
    if text_editor is not None:
        return text_editor
    elif os.name == "posix":
        return "vi"
    else:
        return "edit"
