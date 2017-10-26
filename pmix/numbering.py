"""Translate a numbering scheme into actual numbers.

Start a section with a fixed number. Examples are:

    - A
    - 001
    - 200
    - Q320

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

Resume a previous section with the '*' symbol.

    - '*A^A'
    - '*001^1'

Sticky questions are marked with a '#'.

    - '#LCL_101'

Count up to a fixed number with '>'.

    - '>1'
    - '>A'

...and then a fixed number such as 099.
"""

import copy
import re


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
            self.current_series = num
            self.all_series[str(num)] = [num]
            self.numbers.append(num)

    def parse_cmd(self, cmd):
        """Parse a command in this miniature language."""
        if cmd.startswith('^'):
            self.increment(cmd)
        elif cmd.startswith('<'):
            self.lookback(cmd)
        elif cmd.startswith('#'):
            self.sticky(cmd)
        elif not cmd:
            self.blank()
        else:
            raise ValueError(cmd)

    def increment(self, cmd):
        """Parse an increment command and add the correct number."""
        new_num = copy.copy(self.current_series_last())
        new_num.increment(cmd)
        self.current_series_add(new_num)

    def lookback(self, cmd):
        """Parse a lookback command and add the correct number."""
        if cmd == '<':
            lookback = 1
        else:
            lookback = int(cmd[1:])
        new_num = copy.copy(self.current_series_last(lookback))
        self.current_series_add(new_num)

    def sticky(self, cmd):
        """Parse a sticky number command and add the correct number."""
        num_str = cmd[1:]
        num = Numbering(num_str)
        self.numbers.append(num)
        self.stickies.append(num)

    def blank(self):
        """Parse an empty command."""
        self.numbers.append(None)

    def current_series_add(self, num):
        """Add a number to the current series."""
        self.all_series[str(self.current_series)].append(num)
        self.numbers.append(num)

    def current_series_last(self, lookback=1):
        """Return the number in the current series starting from the back."""
        last = self.all_series[str(self.current_series)][-lookback]
        return last

    def string_iter(self):
        """Yield each number as a string."""
        for item in self:
            if item:
                yield str(item)
            else:
                yield ''

    def filtered_iter(self):
        """Return an iterator that skips the non-number entries."""
        return iter(filter(None, self.numbers))

    def __iter__(self):
        """Return an iterator over all entries, including the None's."""
        return iter(self.numbers)

    def is_numbering(self, item):
        """Return true if the item is numbering."""
        pass

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

    upper_re = r'^[A-Z]$'
    number_re = r'^([^\s\d<>@^#*]*)(\d+)$'
    punc_re = r'([:\-)._])'
    ext_letter_re = r'^([^\s\d<>@^#*]*)(\d+){}?([a-z])$'.format(punc_re)
    roman_re = r'(i{1,3}|iv|v|vi{1,3}|ix|x)'
    ext_roman_re = r'^([^\s\d<>@^#*]*)(\d+){}?([a-z]){}{}$'
    ext_roman_re = ext_roman_re.format(punc_re, punc_re, roman_re)

    upper_prog = re.compile(upper_re)
    number_prog = re.compile(number_re)
    ext_roman_prog = re.compile(ext_roman_re)
    ext_letter_prog = re.compile(ext_letter_re)

    def __init__(self, numbering=None):
        """Take input numbering and break apart incrementable components."""
        if numbering is None:
            self.reset()
        else:
            self.set(numbering)

    def reset(self):
        """Set all components of the numbering to empty string."""
        self.upper = ''
        self.leader = ''
        self.number = ''
        self.punc0 = ''
        self.lower = ''
        self.punc1 = ''
        self.roman = ''

    def set(self, numbering):
        """Take input numbering and break apart incrementable components."""
        self.reset()

        upper_match = self.upper_prog.match(numbering)
        number_match = self.number_prog.match(numbering)
        ext_roman_match = self.ext_roman_prog.match(numbering)
        ext_letter_match = self.ext_letter_prog.match(numbering)
        if upper_match:
            self.upper = numbering
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
            elif item.islower():
                self.increase_lower(item)
            elif item.isupper():
                self.increase_upper(item)
            else:
                msg = 'Bad increment "{}". Must be A, 1, a, or i.'.format(cmd)


    def increase_upper(self, upper):
        """Increase an upper by a specified amount.

        Args:
            upper (str): A single upper case letter
        """
        cur_index = UPPER_LETTERS.index(self.upper)
        delta_index = UPPER_LETTERS.index(upper) + 1
        new_upper = UPPER_LETTERS[cur_index + delta_index]
        self.upper = new_upper


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
            upper (str): A single lower case letter
        """
        cur_index = LOWER_LETTERS.index(self.lower) if self.lower else -1
        delta_index = LOWER_LETTERS.index(lower) + 1
        new_lower = LOWER_LETTERS[cur_index + delta_index]
        self.lower = new_lower

    def increase_roman(self, roman):
        """Increase an roman by a specified amount.

        Args:
            upper (str): A single roman numeral
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

    def __str__(self):
        """Convert the numbering to a string."""
        expr = self.upper + self.leader + self.number
        if self.lower:
            expr += self.punc0 + self.lower
            if self.roman:
                expr += self.punc1 + self.roman
        return expr

    def __repr__(self):
        """Return the repr of this numbering."""
        return 'Numbering("{}")'.format(str(self))
