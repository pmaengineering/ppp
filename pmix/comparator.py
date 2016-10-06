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

import workbook
import utils
import error

import xlsxwriter

import os.path
import collections


class Comparator:

    def __init__(self, workbook1, workbook2):
        self.A = workbook1
        self.B = workbook2
        self.a_diffs = dict()
        self.b_diffs = dict()

    def accept_difference(self, sheetname, difference):
        if difference.accept_to_a:
            if sheetname in self.a_diffs:
                self.a_diffs[sheetname].append(difference)
            else:
                self.a_diffs[sheetname] = [difference]
        if difference.accept_to_b:
            if sheetname in self.b_diffs:
                self.b_diffs[sheetname].append(difference)
            else:
                self.b_diffs[sheetname] = [difference]

    def __str__(self):
        m = 'A: "{}"\nB: "{}"'.format(self.A.file, self.B.file)
        return m

    def write_out_excel(self, suffix=None, prefix=None):
        if self.a_diffs:
            a_source = self.A.file
            base, f = os.path.split(a_source)
            name, ext = os.path.splitext(f)
            new_name = "{}{}{}{}".format("" if prefix is None else prefix,
                                         name,
                                         "" if suffix is None else suffix,
                                         ext)
            a_dest = os.path.join(base, new_name)
            wb = xlsxwriter.Workbook(a_dest)
            red_background = wb.add_format({'bg_color': '#FFC7CE'})
            yellow_highlight = wb.add_format({'bg_color': '#FFFBCC'})
            for ws in self.A:
                out_ws = wb.add_worksheet(ws.name)
                utils.write_out_worksheet(out_ws, ws)
                if ws.name in self.a_diffs:
                    for diff in self.a_diffs[ws.name]:
                        if diff.highlight:
                            out_ws.write(diff.a_loc[0], diff.a_loc[1], diff.b_cell,
                                     yellow_highlight)
                        else:
                            out_ws.write(diff.a_loc[0], diff.a_loc[1], diff.b_cell)
            wb.close()
            print('Successfully created: "{}"'.format(a_dest))

        if self.b_diffs:
            b_source = self.B.file
            base, f = os.path.split(b_source)
            name, ext = os.path.splitext(f)
            new_name = "{}{}{}{}".format("" if prefix is None else prefix,
                                         name,
                                         "" if suffix is None else suffix,
                                         ext)
            b_dest = os.path.join(base, new_name)
            wb = xlsxwriter.Workbook(b_dest)
            red_background = wb.add_format({'bg_color': '#FFC7CE'})
            yellow_highlight = wb.add_format({'bg_color': '#FFFBCC'})
            for ws in self.B:
                out_ws = wb.add_worksheet(ws.name)
                utils.write_out_worksheet(out_ws, ws)
                if ws.name in self.b_diffs:
                    for diff in self.b_diffs[ws.name]:
                        if diff.highlight:
                            ws.write(diff.b_loc[0], diff.b_loc[1], diff.a_cell,
                                     yellow_highlight)
                        else:
                            ws.write(diff.b_loc[0], diff.b_loc[1], diff.a_cell)
            wb.close()
            print('Successfully created: "{}"'.format(b_dest))

    @staticmethod
    def get_set_pieces(a, b):
        to_return = {
            "only_a": [val for val in a if val not in b],
            "only_b": [val for val in b if val not in a],
            "both_ab": [val for val in a if val in b]
        }
        return to_return

    def get_sheetname_pieces(self):
        a_sheetnames = self.A.get_sheetnames()
        b_sheetnames = self.B.get_sheetnames()
        d = self.get_set_pieces(a_sheetnames, b_sheetnames)
        return d

    def report_sheetname_pieces(self):
        d = self.get_sheetname_pieces()
        only_a = d["only_a"]
        only_b = d["only_b"]
        both_ab = d["both_ab"]
        print(utils.format_header("Sheet comparison"))
        if only_a:
            print("A \ B: " + ", ".join(only_a))
        if only_b:
            print("B \ A: " + ", ".join(only_b))
        if both_ab:
            print("A \u2229 B: " + ", ".join(both_ab))
        print()
        return both_ab

    @staticmethod
    def column_checks(a_sheet, b_sheet, a_columns, b_columns):
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

    def get_sheet_column_pieces(self, sheetname, checks=False):
        a_sheet = self.A[sheetname]
        b_sheet = self.B[sheetname]

        a_columns = a_sheet.get_columns()
        b_columns = b_sheet.get_columns()

        if checks:
            self.column_checks(a_sheet, b_sheet, a_columns, b_columns)

        d = self.get_set_pieces(a_columns, b_columns)
        d["indexed_ab"] = [(v, a_columns.index(v), b_columns.index(v)) for v in
                           d["both_ab"]]
        return d

    def report_column_pieces(self, sheetname):
        d = self.get_sheet_column_pieces(sheetname, checks=True)
        only_a = d["only_a"]
        only_b = d["only_b"]
        both_ab = d["both_ab"]
        print(utils.format_header("Columns comparison"))
        if only_a:
            print("A \ B: " + ", ".join(only_a))
        if only_b:
            print("B \ A: " + ", ".join(only_b))
        if both_ab:
            print("A \u2229 B:")
            for i, item in enumerate(both_ab):
                print("{:>3}.".format(i), item.replace("\n", "\\n"))
        print()
        return d["indexed_ab"]

    @staticmethod
    def key_checks(a_keys, b_keys):
        a_duplicates = [v for v, c in collections.Counter(a_keys).items()
                        if c > 1]
        b_duplicates = [v for v, c in collections.Counter(b_keys).items()
                        if c > 1]

        print(utils.format_header("Row key duplicates"))

        if a_duplicates:
            m = "A duplicate row keys: {}"
            m = m.format(", ".join(("|".join(v) for v in a_duplicates)))
            print(m)

        if b_duplicates:
            m = "B duplicate row keys: {}"
            m = m.format(", ".join(("|".join(v) for v in b_duplicates)))
            print(m)

    def get_key_pieces(self, sheetname, key, checks=False):
        a_sheet = self.A[sheetname]
        b_sheet = self.B[sheetname]

        a_columns = a_sheet.get_columns()
        b_columns = b_sheet.get_columns()

        a_inds = [a_columns.index(k) for k in key]
        b_inds = [b_columns.index(k) for k in key]

        a_keys = [tuple(row[i] for i in a_inds) for row in a_sheet]
        b_keys = [tuple(row[i] for i in b_inds) for row in b_sheet]

        if checks:
            self.key_checks(a_keys, b_keys)

        d = self.get_set_pieces(a_keys, b_keys)
        d["indexed_ab"] = [(v, a_keys.index(v), b_keys.index(v)) for v in
                           d["both_ab"]]
        return d

    def report_key_pieces(self, sheetname, key):
        d = self.get_key_pieces(sheetname, key, checks=True)
        only_a = d["only_a"]
        only_b = d["only_b"]
        both_ab = d["both_ab"]
        print(utils.format_header("Row key comparison"))
        if only_a:
            print("A \ B: " + ", ".join(("|".join(v) for v in only_a)))
        if only_b:
            print("B \ A: " + ", ".join(("|".join(v) for v in only_b)))
        if both_ab:
            print("A \u2229 B: " + ", ".join(("|".join(v) for v in both_ab)))
        print()
        return d["indexed_ab"]

    def compare_sheet_columns(self, sheetname):
        a_sheet = self.A[sheetname]
        b_sheet = self.B[sheetname]
        shared_columns = self.compare_columns(a_sheet, b_sheet)
        return shared_columns

    def compare_sheet_by_name(self, sheetname, key, shared_columns):
        # Show columns in A not in B
        # Show columns in B not in A
        # Show columns in both A and B
        # Headings must exist and be unique
        #shared_columns = self.compare_columns(a_sheet, b_sheet)

        # Key col must exist in A and B
        # Key col can be tuple of int for column numbers
        # Key col can be tuple of string for column headings

        # Show keys in A not in B
        # Show keys in B not in A
        # Go through one by one the keys in both A and B
        # Key must be unique in spreadsheet
        shared_keys = self.report_key_pieces(sheetname, key)
        return self.compare_cells(sheetname, shared_keys, shared_columns)

    def compare_cells(self, sheetname, shared_keys, shared_columns):
        a_sheet = self.A[sheetname]
        b_sheet = self.B[sheetname]

        for k, ak, bk in shared_keys:
            a_row = a_sheet[ak]
            b_row = b_sheet[bk]
            for c, ac, bc in shared_columns:
                a_cell = a_row[ac]
                b_cell = b_row[bc]
                if a_cell != b_cell:
                    yield Comparator.Difference(
                        key=k, col=c, a_sheetname=a_sheet.name,
                        b_sheetname=b_sheet.name, a_cell=a_cell, b_cell=b_cell,
                        a_loc=(ak, ac), b_loc=(bk, bc)
                    )
                    # print("{}, {}".format("|".join(k), c))
                    # a_loc = ">> A!{}[{}{}]"
                    # a_col_xl = utils.number_to_excel_column(ac)
                    # a_row_xl = str(ak + 1)
                    # a_loc = a_loc.format(a_sheet.name, a_col_xl, a_row_xl)
                    # print(a_loc)
                    # print('"{}"'.format(a_cell))
                    # print("==")
                    # print('"{}"'.format(b_cell))
                    # b_loc = "<< B!{}[{}{}]"
                    # b_col_xl = utils.number_to_excel_column(bc)
                    # b_row_xl = str(bk + 1)
                    # b_loc = b_loc.format(b_sheet.name, b_col_xl, b_row_xl)
                    # print(b_loc)
                    # print()

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

        print(utils.format_header("Row key comparison"))

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

        print(utils.format_header("Columns comparison"))

        if only_a:
            print("A \ B: " + ", ".join(only_a))
        if only_b:
            print("B \ A: " + ", ".join(only_b))
        if both_ab:
            print("A \u2229 B:")
            for i, item in enumerate(both_ab):
                print("{:>3}.".format(i), item.replace("\n", "\\n"))
        print()

        shared_ab = [(item, a_columns.index(item), b_columns.index(item)) for
                     item in both_ab]
        return shared_ab

    class Difference:
        def __init__(self, **kwargs):
            self.key = kwargs["key"]
            self.col = kwargs["col"]
            self.a_sheetname = kwargs["a_sheetname"]
            self.b_sheetname = kwargs["b_sheetname"]
            self.a_cell = kwargs["a_cell"]
            self.b_cell = kwargs["b_cell"]
            self.a_loc = kwargs["a_loc"]
            self.b_loc = kwargs["b_loc"]

            self.accept_to_a = False
            self.accept_to_b = False
            self.highlight = False

        def __str__(self):
            s1 = "{}, {}".format("|".join(self.key), self.col)
            a_loc = ">> A!{}[{}{}]"
            a_col_xl = utils.number_to_excel_column(self.a_loc[1])
            a_row_xl = str(self.a_loc[0] + 1)
            a_loc = a_loc.format(self.a_sheetname, a_col_xl, a_row_xl)
            s2 = a_loc
            s3 = '"{}"'.format(self.a_cell)
            s4 = "=="
            s5 = '"{}"'.format(self.b_cell)
            b_loc = "<< B!{}[{}{}]"
            b_col_xl = utils.number_to_excel_column(self.b_loc[1])
            b_row_xl = str(self.b_loc[0] + 1)
            b_loc = b_loc.format(self.b_sheetname, b_col_xl, b_row_xl)
            s6 = b_loc
            return "\n".join([s1, s2, s3, s4, s5, s6])


