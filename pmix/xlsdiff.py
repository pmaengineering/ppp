"""Module for the xls diffing and CLI.

IndexedVenn
    This is a named tuple that is meant to carry information about two
    sequences (called "a" and "b"). It has the following ordered members:
        - common_a: The index and item of all items in both a and b with the
            condition that the item appears exactly once in both. It preserves
            the order of what is in a.
        - common_a_dup: The index and item of all items in both a and b with
            the condition the item appears more than once in either a or b. It
            preserves the order of what is in a.
        - a_not_b: The index and item of all items in a that are not in b. It
            preserves the order of what is in a.
        - a_to_b: A map of indices from items in common_a to common_b.
        - common_b: Same as common_a but a and b reversed.
        - common_b_dup: Same as common_a_dup but a and b reversed.
        - b_not_a: Same as a_not_b but a and b reversed.
        - b_to_a: Same as a_to_b but a and b reversed.

CellDiff
    This is a named tuple with information about cell differences between
    workbook "a" and "b".
        - cell_a: The cell in a
        - cell_b: The cell in b
        - row_a: The row number in a
        - col_a: The column number in a
        - row_b: The row number in b
        - col_b: The col number in b
        - row_key: The key for the row, e.g. name and type
        - col_key: The key for the column, e.g. column header
"""
import argparse
from collections import defaultdict, Counter, namedtuple
import difflib
import os.path

import pmix.utils as utils
import pmix.workbook


CellDiff = namedtuple('CellDiff', ['cell_a', 'cell_b', 'row_a', 'col_a',
                                   'row_b', 'col_b', 'row_key', 'col_key'])


IndexedVenn = namedtuple('IndexedVenn', ['common_a', 'common_a_dup', 'a_not_b',
                                         'a_to_b', 'common_b', 'common_b_dup',
                                         'b_not_a', 'b_to_a'])


def indexed_venn(seq1, seq2):
    """Get the intersection and two set differences for two lists.

    This could be visualized as a Venn Diagram.

    First what is common between the two lists is determined. Then various
    lists are created.

    The items in the input sequences must be hashable, since they are counted
    and retrieved via list.index().

    Args:
        seq1 (list): The first sequence
        seq2 (list): The second sequence

    Returns:
        IndexedVenn named tuple.
    """
    seq1_set = set(seq1)
    seq2_set = set(seq2)
    common = seq1_set & seq2_set
    counted = Counter(seq1) + Counter(seq2)

    def build_indexed_a_b(seq_a, seq_b):
        """Build up indexed components for IndexedVenn."""
        common_a = []
        common_a_dup = []
        a_not_b = []
        a_to_b = {}
        for i, item in enumerate(seq_a):
            if item in common:
                appearance_count = counted[item]
                if appearance_count > 2:
                    common_a_dup.append((i, item))
                else:
                    common_a.append((i, item))
                    seq_b_ind = seq_b.index(item)
                    a_to_b[i] = seq_b_ind
            else:
                a_not_b.append((i, item))
        return common_a, common_a_dup, a_not_b, a_to_b
    seq_1_info = build_indexed_a_b(seq1, seq2)
    seq_2_info = build_indexed_a_b(seq2, seq1)

    return IndexedVenn(*seq_1_info, *seq_2_info)


