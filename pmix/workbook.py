import os.path

import xlrd
import xlsxwriter

from verbiage import TranslationDict
from worksheet import Worksheet
import constants


class Workbook:

    def __init__(self, file):
        self.file = file
        self.data = []

        ext = os.path.splitext(file)[1]
        if ext in ('.xls', '.xlsx'):
            self.data = self.data_from_excel(file)
        else:
            raise TypeError(file)

    def get_sheetnames(self):
        return tuple(sheet.name for sheet in self)

    def merge_translations(self, translations):
        for sheet in self:
            sheet.merge_translations(translations)

    def create_translation_dict(self):
        result = TranslationDict()
        for sheet in self:
            this_result = sheet.create_translation_dict()
            result.update(this_result)
        return result

    def write_out(self, path):
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
            sheetnames = self.get_sheetnames()
            try:
                ind = sheetnames.index(key)
                value = self.data[ind]
                return value
            except ValueError:
                raise KeyError(key)

    @staticmethod
    def data_from_excel(file):
        result = []
        with xlrd.open_workbook(file) as book:
            datemode = book.datemode
            for i in range(book.nsheets):
                ws = book.sheet_by_index(i)
                ws_name = ws.name
                my_ws = Worksheet(data=ws, name=ws_name, datemode=datemode)
                result.append(my_ws)
        return result