class IComparator:

    class QuitException(Exception):
        pass

    def __init__(self, comparator):
        self.comparator = comparator

    def select_sheetname(self):
        common_sheetnames = self.comparator.report_sheetname_pieces()
        quit_choices = ("q", "Q", "q()", "Q()", "x", "X", "x()", "X()")
        quit = next((i for i in quit_choices if i not in common_sheetnames))
        print("Type the name of the sheet you want to compare in A \u2229 B")
        print("[{}] Quit".format(quit))
        while True:
            choice = input("Choice> ")
            if choice == quit:
                raise IComparator.QuitException()
            elif choice == "":
                print("Nothing selected!")
                continue
            selected = [n for n in common_sheetnames if n.startswith(choice)]
            exact = [n for n in common_sheetnames if n == choice]
            if len(selected) == 1 or len(exact) == 1:
                if exact:
                    selection = exact[0]
                else:
                    selection = selected[0]
                print('You have selected "{}"'.format(selection))
                print()
                return selection
            elif len(selected) == 0:
                print('No sheet selected with input "{}"'.format(choice))
            else:  # len(selected) > 1
                print('Ambiguous selection matches:', *selected)

    def select_key_columns(self, sheetname):
        shared_columns = self.comparator.report_column_pieces(sheetname)
        m = ("Type a space-separated list of numbers to indicate which columns "
             "should create a row-key from columns in A \u2229 B")
        print(m)
        quit = "q"
        print("[{}] Quit".format(quit))
        while True:
            choice = input("Choice> ")
            if choice == quit:
                raise IComparator.QuitException()
            elif choice == "":
                print("Nothing selected!")
                continue
            selection = choice.split()
            keys = [shared_columns[int(i)][0] for i in selection]
            print("You have selected:", ", ".join(keys))
            return keys

    def compare_sheet_by_name(self, sheetname, key, shared_columns):
        b_to_a = "a"
        b_to_a_highlight = "A"
        a_to_b = "b"
        a_to_b_highlight = "B"
        skip = "n"
        quit = "q"

        cell_differences = self.comparator.compare_sheet_by_name(sheetname,
                                                                 key,
                                                                 shared_columns)
        if cell_differences:
            print(utils.format_header("Cell by cell comparison"))
        for diff in cell_differences:
            total_rows = len(self.comparator.A[diff.a_sheetname])
            location = "{}/{}. ".format(diff.a_loc[0] + 1, total_rows)
            print()
            print("Row", location, end="")
            print(diff)
            print("[{}] Copy B to A".format(b_to_a))
            print("[{}] Copy B to A and highlight".format(b_to_a_highlight))
            print("[{}] Copy A to B".format(a_to_b))
            print("[{}] Copy A to B and highlight".format(a_to_b_highlight))
            print("[{}] Next (skip)".format(skip))
            print("[{}] Quit".format(quit))
            while True:
                choice = input("Choice> ")
                if choice == quit:
                    raise IComparator.QuitException()
                elif choice == skip:
                    break
                elif choice == b_to_a:
                    diff.accept_to_a = True
                    self.comparator.accept_difference(sheetname, diff)
                    break
                elif choice == b_to_a_highlight:
                    diff.accept_to_a = True
                    diff.highlight = True
                    self.comparator.accept_difference(sheetname, diff)
                    break
                elif choice == a_to_b:
                    diff.accept_to_b = True
                    self.comparator.accept_difference(sheetname, diff)
                    break
                elif choice == a_to_b_highlight:
                    diff.accept_to_b = True
                    diff.highlight = True
                    self.comparator.accept_difference(sheetname, diff)
                    break
                else:
                    print("Bad selection. Try again.")

    def run(self):
        try:
            print(utils.format_header("Interactive comparator"))
            print(self.comparator)
            sheetname = self.select_sheetname()
            key = self.select_key_columns(sheetname)
            col_pieces = self.comparator.get_sheet_column_pieces(sheetname)
            shared_columns = col_pieces["indexed_ab"]
            self.compare_sheet_by_name(sheetname, key, shared_columns)
            self.comparator.write_out_excel(prefix="comp-")
        except IComparator.QuitException:
            print("Quitting. Goodbye...")


if __name__ == '__main__':
    files = [
        '/Users/jpringle/Downloads/KER5-SDP-Questionnaire-v2-jef.xlsx',
        '/Users/jpringle/Downloads/NER3-SDP-Questionnaire-v3-jkp.xlsx'
        #'test/files/IDR2-SDP-Questionnaire-v2-lhm.xlsx',
        #'test/files/GHR5-SDP-Questionnaire-v13-jkp.xlsx'
        #'test/files/test1.xlsx',
        #'test/files/test2.xlsx'
    ]
    wb1 = workbook.Workbook(files[0])
    wb2 = workbook.Workbook(files[1])
    c = Comparator(wb1, wb2)
    ic = IComparator(c)
    ic.run()
#    print(c)
#    c.compare_sheetnames()
#    c.compare_sheet_by_name("survey", key=("type", "name"))
