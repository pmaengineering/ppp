"""
File to compare differences between two spreadsheets

A compared to B

List matching sheet names
List extra sheet names in A
List extra sheet names in B

Example

A: sheet1, sheet2, sheet3
B: sheet4, sheet5
AB: survey, choices, settings




Match by column name and row key (name + type)
-----> Generic would choose the column(s) that make a key

A compared to B scenarios

## Missingness
A has extra columns
B has extra columns
A has extra rows (keys)
B has extra rows (keys)
---> should allow key renames

## Matches (skip column(s) used for key)
A[x,y] != B[x,y]
---> Do nothing
---> copy A to B
---> copy B to A
---> (if copy, mark other columns for translation, e.g. label)


Example

select_one choose|best_thing, label::English
>> A[D10]
The best there ever was
==
The best there ever were
<< B[D10]


"""

import sheetinterface
import utils
import error

import collections


class Comparator:

    def __init__(self, workbook1, workbook2):
        self.A = workbook1
        self.B = workbook2

    def __str__(self):
        m = 'A: "{}"\nB: "{}"'.format(self.A.file, self.B.file)
        return m

    def compare_sheetnames(self):
        a_sheetnames = self.A.get_sheetnames()
        b_sheetnames = self.B.get_sheetnames()

        only_a = [name for name in a_sheetnames if name not in b_sheetnames]
        only_b = [name for name in b_sheetnames if name not in a_sheetnames]
        both_ab = [name for name in a_sheetnames if name in b_sheetnames]

        print("*** Sheetnames comparison ***")
        if only_a:
            print("A \ B: " + ", ".join(only_a))
        if only_b:
            print("B \ A: " + ", ".join(only_b))
        if both_ab:
            print("A \u2229 B: " + ", ".join(both_ab))
        print()

    def compare_sheet_by_name(self, sheetname, key):
        a_sheet = self.A[sheetname]
        b_sheet = self.B[sheetname]

        # Show columns in A not in B
        # Show columns in B not in A
        # Show columns in both A and B
        # Headings must exist and be unique
        shared_columns = self.compare_columns(a_sheet, b_sheet)

        # Key col must exist in A and B
        # Key col can be tuple of int for column numbers
        # Key col can be tuple of string for column headings

        # Show keys in A not in B
        # Show keys in B not in A
        # Go through one by one the keys in both A and B
        # Key must be unique in spreadsheet
        shared_keys = self.compare_keys(a_sheet, b_sheet, key)

        self.compare_cells(a_sheet, b_sheet, shared_keys, shared_columns)


    @staticmethod
    def compare_cells(a_sheet, b_sheet, shared_keys, shared_columns):
        print("*** Cell comparison")
        diff_count = 0
        for k, ak, bk in shared_keys:
            a_row = a_sheet[ak]
            b_row = b_sheet[bk]
            for c, ac, bc in shared_columns:
                a_cell = a_row[ac]
                b_cell = b_row[bc]
                if a_cell != b_cell:
                    diff_count += 1
                    print("{}, {}".format("|".join(k), c))
                    a_loc = ">> A!{}[{}{}]"
                    a_col_xl = utils.number_to_excel_column(ac)
                    a_row_xl = str(ak + 1)
                    a_loc = a_loc.format(a_sheet.name, a_col_xl, a_row_xl)
                    print(a_loc)
                    print('"{}"'.format(a_cell))
                    print("==")
                    print('"{}"'.format(b_cell))
                    b_loc = "<< B!{}[{}{}]"
                    b_col_xl = utils.number_to_excel_column(bc)
                    b_row_xl = str(bk + 1)
                    b_loc = b_loc.format(b_sheet.name, b_col_xl, b_row_xl)
                    print(b_loc)
                    print()
        print("Total cell differences found: {}".format(diff_count))

    @staticmethod
    def compare_keys(a_sheet, b_sheet, key):
        a_columns = a_sheet.get_columns()
        b_columns = b_sheet.get_columns()

        a_inds = [k if isinstance(k, int) else a_columns.index(k) for k in key]
        b_inds = [k if isinstance(k, int) else b_columns.index(k) for k in key]

        a_keys = [tuple(row[i] for i in a_inds) for row in a_sheet]
        b_keys = [tuple(row[i] for i in b_inds) for row in b_sheet]

        a_duplicates = [v for v, c in collections.Counter(a_keys).items()
                        if c > 1]
        b_duplicates = [v for v, c in collections.Counter(b_keys).items()
                        if c > 1]

        print("*** Row key comparison ***")

        if a_duplicates:
            m = "A duplicate row keys: {}"
            m = m.format(", ".join(("|".join(v) for v in a_duplicates)))
            print(m)

        if b_duplicates:
            m = "B duplicate row keys: {}"
            m = m.format(", ".join(("|".join(v) for v in b_duplicates)))
            print(m)

        only_a = [name for name in a_keys if name not in b_keys]
        only_b = [name for name in b_keys if name not in a_keys]
        both_ab = [name for name in a_keys if name in b_keys]


        if only_a:
            print("A \ B: " + ", ".join(("|".join(v) for v in only_a)))
        if only_b:
            print("B \ A: " + ", ".join(("|".join(v) for v in only_b)))
        if both_ab:
            print("A \u2229 B: " + ", ".join(("|".join(v) for v in both_ab)))
        print()

        shared_ab = [(item, a_keys.index(item), b_keys.index(item)) for item in
                     both_ab]
        return shared_ab

    @staticmethod
    def compare_columns(a_sheet, b_sheet):
        a_columns = a_sheet.get_columns()
        b_columns = b_sheet.get_columns()

        for i, col in enumerate(a_columns):
            if col == '' or col is None:
                col = utils.number_to_excel_column(i)
                row = "1"
                m = 'A!{}[{}{}] has empty heading cell'
                m = m.format(a_sheet.name, col, row)
                raise error.ComparatorError(m)

        for i, col in enumerate(b_columns):
            if col == '' or col is None:
                col = utils.number_to_excel_column(i)
                row = "1"
                m = 'B!{}[{}{}] has empty heading cell'
                m = m.format(b_sheet.name, col, row)
                raise error.ComparatorError(m)

        a_duplicates = [v for v, c in collections.Counter(a_columns).items()
                        if c > 1]
        b_duplicates = [v for v, c in collections.Counter(b_columns).items()
                        if c > 1]
        if a_duplicates:
            m = "A duplicate columns: {}"
            m = m.format(", ".join(a_duplicates))
            raise error.ComparatorError(m)

        if b_duplicates:
            m = "B duplicate columns: {}"
            m = m.format(", ".join(b_duplicates))
            raise error.ComparatorError(m)

        only_a = [name for name in a_columns if name not in b_columns]
        only_b = [name for name in b_columns if name not in a_columns]
        both_ab = [name for name in a_columns if name in b_columns]

        print("*** Columns comparison ***")
        if only_a:
            print("A \ B: " + ", ".join(only_a))
        if only_b:
            print("B \ A: " + ", ".join(only_b))
        if both_ab:
            print("A \u2229 B: " + ", ".join(both_ab))
        print()

        shared_ab = [(item, a_columns.index(item), b_columns.index(item)) for
                     item in both_ab]
        return shared_ab


if __name__ == '__main__':
    files = [
        'test/files/GHR5-Household-Questionnaire-v12-jkp.xlsx',
        'test/files/IDR2-Household-Questionnaire-v5-jkp.xlsx'
    ]
    wb1 = sheetinterface.Workbook(files[0])
    wb2 = sheetinterface.Workbook(files[1])
    c = Comparator(wb1, wb2)
    print(c)
    c.compare_sheetnames()
    c.compare_sheet_by_name("survey", key=("type", "name"))
