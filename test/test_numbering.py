"""Unit tests for numbering.py."""

import itertools
import unittest

import pmix.numbering as numbering


class NumberingFormatTest(unittest.TestCase):
    """Test the string format for fixed numberings."""

    def match_re(self, prog, expr, match):
        found = prog.match(expr)
        if match:
            msg = 'Expected "{}" to be accepted.'.format(expr)
            self.assertIsNotNone(found, msg=msg)
        else:
            msg = 'Expected "{}" not to be accepted.'.format(expr)
            self.assertIsNone(found, msg=msg)

    def test_upper_re(self):
        """Regex-ify uppercase numbering."""
        this_prog = numbering.Numbering.letter_prog
        good = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for item in good:
            self.match_re(this_prog, item, True)

        bad_single = tuple('ÁÉ01')
        other_bad = ('', 'AA', 'A1', '1A', '_', '-', 'A.', ' A', 'A ')
        for item in itertools.chain(bad_single, other_bad):
            self.match_re(this_prog, item, False)

    def test_number_re(self):
        """Regex-ify pure number numbering."""
        this_prog = numbering.Numbering.number_prog
        good = ('001', '101', '201', 'LCL_301', 'A1', 'FLW801', 'PHC105', '1')
        for item in good:
            self.match_re(this_prog, item, True)

        bad = ('', '001a', '10.', '_', '-', 'SN_101i')
        for item in bad:
            self.match_re(this_prog, item, False)

    def test_ext_letter_re(self):
        """Regex-ify extended numbering with letter."""
        this_prog = numbering.Numbering.ext_letter_prog
        good = ('001a', 'PHC101d', '101z', 'LCL_308a', 'SN_101.i')
        for item in good:
            self.match_re(this_prog, item, True)

        bad = ('001', 'A', '', '_', '-', 'PHC101.ix', '101a.', ' 101a', '1a ')
        for item in bad:
            self.match_re(this_prog, item, False)

    def test_ext_roman_re(self):
        """Regex-ify extended numbering with roman numeral."""
        this_prog = numbering.Numbering.ext_roman_prog
        good = ('1a.i', '2b.ii', '3c.iii', '4d:iv', '5e_v', '6f-vi', '7g)vii',
                '8h_viii', '9i_ix', '10j_x', '1.a.i')
        for item in good:
            self.match_re(this_prog, item, True)

        bad = ('', '_', '-', '001', 'A', '2ii', '1iiii', '25y', '1i ', ' 2ii',
               '21av')
        for item in bad:
            self.match_re(this_prog, item, False)

    def test_decompose(self):
        """Decompose numbering."""
        answers = (
            ('a', 'a', '', '', '', '', '', ''),
            ('A', 'A', '', '', '', '', '', ''),
            ('001', '', '', '001', '', '', '', ''),
            ('001a', '', '', '001', '', 'a', '', ''),
            ('001.a', '', '', '001', '.', 'a', '', ''),
            ('3a.iii', '', '', '3', '', 'a', '.', 'iii'),
            ('PHC101-i', '', 'PHC', '101', '-', 'i', '', ''),
            ('FLW801', '', 'FLW', '801', '', '', '', ''),
            ('LCL_101', '', 'LCL_', '101', '', '', '', '')
        )
        for expr, let, lead, number, p0, low, p1, rom in answers:
            msg = 'Working with "{}"'.format(expr)
            num = numbering.Numbering(expr)
            self.assertEqual(let, num.letter, msg=msg)
            self.assertEqual(lead, num.leader, msg=msg)
            self.assertEqual(number, num.number, msg=msg)
            self.assertEqual(p0, num.punc0, msg=msg)
            self.assertEqual(low, num.lower, msg=msg)
            self.assertEqual(p1, num.punc1, msg=msg)
            self.assertEqual(rom, num.roman, msg=msg)

