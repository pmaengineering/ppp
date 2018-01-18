"""Useful string functions for PMIX."""

import re


NUMBER_RE = r"""
            ^\s*                # Begin with possible whitespace.
            (
                [a-zA-Z]        # Start with a letter
            |
                (
                    \S*         # or start with non-whitespace and
                    \d+         # one or more numbers, then possibly
                    [.a-z]*     # dots (.) and lower-case letters
                )
            )
            [.:)]               # Always end with one of '.', ':', ')' and
            \s+                 # finally whitespace
            """


# pylint: disable=no-member
NUMBER_PROG = re.compile(NUMBER_RE, re.VERBOSE)


def td_clean_string(text):
    """Clean a string for a translation dictionary.

    Removes extra whitespace and a number if found.

    Args:
        text (str): String to be cleaned.

    Returns:
        String with extra whitespace and leading number (if found) removed.
    """
    text = clean_string(text)
    _, text = td_split_text(text)
    return text


def td_split_text(text):
    """Split text into a number and the rest.

    This splitting is done using the regex program `NUMBER_PROG`.

    Args:
        text (str): String to split

    Returns:
        A tuple `(number, the_rest)`. The original string is `number +
        the_rest`. If no number is found with the regex, then `number` is
        '', the empty string.
    """
    number = ''
    the_rest = text
    if len(text.split()) > 1:
        match = NUMBER_PROG.match(text)
        if match:
            number = text[match.span()[0]:match.span()[1]]
            the_rest = text[match.span()[1]:]
    return number, the_rest


def clean_string(text):
    """Clean a string for addition into the translation dictionary.

    Leading and trailing whitespace is removed. Newlines are converted to
    the UNIX style.

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
    text = space_space_fix(text)
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


def space_space_fix(text):
    """Replace "space-space" with "space".

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    space_space = '  '
    space = ' '
    while space_space in text:
        text = text.replace(space_space, space)
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


def show_whitespace(text):
    """Replace whitespace characters with unicode.

    Args:
        text (str): The string to work with

    Returns:
        The text with the whitespace now visible.
    """
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    # Middle dot
    text = text.replace(' ', '\u00b7')
    # Small right triangle
    text = text.replace('\t', '\u25b8')
    # Downwards arrow with corner leftwards
    text = text.replace('\n', '\u21b5')
    return text


def number_to_excel_column(col):
    """Convert a zero-indexed column number to Excel column name.

    Args:
        col (int): The column number, e.g. from a Worksheet. Should be
            zero-indexed

    Returns:
        str: The Excel column name

    Raises:
        ValueError: If col > 26*26 or col < 0
    """
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if len(letters) * len(letters) < col or col < 0:
        raise ValueError(col)
    div, mod = divmod(col, len(letters))
    primary_letter = letters[mod]
    if div > 0:
        return letters[div - 1] + primary_letter
    return primary_letter
