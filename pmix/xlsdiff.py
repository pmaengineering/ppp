import argparse
from collections import defaultdict, Counter
import difflib
from itertools import zip_longest

import pmix.utils as utils
from pmix.xlsform import Xlsform


class XlsDiff:

    def __init__(self, base, new):
        self.base = base
        self.new = new
        self.odk_diff = OdkDiff(self.base, self.new)
        self.simple_diff = SimpleDiff(self.base, self.new)

    @classmethod
    def from_file(cls, base, new):
        """Initialize XlsDiff from files.

        Creates XlsForm objects and returns their diff.

        Args:
            base (str): A path to an xlsform
            new (str): A path to an xlsform
        """
        base_xlsform = Xlsform(base, stripstr=False)
        new_xlsform = Xlsform(new, stripstr=False)
        xls_diff = cls(base_xlsform, new_xlsform)
        return xls_diff

    def swap(self):
        """Swap base and the new."""
        self.base, self.new = self.new, self.base

    def simple_diff(self):
        """Return a simple diff object."""
        this_diff = self.simple_diff_wb(self.base, self.new)
        return this_diff

    def write_simple_diff(self, path):
        """Write a simple diff of two Excel files.

        Args:
            path (str): The path to the output file
        """
        base = self.base.copy()
        new = self.new.copy()
        self.simple_diff_wb(base, new, True)
        base.write_out(path)

    @staticmethod
    def simple_diff_wb(base, new, highlight=False):
        """Return a simple diff of two workbooks."""
        simple_diff = SimpleDiff(base, new)
        for b_sheet, a_sheet in zip_longest(base, new):
            if b_sheet is None:
                simple_diff.added_sheet.append(a_sheet)
                continue
            if a_sheet is None:
                simple_diff.removed_sheet.append(b_sheet)
                if highlight:
                    cell_iter = (c for c in b_sheet.cell_iter() if not
                                 c.is_blank())
                    for cell in cell_iter:
                            cell.set_highlight()
            else:  # both a_sheet and b_sheet exist
                XlsDiff.simple_diff_ws(b_sheet, a_sheet, simple_diff,
                                       highlight)
        return simple_diff

    @staticmethod
    def simple_diff_ws(base, new, simple_diff, highlight=False):
        simple_diff.new_sheet_context(base)
        for b_row, a_row in zip_longest(base, new):
            simple_diff.context['row'] += 1
            if b_row is None:
                simple_diff.row_changed(a_row, 'added')
                continue
            if a_row is None:
                simple_diff.row_changed(b_row, 'removed')
                if highlight:
                    cell_iter = (c for c in b_row if not c.is_blank())
                    for cell in cell_iter:
                        cell.set_highlight()
            else:  # both b_row and a_row exist
                XlsDiff.simple_diff_row(b_row, a_row, simple_diff, highlight)

    @staticmethod
    def simple_diff_row(base, new, simple_diff, highlight=False):
        simple_diff.new_row_context()
        for b_cell, a_cell in zip_longest(base, new):
            simple_diff.context['col'] += 1
            if b_cell != a_cell:
                simple_diff.add_cell_diff(b_cell, a_cell)
                if b_cell is not None and highlight:
                    b_cell.set_highlight()


