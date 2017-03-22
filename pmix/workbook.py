"""This module defines a Workbook class to represent Excel files"""

import os.path
import argparse

import xlrd
import xlsxwriter

from pmix import constants
from pmix.worksheet import Worksheet


class Workbook:
    """Class to represent an Excel file"""

    def __init__(self, file):
        """Initialize by storing data from spreadsheet"""
        self.file = file
        self.data = []

        ext = os.path.splitext(file)[1]
        if ext in ('.xls', '.xlsx'):
            self.data = self.data_from_excel(file)
        else:
            raise TypeError(file)

    def sheetnames(self):
        """Get sheetnames from this Workbook"""
        return tuple(sheet.name for sheet in self)

    def write_out(self, path):
        """Write this Workbook out to file"""
        wb = xlsxwriter.Workbook(path)
        formats = {}
        for worksheet in self.data:
            ws = wb.add_worksheet(worksheet.name)
            for i, line in enumerate(worksheet):
                ws.write_row(i, 0, line)
            for s in worksheet.style:
                bg_color = s[constants.BG_COLOR_KEY]
                if bg_color not in formats:
                    this_format = wb.add_format({constants.BG_COLOR_KEY: bg_color})
                    formats[bg_color] = this_format
            for s in worksheet.style:
                row, col = s[constants.LOCATION]
                text = s[constants.TEXT]
                this_format = formats[s[constants.BG_COLOR_KEY]]
                ws.write(row, col, text, this_format)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str):
            for sheet in self:
                if sheet.name == key:
                    return sheet
            else:
                raise KeyError(key)
        else:
            raise KeyError(key)

    @staticmethod
    def data_from_excel(file):
        """Get data from Excel through xlrd"""
        result = []
        with xlrd.open_workbook(file) as book:
            datemode = book.datemode
            for i in range(book.nsheets):
                ws = book.sheet_by_index(i)
                my_ws = Worksheet(ws, datemode)
                result.append(my_ws)
        return result


def write_sheet_to_csv(inpath, outpath, sheet):
    """Write a worksheet of a workbook to CSV"""
    wb = Workbook(inpath)
    ws = wb[sheet]
    ws.to_csv(outpath)


if __name__ == '__main__':
    prog_desc = 'Utilities for workbooks, depending on the options provided'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForms containing translations.'
    parser.add_argument('xlsxfile', help=file_help)

    csv_help = ('Write a worksheet to CSV. Supply the worksheet name here.')
    parser.add_argument('-c', '--csv', help=csv_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    if args.csv is not None:
        base = os.path.split(args.xlsxfile)[0]
        sheet_name = args.csv
        if args.outpath is not None:
            outpath = args.outpath
        elif sheet_name.endswith(constants.CSV_EXT):
            outpath = os.path.join(base, sheet_name)
        else:
            outpath = os.path.join(base, sheet_name + constants.CSV_EXT)

        write_sheet_to_csv(args.xlsxfile, outpath, args.csv)
        print('Wrote csv file to "{}"'.format(outpath))
