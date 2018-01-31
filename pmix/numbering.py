"""Translate a numbering scheme into actual numbers.

Start a section with a fixed number. Examples are:

    - A
    - a
    - 001
    - 200
    - Q320

Enter a silenced fixed number with '~'. This is useful to start a series
without numbering.

    - ~A
    - ~000
    - ~Q300

TODO: Silence any of the other increments by starting with a '~'.

    - ~^1
    - ~<4

Increment with special strings starting with '^'.

    - '^1'
    - '^a'
    - '^1a'
    - '^i'
    - '^A'

Keep the same as previous numbers in the same series with the lookback symbol
'<'.

    - '<'
    - '<3'

Lookbacks can be followed by an increment.

    - '<3^a'

Resume a previous section with the '*' symbol. '*' alone refers to one previous

    - '*^1'
    - '*A^A'
    - '*001^1'

Sticky questions are marked with a '#'.

    - '#LCL_101'

TODO: Count up to a fixed number with '>'.

    - '>1'
    - '>A'

...and then a fixed number such as 099 with '>1@099'
"""
import argparse
import copy
import os.path
import re

import pmix.utils as utils
from pmix.xlsform import Xlsform


DEFAULT_NUM_COL = 'N'
LOWER_LETTERS = tuple('abcdefghijklmnopqrstuvwxyz')
UPPER_LETTERS = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ROMAN_NUMERALS = ('i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x')
PUNCTUATION = tuple(':-)._')


class NumberingContext:
    """Class to represent the context in which numbering occurs."""

    def __init__(self):
        """Initialize the numbering context with empty values."""
        self.stream = []
        self.numbers = []
        self.prev_series = None
        self.current_series = None
        self.all_series = {}
        self.stickies = []

    def next(self, item):
        """Process the next item in the stream.

        A stream includes commands and non-commands. Remember but do nothing
        with the non-commands.
        """
        self.stream.append(item)
        try:
            self.parse_cmd(item)
        except ValueError:
            num = Numbering(item)
            self.new_series_add(num)

    def parse_cmd(self, cmd):
        """Parse a command in this miniature language."""
        if cmd.startswith('^'):
            self.increment(cmd)
        elif cmd.startswith('<'):
            self.lookback(cmd)
        elif cmd.startswith('#'):
            self.sticky(cmd)
        elif cmd.startswith('~'):
            self.silent(cmd)
        elif cmd.startswith('>'):
            raise RuntimeError('">" not yet implemented')
        elif cmd.startswith('*'):
            self.resume(cmd)
        elif not cmd:
            self.blank()
        else:
            raise ValueError(cmd)

    def increment(self, cmd):
        """Parse an increment command and add the correct number."""
        new_num = copy.copy(self.current_series_last())
        new_num.silent = False
        new_num.increment(cmd)
        self.current_series_add(new_num)

    def lookback(self, cmd):
        """Parse a lookback command and add the correct number."""
        increment_pos = cmd.find('^')
        if increment_pos < 0:
            increment = ''
        else:
            increment = cmd[increment_pos:]
            cmd = cmd[:increment_pos]
        if cmd == '<':
            lookback = 1
        else:
            lookback = int(cmd[1:])
        new_num = copy.copy(self.current_series_last(lookback))
        new_num.silent = False
        if increment:
            new_num.increment(increment)
        self.current_series_add(new_num)


    def sticky(self, cmd):
        """Parse a sticky number command and add the correct number."""
        num_str = cmd[1:]
        num = Numbering(num_str)
        self.numbers.append(num)
        self.stickies.append(num)

    def silent(self, cmd):
        """Parse a silent fixed number command and add to the list."""
        num_str = cmd[1:]
        num = Numbering.init_silent(num_str)
        self.new_series_add(num)

    def resume(self, cmd):
        """Resume a previous series."""
        if cmd[1] in '<^':
            tmp = self.current_series
            self.current_series = self.prev_series
            self.prev_series = tmp
            self.parse_cmd(cmd[1:])
        else:
            raise RuntimeError('"*NUM" not yet implemented')

    def blank(self):
        """Parse an empty command."""
        self.numbers.append(None)

    def current_series_add(self, num):
        """Add a number to the current series."""
        self.all_series[str(self.current_series)].append(num)
        self.numbers.append(num)

    def new_series_add(self, num):
        """Add a number to start a new series."""
        self.prev_series = self.current_series
        self.current_series = num
        self.all_series[str(num)] = [num]
        self.numbers.append(num)

    def current_series_last(self, lookback=1):
        """Return the number in the current series starting from the back."""
        last = self.all_series[str(self.current_series)][-lookback]
        return last

    def string_iter(self):
        """Yield each number as a string for numbering."""
        for item in self:
            if item:
                yield item.to_string()
            else:
                yield ''

    def filtered_iter(self):
        """Return an iterator that skips the non-number entries."""
        return iter(filter(None, self.numbers))

    def __iter__(self):
        """Return an iterator over all entries, including the None's."""
        return iter(self.numbers)