class NumberingIncrementTest(unittest.TestCase):
    """Test numbering increments."""

    def test_naive_number_increment(self):
        """A naive test of incrementing."""
        num = numbering.Numbering('001')
        num.increment('^1')
        self.assertEqual(str(num), '002')
        num.increment('^2')
        self.assertEqual(str(num), '004')
        num.increment('^a')
        self.assertEqual(str(num), '004a')
        num.increment('^1')
        self.assertEqual(str(num), '005')
        num.increment('^1a')
        self.assertEqual(str(num), '006a')
        num.increment('^1a')
        self.assertEqual(str(num), '007a')

        num = numbering.Numbering('101')
        num.increment('^1')
        self.assertEqual(str(num), '102')

    def compare_chains(self, chains):
        """Compare commands to answers in batches."""
        for chain, answers in chains:
            context = numbering.NumberingContext()
            for cmd, answer in zip(chain, answers):
                context.next(cmd)
                num_now = context.numbers[-1].to_string()
                msg = 'Mistake on chain {}'.format(chain)
                self.assertEqual(num_now, answer, msg=msg)

    def compare_chains_entirely(self, chains):
        """Compare chains in their entirety."""
        for chain, answers in chains:
            context = numbering.NumberingContext()
            for cmd in chain:
                context.next(cmd)
            results = tuple(context.string_iter())
            self.assertEqual(results, answers)

    def test_increment_lookback(self):
        """Increment and lookback operators and their interplay."""
        chains = (
            (('001', '^1',  '^1',  '^1',  '<',   '<',   '^1a',  '^a'),
             ('001', '002', '003', '004', '004', '004', '005a', '005b')),

            (('101', '^1',  '^1',  '^1',  '<',   '<',   '^1a',  '^a'),
             ('101', '102', '103', '104', '104', '104', '105a', '105b')),

            (('101', '^1a',  '^a',   '^1',  '201', '<',   '^a',   '<' ),
             ('101', '102a', '102b', '103', '201', '201', '201a', '201a')),

            (('323a', '^a',   '<2',   '<2'),
             ('323a', '323b', '323a', '323b')),

            (('323a', '^1a',  '<2^a', '<2^a'),
             ('323a', '324a', '323b', '324b')),

            (('001a', '<^i'),
             ('001a', '001a.i')),

            (('711a.ii', '<^ai'),
             ('711a.ii', '711b.i')),
        )
        self.compare_chains(chains)

    def test_letter_increment(self):
        """Increment upper and lower case letters."""
        chains = (
            (('A', '^A', '^A'),
             ('A', 'B',  'C')),

            (('a', '^a', '^a'),
             ('a', 'b',  'c'))
        )
        self.compare_chains(chains)

    def test_all_increment(self):
        """Increment with ^1ai."""
        chains = (
            (('1', '^1ai'),
             ('1', '2a.i')),
        )
        self.compare_chains(chains)

    def test_sticky(self):
        """Sticky operator correctness."""
        chains = (
            (('PHC101', '^1',     '#LCL_301', '^1'),
             ('PHC101', 'PHC102', 'LCL_301',  'PHC103')),

            (('BF012', '^1',    '#NS012', '^1'),
             ('BF012', 'BF013', 'NS012',  'BF014')),

            (('001a', '#099', '101a'),
             ('001a', '099',  '101a'))
        )
        self.compare_chains(chains)

    def test_blanks(self):
        """Blanks mixed in with commands."""
        chains = (
            (('', '001a', '', '^1'),
             ('', '001a', '', '002')),

            (('PHC_101', '^a',       '', '#LCL_100', '', '^1'),
             ('PHC_101', 'PHC_101a', '', 'LCL_100',  '', 'PHC_102'))
        )
        self.compare_chains_entirely(chains)

    def test_silent(self):
        """Silent numbers."""
        chains = (
            (('', '~000', '^1',  '^1a'),
             ('', '',     '001', '002a')),

            (('~PHC100', '', '^1a',     '^a'),
             ('',        '', 'PHC101a', 'PHC101b'))
        )
        self.compare_chains_entirely(chains)

    def test_resume(self):
        """Resume previous series."""
        chains = (
            (('PHC101', 'a', '^a', '*^1a'),
             ('PHC101', 'a', 'b',  'PHC102a')),

            (('~000', '^1',  'a', '^a', '*<'),
             ('',     '001', 'a', 'b',  '001'))
        )
        self.compare_chains_entirely(chains)
