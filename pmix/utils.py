"""Useful functions for PMIX."""


def clean_string(text):
    """Clean a string for addition into the translation dictionary.

    Leading and trailing whitespace is removed. Newlines are converted to
    the UNIX style. Opening number is removed if found by `split_text`.

    Args:
        text (str): String to be cleaned.

    Returns:
        A cleaned string with number removed.
    """
    text = text.strip()
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = space_newline_fix(text)
    text = newline_space_fix(text)
    return text

def newline_space_fix(text):
    """Replace "newline-space" with "newline".

    This function was particularly useful when converting between Google
    Sheets and .xlsx format.

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    newline_space = '\n '
    fix = '\n'
    while newline_space in text:
        text = text.replace(newline_space, fix)
    return text

def space_newline_fix(text):
    """Replace "space-newline" with "newline".

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    space_newline = ' \n'
    fix = '\n'
    while space_newline in text:
        text = text.replace(space_newline, fix)
    return text