# pylint: disable=too-many-instance-attributes
class Numbering:
    """Class to represent a numbering object.

    Currently supported formats are:

    - Uppercase letters
      + A
    - Numbers, possibly with a prefix
      + LCL_101
      + 001

    - An extended number, which is a Number above, plus a lowercase letter,
      and possibly punctuation and a roman numeral.
      + 201a
      + 201a.i
    """

    letter_re = r'^[a-zA-Z]$'
    number_re = r'^([^\s\d~<>@^#*]*)(\d+)$'
    punc_re = r'([:\-)._])'
    ext_letter_re = r'^([^\s\d~<>@^#*]*)(\d+){}?([a-z])$'.format(punc_re)
    roman_re = r'(i{1,3}|iv|v|vi{1,3}|ix|x)'
    ext_roman_re = r'^([^\s\d~<>@^#*]*)(\d+){}?([a-z]){}{}$'
    ext_roman_re = ext_roman_re.format(punc_re, punc_re, roman_re)

    letter_prog = re.compile(letter_re)
    number_prog = re.compile(number_re)
    ext_roman_prog = re.compile(ext_roman_re)
    ext_letter_prog = re.compile(ext_letter_re)

    def __init__(self, numbering=None):
        """Take input numbering and break apart incrementable components."""
        self.silent = False
        if numbering is None:
            self.reset()
        else:
            self.set(numbering)

    @classmethod
    def init_silent(cls, numbering=None):
        """Create and return a silent Numbering."""
        num = cls(numbering)
        num.silent = True
        return num

    # pylint: disable=attribute-defined-outside-init
    def reset(self):
        """Set all components of the numbering to empty string."""
        self.letter = ''
        self.leader = ''
        self.number = ''
        self.punc0 = ''
        self.lower = ''
        self.punc1 = ''
        self.roman = ''

    def set(self, numbering):
        """Take input numbering and break apart incrementable components."""
        self.reset()

        letter_match = self.letter_prog.match(numbering)
        number_match = self.number_prog.match(numbering)
        ext_roman_match = self.ext_roman_prog.match(numbering)
        ext_letter_match = self.ext_letter_prog.match(numbering)
        if letter_match:
            self.letter = numbering
        elif number_match:
            self.leader = number_match.group(1)
            self.number = number_match.group(2)
        elif ext_letter_match:
            self.leader = ext_letter_match.group(1)
            self.number = ext_letter_match.group(2)
            self.punc0 = ext_letter_match.group(3)
            self.lower = ext_letter_match.group(4)
        elif ext_roman_match:
            self.leader = ext_roman_match.group(1)
            self.number = ext_roman_match.group(2)
            self.punc0 = ext_roman_match.group(3)
            self.lower = ext_roman_match.group(4)
            self.punc1 = ext_roman_match.group(5)
            self.roman = ext_roman_match.group(6)
        else:
            raise ValueError(numbering)

        if self.punc0 is None:
            self.punc0 = ''

    def increment(self, cmd):
        """Increment a number based on an increment command."""
        sub_cmds = list(cmd)
        if sub_cmds.pop(0) != '^':
            msg = 'Bad increment "{}". Must start with "^"'.format(cmd)
            raise TypeError(msg)
        for item in sub_cmds:
            if item.isdigit():
                self.increase_number(item)
            elif item in ('i', 'v', 'x'):
                self.increase_roman(item)
            elif self.letter and item.isalpha():
                self.increase_letter(item)
            elif item.islower():  # and not self.letter
                self.increase_lower(item)
            else:
                msg = 'Bad increment "{}". Must be A, 1, a, or i.'.format(cmd)

    def increase_letter(self, letter):
        """Increase a letter by a specified amount.

        Args:
            letter (str): A single letter
        """
        if letter.isupper():
            cur_index = UPPER_LETTERS.index(self.letter)
            delta_index = UPPER_LETTERS.index(letter) + 1
            new_letter = UPPER_LETTERS[cur_index + delta_index]
            self.letter = new_letter
        else:
            # Assume lower case
            cur_index = LOWER_LETTERS.index(self.letter)
            delta_index = LOWER_LETTERS.index(letter) + 1
            new_letter = LOWER_LETTERS[cur_index + delta_index]
            self.letter = new_letter

    def increase_number(self, increment):
        """Increase a number by an increment.

        Args:
            increment (str): The amount to increase by. Should be > 0.
        """
        increment = int(increment)
        new_number = int(self.number) + increment
        if self.number.startswith('0'):
            self.number = str(new_number).zfill(len(self.number))
        else:
            self.number = str(new_number)

        self.lower = ''
        self.roman = ''

    def increase_lower(self, lower):
        """Increase an lower by a specified amount.

        Args:
            lower (str): A single lower case letter
        """
        cur_index = LOWER_LETTERS.index(self.lower) if self.lower else -1
        delta_index = LOWER_LETTERS.index(lower) + 1
        new_lower = LOWER_LETTERS[cur_index + delta_index]
        self.lower = new_lower

        self.roman = ''

    def increase_roman(self, roman):
        """Increase an roman by a specified amount.

        Args:
            roman (str): A single roman numeral
        """
        if not self.lower:
            msg = 'Cannot increase roman numeral without lower case letter'
            raise ValueError(msg)
        if not self.punc1:
            self.punc1 = '.'
        cur_index = ROMAN_NUMERALS.index(self.roman) if self.roman else -1
        delta_index = ROMAN_NUMERALS.index(roman) + 1
        new_roman = ROMAN_NUMERALS[cur_index + delta_index]
        self.roman = new_roman

    def to_string(self):
        """Convert to string for use in numbering."""
        if self.silent:
            return ''
        return str(self)

    def __str__(self):
        """Convert the numbering to a string."""
        expr = self.letter + self.leader + self.number
        if self.lower:
            expr += self.punc0 + self.lower
            if self.roman:
                expr += self.punc1 + self.roman
        if self.silent:
            expr = '~' + expr
        return expr

    def __repr__(self):
        """Return the repr of this numbering."""
        return 'Numbering("{}")'.format(str(self))