class OdkDiff:

    sheet_diff_row_key = {
        'survey': ['type', 'name'],
        'choices': ['list_name', 'name'],
        'external_choices': ['list_name', 'name']
    }

    def __init__(self, base, new, **kwargs):
        self.base = base
        self.new = new
        self.sheet_venn = self.sheet_comparison(base, new)

        self.sheet_diff_row_key.update(kwargs)
        common_sheets = (s[1] for s in self.sheet_venn[0])
        self.col_venn = {}
        self.row_venn = {}
        self.cell_diff = defaultdict(list)
        self.duplicate_rows = defaultdict(list)
        for sheet in common_sheets:
            base_sheet = base[sheet]
            new_sheet = new[sheet]
            this_col_comparison = self.column_comparison(base_sheet, new_sheet,
                                                         True)
            key = self.sheet_diff_row_key.get(sheet)
            this_row_comparison = self.row_comparison(base_sheet, new_sheet,
                                                      key)
            self.col_venn[sheet] = this_col_comparison
            self.row_venn[sheet] = this_row_comparison
            self.find_cell_diffs(base_sheet, new_sheet)

    def find_cell_diffs(self, base_sheet, new_sheet):
        sheet_name = base_sheet.name
        common_cols_base = self.col_venn[sheet_name][0]
        common_cols_new = self.col_venn[sheet_name][2]
        common_rows_base = self.row_venn[sheet_name][0]
        common_rows_new = self.row_venn[sheet_name][2]
        rows_base_counter = Counter(i[1] for i in common_rows_base)
        rows_new_counter = Counter(i[1] for i in common_rows_new)
        row_key_counter = rows_base_counter + rows_new_counter
        for row_ind in common_rows_base:
            if row_key_counter[row_ind[1]] > 2:
                self.duplicate_rows[sheet_name].append(row_ind)
                continue
            for col_ind in common_cols_base:
                base_cell = base_sheet[row_ind[0]][col_ind[0]]
                new_cell = new_sheet[row_ind[2]][col_ind[2]]
                if base_cell != new_cell:
                    record = (row_ind[1], col_ind[1], row_ind[0], col_ind[0],
                              base_cell, row_ind[2], col_ind[2], new_cell)
                    self.cell_diff[sheet_name].append(record)

    def report_cell_diffs(self):
        inner = '{:^20}'.format('Diff report')
        outer = '{:*^60}'.format(inner)
        print(outer)
        print('Base: {}'.format(self.base.file))
        print('New:  {}'.format(self.new.file))
        print('*'*60)
        differ = difflib.Differ()
        for sheet, cell_list in self.cell_diff.items():
            inner = '  Total diffs on "{}": {}  '.format(sheet, len(cell_list))
            outer = '{:-^60}'.format(inner)
            print(outer)
            for record in cell_list:
                base_location = record[2], record[3]
                new_location = record[5], record[6]
                print('>>> Base cell[{}] != New cell[{}]'.format(base_location,
                      new_location))
                cell1_lines = str(record[4]).splitlines()
                cell2_lines = str(record[7]).splitlines()
                diff = differ.compare(cell1_lines, cell2_lines)
                print('\n'.join(diff))
        inner = '{:^20}'.format('End diff report')
        outer = '{:*^60}'.format(inner)
        print(outer)

    @staticmethod
    def row_comparison(base, new, key=None):
        """Compare rows in two sheets by key.

        Args:
            base (Worksheet): The base worksheet
            new (Worksheet): The new worksheet
            key (seq, int, or str): The column(s) to use for determining unique
                rows
        """
        if key is None:
            base_seq = list(range(len(base)))
            new_seq = list(range(len(new)))
        else:
            base_cols = base.column_key(key)
            base_iters = tuple(base.column_str(c) for c in base_cols)
            base_seq = list(zip(*base_iters))
            new_cols = new.column_key(key)
            new_iters = tuple(new.column_str(c) for c in new_cols)
            new_seq = list(zip(*new_iters))
        return OdkDiff.sequence_venn(base_seq, new_seq)

    @staticmethod
    def column_comparison(base, new, names=False):
        """Compare two sheet columns.

        Args:
            base (Worksheet): The base worksheet
            new (Worksheet): The new worksheet
            names (bool): If true, compare on column headers, else use indices
        """
        if names:
            base_seq = base.column_headers()
            new_seq = new.column_headers()
        else:
            base_seq = list(range(base.ncol()))
            new_seq = list(range(new.ncol()))
        return OdkDiff.sequence_venn(base_seq, new_seq)


    @staticmethod
    def sheet_comparison(base, new):
        """Get the full Venn diagram of sheet names for two workbooks.

        Args:
            base (Workbook): The base workbook
            new (Workbook): The new workbook
        """
        base_names = base.sheetnames()
        new_names = new.sheetnames()
        return OdkDiff.sequence_venn(base_names, new_names)

    @staticmethod
    def sequence_venn(seq1, seq2):
        """Get the intersection and two set differences for two sequences.

        This could be visualized as a Venn Diagram.

        Args:
            seq1 (list): The first sequence
            seq2 (list): The second sequence
        """
        seq1_set = set(seq1)
        seq2_set = set(seq2)
        common = seq1_set & seq2_set
        common_seq1_sorted = []
        seq1_not_seq2_sorted = []
        for i, item in enumerate(seq1):
            record = (i, item)
            if item in common:
                seq2_ind = seq2.index(item)
                common_seq1_sorted.append((i, item, seq2_ind))
            else:
                seq1_not_seq2_sorted.append(record)
        common_seq2_sorted = []
        seq2_not_seq1_sorted = []
        for i, item in enumerate(seq2):
            record = (i, item)
            if item in common:
                common_seq2_sorted.append(record)
            else:
                seq2_not_seq1_sorted.append(record)
        return (common_seq1_sorted, seq1_not_seq2_sorted, common_seq2_sorted,
                seq2_not_seq1_sorted)



