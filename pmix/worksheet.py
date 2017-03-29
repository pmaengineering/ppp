"""This module defines the Worksheet class."""
import csv

from pmix.cell import Cell
from pmix.error import SpreadsheetError


class Worksheet:
    """This module represents a worksheet in a spreadsheet.

    A Worksheet is always supposed to have rectangular dimensions. It should
    not ever become a ragged array.

    Attributes:
        count (int): Keeps track of the sheets created without a name.
    """

    count = 0

    def __init__(self, *, data=None, name=None):
        """Initialize the Worksheet.

        Attributes:
            data (list): The rows of the worksheet
            name (str): The name of the worksheet

        Args:
            data: The data. Defaults to None to represent an empty worksheet.
            name (str): The string name of the Worksheet. If not supplied,
                then a default name is given.
        """
        if data is None:
            self.data = []
        else:
            self.data = data
        if name is None:
            Worksheet.count += 1
            self.name = 'sheet' + str(Worksheet.count)
        else:
            self.name = name

    def dim(self):
        """Return the dimensions of this Worksheet as tuple (nrow, ncol)."""
        nrow = len(self)
        ncol = self.ncol()
        return (nrow, ncol)

    def ncol(self):
        """Return the number of columns for this Worksheet.

        Checks that all rows have the same length.
        """
        if len(self) > 0:
            lengths = {len(line) for line in self}
            if len(lengths) > 1:
                msg = 'Worksheet has inconsistent column counts'
                raise SpreadsheetError(msg)
            else:
                return iter(lengths).__next__()
        else:
            return 0

    @classmethod
    def from_sheet(cls, sheet, datemode=None):
        """Create Worksheet from xlrd Sheet object.

        Args:
            sheet (xlrd.Sheet): A sheet instance to copy over
            datemode (int): The date mode of the Excel workbook

        Returns:
            An initialized Worksheet object
        """
        worksheet = cls(name=sheet.name)
        for i in range(sheet.nrows):
            cur_row = [Cell.from_cell(c, datemode) for c in sheet.row(i)]
            worksheet.data.append(cur_row)
        return worksheet

    def prepend_row(self, row=None):
        """Insert a row as the first row in this sheet.

        Args:
            row (sequence): A sequence of values to insert as the first row
                of this worksheet.
        """
        if row is None and self.data:
            new_row = [Cell() for _ in self.data[0]]
            self.data.insert(0, new_row)
        elif row is None:
            self.data.append([Cell()])
        else:
            # TODO: row is something, add it in.
            pass

    def append_col(self, header=None):
        """Append a column to the end of the worksheet.

        Args:
            header: The optional header for the column
        """
        for i, row in enumerate(self):
            if i == 0:
                row.append(Cell(header))
            else:
                row.append(Cell())

    def to_csv(self, path, strings=True):
        """Write this Worksheet as a CSV.

        Args:
            path (str): The path where to write the CSV
            strings (bool): False if the original value should be written,
                otherwise the string value of the cell is used.
        """
        with open(path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self:
                if strings:
                    values = [str(cell) for cell in row]
                else:
                    values = [cell.value for cell in row]
                csv_writer.writerow(values)

    def __iter__(self):
        """Return an iterator on the rows of this Worksheet."""
        return iter(self.data)

    def __getitem__(self, key):
        """Return the row indexed by key (int)."""
        return self.data[key]

    def __len__(self):
        """Return the number of rows."""
        return len(self.data)

    def __str__(self):
        """Return string representation of the Worksheet."""
        msg = '<"{}": {}>'.format(self.name, self.data)
        return msg

    def __repr__(self):
        """Return formal representation of the Worksheet."""
        msg = '<Worksheet(name="{}"), dim={}>'.format(self.name, self.dim())
        return msg