class XlsDiff:
    """A class to represent a difference between two Excel workbooks.

    Class attributes:
        sheet_diff_key (dict): A dictionary of sheet names to lists of column
            headers. The column headers are what are combined to make unique
            row identifiers for those rows.

    Instance attributes:
        base (Workbook): The base workbook
        new (Workbook): The new workbook
        simple (bool): True if this should be a simple diff
        sheet_venn (IndexedVenn): The Venn diagram of sheetnames
        col_venn (dict): Keys are sheetnames. Values are Venn diagrams of
            columns in a given sheet
        row_venn (dict): Keys are sheetnames. Values are Venn diagrams of
            rows in a given sheet
        cell_diff (dict): Keys are sheetnames. Values are individual cell
            differences between cells sharing the same row, col, and sheet.
    """

    sheet_diff_key = {
        'survey': ['type', 'name'],
        'choices': ['list_name', 'name'],
        'external_choices': ['list_name', 'name']
    }

    def __init__(self, base, new, simple=True, **kwargs):
        """Initialize a diff between worksheets.

        Args:
            base (Workbook): The base workbook
            new (Workbook): The new workbook
            simple (bool): True if this should be a simple diff
            **kwargs: Anything in kwargs updates the sheet_diff_key map
        """
        self.base = base
        self.new = new
        self.simple = simple
        self.sheet_diff_key.update(kwargs)

        self.sheet_venn = self.sheet_comparison(base, new)
        common_sheets = (s[1] for s in self.sheet_venn.common_a)
        self.col_venn = {}
        self.row_venn = {}
        self.cell_diff = defaultdict(list)
        for sheet in common_sheets:
            base_sheet = base[sheet]
            new_sheet = new[sheet]
            col_venn = self.column_comparison(base_sheet, new_sheet, simple)
            self.col_venn[sheet] = col_venn
            key = None if simple else self.sheet_diff_key.get(sheet)
            row_venn = self.row_comparison(base_sheet, new_sheet, key)
            self.row_venn[sheet] = row_venn
            self._find_cell_diffs(base_sheet, new_sheet)

    @classmethod
    def from_file(cls, base, new, simple, **kwargs):
        """Initialize XlsDiff from files.

        Creates XlsForm objects and returns their diff.

        Args:
            base (str): A path to an xlsform
            new (str): A path to an xlsform
            simple (bool): True if this should be a simple diff
            **kwargs: Anything in kwargs updates the sheet_diff_key map
        """
        base_xlsform = pmix.workbook.Workbook(base, stripstr=False)
        new_xlsform = pmix.workbook.Workbook(new, stripstr=False)
        xls_diff = cls(base_xlsform, new_xlsform, simple, **kwargs)
        return xls_diff

    def swap(self):
        """Swap base and the new.

        Returns:
            A new XlsDiff object with the two workbooks swapped.
        """
        return XlsDiff(self.new, self.base, self.simple, **self.sheet_diff_key)

    def copy(self):
        """Get a diff of copies of the original workbooks.

        Returns:
            A new XlsDiff object with copies of the two original workbooks.
        """
        base_copy = self.base.copy()
        new_copy = self.new.copy()
        return XlsDiff(base_copy, new_copy, self.simple, **self.sheet_diff_key)

    @staticmethod
    def sheet_comparison(base, new):
        """Get the full Venn diagram of sheet names for two workbooks.

        Args:
            base (Workbook): The base workbook
            new (Workbook): The new workbook
        """
        base_names = base.sheetnames()
        new_names = new.sheetnames()
        return indexed_venn(base_names, new_names)

    @staticmethod
    def column_comparison(base, new, ind=True):
        """Compare two sheet columns.

        A simple comparison should compare on column indices.

        Args:
            base (Worksheet): The base worksheet
            new (Worksheet): The new worksheet
            ind (bool): If true, compare on column headers, else use indices
        """
        if ind:
            base_seq = list(range(base.ncol()))
            new_seq = list(range(new.ncol()))
        else:
            base_seq = base.column_headers()
            new_seq = new.column_headers()
        return indexed_venn(base_seq, new_seq)

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
        return indexed_venn(base_seq, new_seq)

    def _find_cell_diffs(self, base_sheet, new_sheet):
        """Find cell differences between two sheets.

        Pre-condition: Column and row comparisons should have been performed
        first. These should be saved in the instance variables row_venn and
        col_venn.

        Args:
            base_sheet (Worksheet): The base worksheet
            new_sheet (Worksheet): The new worksheet
        """
        sheet_name = base_sheet.name
        common_rows_base = self.row_venn[sheet_name].common_a
        common_cols_base = self.col_venn[sheet_name].common_a
        rows_base_to_new = self.row_venn[sheet_name].a_to_b
        cols_base_to_new = self.col_venn[sheet_name].a_to_b
        for row in common_rows_base:
            for col in common_cols_base:
                base_cell = base_sheet[row[0]][col[0]]
                new_row = rows_base_to_new[row[0]]
                new_col = cols_base_to_new[col[0]]
                new_cell = new_sheet[new_row][new_col]
                if base_cell != new_cell:
                    record = CellDiff(base_cell, new_cell, row[0], col[0],
                                      new_row, new_col, row[1], col[1])
                    self.cell_diff[sheet_name].append(record)

    def write_diff_new(self, path, copy=False):
        """Highlight the differences on the new spreadsheet and write out.

        The higlighting is as follows:
            - Orange shows columns and rows that are added
            - Red shows columns and rows that are duplicated based on key
            - Green shows columns and rows that are out of order
            - Yellow shows cells that are different from common rows and cols

        Args:
            path (str): The path to the output file
            copy (bool): Make a copy of the files first? Highlighting modifies
                the original workbook
        """
        if copy:
            self = self.copy()
        self._highlight_cols_new()
        self._highlight_rows_new()
        self._highlight_cell_diffs_new()
        self.new.write_out(path)

    def _highlight_cols_new(self):
        """Highlight duplicate and new columns."""
        for sheet, venn in self.col_venn.items():
            for col in venn.b_not_a:
                for cell in self.new[sheet].column(col[0]):
                    cell.set_highlight('HL_ORANGE')
            for col in venn.common_b_dup:
                for cell in self.new[sheet].column(col[0]):
                    cell.set_highlight('HL_RED')

    def _highlight_rows_new(self):
        """Highlight duplicate, mis-ordered, and new rows."""
        for sheet, venn in self.row_venn.items():
            for row in venn.b_not_a:
                for cell in self.new[sheet][row[0]]:
                    cell.set_highlight('HL_ORANGE')
            for row in venn.common_b_dup:
                for cell in self.new[sheet][row[0]]:
                    cell.set_highlight('HL_RED')
            mapping = sorted((k, v) for (k, v) in venn.a_to_b.items())
            old = 0
            for ind in (a_to_b[1] for a_to_b in mapping):
                if ind < old:
                    for cell in self.new[sheet][ind]:
                        cell.set_highlight('HL_GREEN')
                old = ind

    def _highlight_cell_diffs_new(self):
        """Highlight cell differences."""
        for _, diffs in self.cell_diff.items():
            for cell_diff in diffs:
                cell_diff.cell_b.set_highlight()

    def report_overview(self):
        """Report an overview of the differences based on indexed Venns."""
        inner = '{:^20}'.format('Overview of diff')
        outer = '{:*^60}'.format(inner)
        print(outer)
        print('Base: {}'.format(self.base.file))
        print('New:  {}'.format(self.new.file))
        print('*'*60)
        msg = 'Sheets: {} in common, {} in base not new, {} in new not base'
        common = len(self.sheet_venn.common_b)
        common_dup = len(self.sheet_venn.common_b_dup)
        a_not_b = len(self.sheet_venn.a_not_b)
        b_not_a = len(self.sheet_venn.b_not_a)
        msg = msg.format(common + common_dup, a_not_b, b_not_a)
        print(msg)
        for sheet in (i[1] for i in self.sheet_venn.common_b):
            print(' ---')
            self.report_sheet_overview(sheet)

    def report_sheet_overview(self, sheetname):
        """Report an overview for the differences in a single sheet.

        Args:
            sheetname (str): The name of the sheet to report on. Should be a
                common sheet name between the base and the new workbook.
        """
        msg = ('Sheet "{}" columns: {} in common, {} duplicated, {} in base '
               'not new, {} in new not base')
        common = len(self.col_venn[sheetname].common_b)
        dup = len(self.col_venn[sheetname].common_b_dup)
        a_not_b = len(self.col_venn[sheetname].a_not_b)
        b_not_a = len(self.col_venn[sheetname].b_not_a)
        msg = msg.format(sheetname, common, dup, a_not_b, b_not_a)
        print(msg)
        msg = ('Sheet "{}" rows: {} in common, {} duplicated, {} in base '
               'not new, {} in new not base')
        common = len(self.row_venn[sheetname].common_b)
        dup = len(self.row_venn[sheetname].common_b_dup)
        a_not_b = len(self.row_venn[sheetname].a_not_b)
        b_not_a = len(self.row_venn[sheetname].b_not_a)
        msg = msg.format(sheetname, common, dup, a_not_b, b_not_a)
        print(msg)
        msg = 'Sheet "{}" count of cell differences: {}'
        msg = msg.format(sheetname, len(self.cell_diff[sheetname]))
        print(msg)

    def report_cell_diffs(self):
        """Report cell differences."""
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
                base_row = record.row_a + 1
                base_col = utils.number_to_excel_column(record.col_a)
                new_row = record.row_b + 1
                new_col = utils.number_to_excel_column(record.col_b)
                msg = '>>> Base[{}{}] != New[{}{}]'
                msg = msg.format(base_col, base_row, new_col, new_row)
                print(msg)
                cell1_lines = str(record.cell_a).splitlines()
                cell2_lines = str(record.cell_b).splitlines()
                diff = differ.compare(cell1_lines, cell2_lines)
                print('\n'.join(diff))
        inner = '{:^20}'.format('End diff report')
        outer = '{:*^60}'.format(inner)
        print(outer)


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
    parser.add_argument('-s', '--simple', action='store_true',
                        help=simple_help)
    out_help = ('Path to write Excel output. If flag is given with no '
                'argument then default out path is used. If flag is omitted, '
                'then write text output to STDOUT.')
    parser.add_argument('-e', '--excel', help=out_help, nargs='?', const=0)
    args = parser.parse_args()
    file1, file2 = args.xlsxfile
    if args.reverse:
        file1, file2 = file2, file1
    diff = XlsDiff.from_file(file1, file2, args.simple)
    diff.report_overview()
    if args.excel is None:
        diff.report_cell_diffs()
    elif isinstance(args.excel, str):
        diff.write_diff_new(args.excel)
    else:
        filename, extension = os.path.splitext(file2)
        outpath = os.path.join(filename+'-diff'+extension)
        diff.write_diff_new(outpath)


if __name__ == '__main__':
    xlsdiff_cli()
