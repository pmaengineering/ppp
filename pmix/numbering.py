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

Keep the same as previous numbers with the lookback symbol '<'.

    - '<'
    - '<3'

Resume a previous section with the '*' symbol.

    - '*A^A'
    - '*001^1'

One time questions are marked with a '#'.

    - '#LCL_101'

Count up to a fixed number with '>'.

    - '>1'
    - '>A'

...and then a fixed number such as 099.
"""

import re


LOWER_LETTERS = tuple('abcdefghijklmnopqrstuvwxyz')
UPPER_LETTERS = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ROMAN_NUMERALS = ('i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x')
PUNCTUATION = tuple(':-)._')


class NumberingContext:

    def __init__(self):
        self.current_series = None
        self.all_series = {}

    def next(self, item):
        pass

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

    - An extended number, which is a Number above, plus a lowercase letter or a
      roman numeral.
      + 201a
      + 201.i
    """

    upper_re = r'^[A-Z]$'
    number_re = r'^([^\s\d]*)(\d+)$'
    punc_re = r'([:\-)._])'
    ext_letter_re = r'^([^\s\d]*)(\d+){}?([a-z])$'.format(punc_re)
    roman_re = r'(i{1,3}|iv|v|vi{1,3}|ix|x)'
    ext_roman_re = r'^([^\s\d]*)(\d+){}?([a-z]){}{}$'
    ext_roman_re = ext_roman_re.format(punc_re, punc_re, roman_re)

    upper_prog = re.compile(upper_re)
    number_prog = re.compile(number_re)
    ext_roman_prog = re.compile(ext_roman_re)
    ext_letter_prog = re.compile(ext_letter_re)

    def __init__(self, numbering):
        """Take input numbering and break apart incrementable components."""
        self.upper = ''
        self.leader = ''
        self.number = ''
        self.punc0 = ''
        self.lower = ''
        self.punc1 = ''
        self.roman = ''

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

        self.punc0 = ''
        self.lower = ''
        self.punc1 = ''
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
        parts = (self.upper, self.number, self.punc0, self.lower, self.punc1,
                 self.roman)
        expr = ''.join(filter(None, parts))
        return expr

    def __repr__(self):
        """Return the repr of this numbering."""
        return 'Numbering("{}")'.format(str(self))