def compute_prepend_numbers(inpath, col, outpath, rm_on_empty=False):
    """Compute numbers based on mini-language and prepend to all labels.

    This program highlights cells in the following two specific cases:

    (1) The numbering column says there should be a number in the label, but
        there is no number found in the original label. In this case, the
        number is add to the label.
    (2) The numbering column does not produce a number, but the original label
        has a number. In this case, the number is removed.

    Adding a number means to join the number, the string '. ', and the text of
    the cell.

    Args:
        inpath (str): The path where to find the source file.
        col (str): The name of the column where to find numbering.
        outpath (str): The path where to write the new xlsxfile.
        rm_on_empty (bool): Remove numbers that exist when numbering column is
            blank.

    """
    xlsform = Xlsform(inpath)
    survey = xlsform['survey']
    context = NumberingContext()
    for cell in survey.column(col):
        context.next(str(cell))
    for i, header in enumerate(survey.column_headers()):
        if header.startswith('label') or header.startswith('ppp_label'):
            header_skipped = False
            for num, cell in zip(context.string_iter(), survey.column(i)):
                if not header_skipped:
                    header_skipped = True
                    continue
                if num:
                    old_text = str(cell)
                    cell_num, the_rest = utils.td_split_text(old_text)
                    new_text = '. '.join((num, the_rest))
                    cell.value = new_text
                    if not cell_num:
                        # Highlight yellow for adding a number
                        cell.set_highlight()
                    elif new_text != old_text:
                        # Highlight orange for changing a number
                        cell.set_highlight('HL_ORANGE')
                elif cell and rm_on_empty:
                    cell_num, the_rest = utils.td_split_text(str(cell))
                    if cell_num:
                        cell.value = the_rest
                        cell.set_highlight()
    xlsform.write_out(outpath)


def numbering_cli():
    """Run the command line interface for this module."""
    prog_desc = 'Update numbering in an ODK form'
    parser = argparse.ArgumentParser(description=prog_desc)
    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)
    numbering_help = ('Compute numbering based on a column in the "survey" '
                      'tab. If this option string is not given, '
                      'then a default of "N" is assumed for the column '
                      'header. This program updates label and ppp_label '
                      'columns.')
    parser.add_argument('-n', '--numbering', help=numbering_help)
    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)
    rm_help = ('Remove a number that pre-exists in a label if numbering '
               'column is blank.')
    parser.add_argument('-r', '--rm_on_empty', action='store_true',
                        help=rm_help)
    args = parser.parse_args()

    col = DEFAULT_NUM_COL
    if args.numbering:
        col = args.numbering
    filename, extension = os.path.splitext(args.xlsxfile)
    if args.outpath is None:
        outpath = os.path.join(filename+'-num'+extension)
    else:
        outpath = args.outpath
    compute_prepend_numbers(args.xlsxfile, col, outpath)
    print('Renumbered labels and wrote file to "{}"'.format(outpath))


if __name__ == '__main__':
    numbering_cli()