class SimpleDiff:
    # TODO: REFACTOR SIMPLEDIFF TO BE LIKE ODKDIFF
    # STORE ALL THE DIFF INFORMATION IN THIS OBJECT
    # SHEET, ROW, COLUMN comparison, then
    # CELL BY CELL comparison for what is common
    def __init__(self, base, new):
        self.base = base
        self.new = new
        self.context = {}
        self.added_sheet = []
        self.removed_sheet = []
        self.rows = {}
        self.cell_diffs = {}

    def row_changed(self, row, verb):
        sheet = self.context['sheet']
        ind = self.context['row']
        row_info = (ind, verb, row)
        if sheet.name in self.rows:
            self.rows[sheet.name].append(row_info)
        else:
            self.rows[sheet.name] = [row_info]

    def new_sheet_context(self, sheet):
        self.context = {
            'sheet': sheet,
            'row': -1,
            'col': -1
        }

    def new_row_context(self):
        self.context['col'] = -1

    def add_cell_diff(self, base, new):
        sheet = self.context['sheet']
        row = self.context['row']
        col = self.context['col']
        diff_info = (row, col, base, new)
        if sheet.name in self.cell_diffs:
            self.cell_diffs[sheet.name].append(diff_info)
        else:
            self.cell_diffs[sheet.name] = [diff_info]


def xlsdiff_cli():
    """Run the command line interface for this module."""
    prog_desc = 'Create a diff of two Excel workbooks'
    parser = argparse.ArgumentParser(description=prog_desc)
    file_help = ('Path to source XLSForm. Two must be supplied. The first is '
                 'treated as the base, the second is treated as the new file.')
    parser.add_argument('xlsxfile', help=file_help, nargs=2)
    reverse_help = 'Reverse the base file and the new file for processing.'
    parser.add_argument('-r', '--reverse', action='store_true',
                        help=reverse_help)
    simple_help = 'Do a simple diff instead of the default ODK diff.'
    parser.add_argument('-s', '--simple', action='store_true')
    out_help = ('Path to write Excel output. If flag is given with no '
                'argument then default out path is used. If flag is omitted, '
                'then write text output to STDOUT.')
    parser.add_argument('-e', '--excel', help=out_help, nargs='?', const=0)
    args = parser.parse_args()
    file1, file2 = args.xlsxfile
    if args.reverse:
        file1, file2 = file2, file1
    if args.simple:
        # Make a simple diff output
        if args.excel is None:
            # Write to console
            pass
        elif isinstance(args.excel, str):
            # Write excel to this path
            pass
        else:
            # Write to default excel path
            pass
    else:
        # Make an ODK diff output
        if args.excel is None:
            # Write to console
            pass
        elif isinstance(args.excel, str):
            # Write excel to this path
            pass
        else:
            # Write to default excel path
            pass
    diff = XlsDiff.from_file(file1, file2)
    diff.odk_diff.report_cell_diffs()


if __name__ == '__main__':
    xlsdiff_cli()
