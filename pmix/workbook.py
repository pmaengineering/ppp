"""Module defines a Workbook class to represent Excel files."""

import itertools
import copy
import os.path
import argparse

import xlrd
import xlsxwriter

import pmix.utils as utils
import pmix.wbformat as wbformat
from pmix.worksheet import Worksheet


class Workbook:
    """Class to represent an Excel file."""

    def __init__(self, path, stripstr=True):
        """Initialize by storing data from spreadsheet.

        Args:
            path (str): The path where to find the Excel file
            stripstr (bool): Remove trailing / leading whitespace from text?
        """
        self.file = path
        self.data = []

        ext = os.path.splitext(path)[1]
        if ext in ('.xls', '.xlsx'):
            self.data = self.data_from_excel(path, stripstr)
        else:
            msg = 'Unsupported file type. Extension: "{}"'.format(ext)
            raise TypeError(msg)

    def sheetnames(self):
        """Get sheetnames from this Workbook.

        Returns:
            A tuple of string, in the order of the sheets.
        """
        return tuple(sheet.name for sheet in self)

    @staticmethod
    def init_formats(wb):
        """Add formats to workbook and return those formats.

        Currently, only highlighting is supported. Therefore, all highlight
        colors are added, regardless of whether or not they are used.

        However, in the future, more complex formatting may be supported, so
        searching the contents of the this object may become necessary to
        find the formats.

        Args:
            wb (xlsxwriter.Workbook): The workbook to write to

        Returns:
            A dictionary with colors as keys and formats as values

        Todo:
            If more complicated formats are used, then make a FormatManager
            that can look up formats based on what is stored in the Cell obj.
        """
        formats = {}
        for k, v in wbformat.HL_COLORS.items():
            this_format = wb.add_format({'bg_color': v})
            formats[k] = this_format
        return formats

    def cell_iter(self):
        """Iterate over the cells of the workbook."""
        sheet_iters = [sheet.cell_iter() for sheet in self]
        return itertools.chain(*sheet_iters)

    def write_out(self, path, strings=False):
        """Write this Workbook out to file.

        Args:
            path (str): The path where to write the Excel file
            strings (bool): False if the original value should be written,
                otherwise the string value of the cell is used.
        """
        wb = xlsxwriter.Workbook(path)
        formats = self.init_formats(wb)
        for worksheet in self.data:
            ws = wb.add_worksheet(worksheet.name)
            for i, line in enumerate(worksheet):
                for j, cell in enumerate(line):
                    this_value = str(cell) if strings else cell.value
                    # TODO: If more complicated formats, then use a lookup
                    if cell.highlight is None:
                        this_format = None
                    else:
                        this_format = formats[cell.highlight]
                    # END TODO
                    if this_format is None:
                        ws.write(i, j, this_value)
                    else:
                        ws.write(i, j, this_value, this_format)

    def copy(self):
        """Make a deep copy of this workbook."""
        return copy.deepcopy(self)

    @staticmethod
    def data_from_excel(path, stripstr=True):
        """Get data from Excel through xlrd.

        Args:
            path (str): The path where to find the Excel file.
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            A list of worksheets, matching the source Excel file.
        """
        result = []
        with xlrd.open_workbook(path) as book:
            datemode = book.datemode
            for i in range(book.nsheets):
                ws = book.sheet_by_index(i)
                my_ws = Worksheet.from_sheet(ws, datemode, stripstr)
                result.append(my_ws)
        return result

    def __len__(self):
        """Return the number of sheets in this workbook."""
        return len(self.data)

    def __iter__(self):
        """Return an iter of the sheets."""
        return iter(self.data)

    def __getitem__(self, key):
        """Get a worksheet from a workbook.

        Args:
            key: Match by index if key is int, match by sheet name if key is
            str.

        Returns:
            The found worksheet is returned.

        Raises:
            IndexError: Supplied int is out of range
            KeyError: Supplied str does not match a worksheet name
            TypeError: If key is neither str nor int
        """
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str):
            for sheet in self:
                if sheet.name == key:
                    return sheet
            raise KeyError(key)
        else:
            raise TypeError(key)


def remove_extra_whitespace(inpath, outpath):
    """Remove trailing and leading whitespace of newlines and text.

    Args:
        inpath (str): The path where to find the source file.
        outpath (str): The path where to write the new xlsxfile.
    """
    wb = Workbook(inpath, stripstr=False)
    for cell in wb.cell_iter():
        old_value = str(cell)
        new_value = utils.clean_string(old_value)
        if old_value != new_value:
            cell.value = new_value
            cell.highlight = 'HL_YELLOW'
    wb.write_out(outpath)


def write_sheet_to_csv(inpath, outpath, sheet=0):
    """Write a worksheet of a workbook to CSV.

    Args:
        inpath (str): The path where to find the source file.
        outpath (str): The path where to write the CSV
        sheet (str): Which sheet to write as CSV. Defaults to 0 for the first
            sheet
    """
    wb = Workbook(inpath)
    ws = wb[sheet]
    ws.to_csv(outpath)


def workbook_cli():
    """Run the command line interface for this module."""
    prog_desc = 'Utilities for workbooks, depending on the options provided'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source workbook.'
    parser.add_argument('xlsxfile', help=file_help)

    ws_help = ('Remove trailing and leading whitespace of text and newlines.')
    parser.add_argument('-w', '--whitespace', help=ws_help,
                        action='store_true')

    csv_help = ('Write a worksheet to CSV. Supply the worksheet name here.')
    parser.add_argument('-c', '--csv', help=csv_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    if args.whitespace:
        filename, extension = os.path.splitext(args.xlsxfile)
        if args.outpath is None:
            outpath = os.path.join(filename+'-rmws'+extension)
        else:
            outpath = args.outpath
        remove_extra_whitespace(args.xlsxfile, outpath)
        print('Cleaned whitespace and wrote file to "{}"'.format(outpath))
    elif args.csv is not None:
        base = os.path.split(args.xlsxfile)[0]
        sheet_name = args.csv
        if args.outpath is not None:
            outpath = args.outpath
        elif sheet_name.endswith('.csv'):
            outpath = os.path.join(base, sheet_name)
        else:
            outpath = os.path.join(base, sheet_name + '.csv')

        write_sheet_to_csv(args.xlsxfile, outpath, args.csv)
        print('Wrote csv file to "{}"'.format(outpath))


if __name__ == '__main__':
    workbook_cli()
