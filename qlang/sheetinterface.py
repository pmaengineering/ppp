import xlrd

import constants

import os.path


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


class Worksheet:
    count = 0

    def __init__(self, data=None, name=None, datemode=None):
        self.data = []
        for i in range(data.nrows):
            cur_row = []
            for j, cell in enumerate(data.row(i)):
                this_value = self.cell_value(cell, datemode, unicode=True)
                cur_row.append(this_value)
            self.data.append(cur_row)

        if name is None:
            Worksheet.count += 1
            self.name = constants.DEFAULT_WS_NAME + str(Worksheet.count)
        else:
            self.name = name

    def get_columns(self):
        if self.data:
            return self.data[0]
        else:
            return []

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    @staticmethod
    def cell_value(cell, datemode=None, unicode=True):
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            if unicode:
                return 'TRUE' if cell.value == 1 else 'FALSE'
            else:
                return True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            if unicode:
                return ''
            else:
                return None
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            # Do I want to have the leading and trailing whitespace trimmed?
            s = cell.value.strip()
            return s
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            if int(cell.value) == cell.value:
                if unicode:
                    return str(int(cell.value))
                else:
                    return int(cell.value)
            else:
                if unicode:
                    return str(cell.value)
                else:
                    return cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            date_tuple = xlrd.xldate_as_tuple(cell.value, datemode)
            return '-'.join((str(x) for x in date_tuple))
        else:
            m = 'Bad cell type: {}. Value is: {}'.format(cell.ctype, cell.value)
            return m
