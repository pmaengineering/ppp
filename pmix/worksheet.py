"""Module for Worksheet class."""
import csv

from pmix.cell import Cell
from pmix.error import SpreadsheetError


class Worksheet:
    """Representative class for a worksheet in a given spreadsheet workbook.

    A Worksheet is always supposed to have rectangular dimensions. It should
    not ever become a ragged array.

    Class Attributes:
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
        return nrow, ncol

    def ncol(self):
        """Return the number of columns for this Worksheet.

        Checks that all rows have the same length.
        """
        if self:
            lengths = {len(line) for line in self}
            if len(lengths) > 1:
                msg = 'Worksheet has inconsistent column counts'
                raise SpreadsheetError(msg)
            else:
                return iter(lengths).__next__()
        else:
            return 0

    @classmethod
    def from_sheet(cls, sheet, datemode=None, stripstr=True):
        """Create Worksheet from xlrd Sheet object.

        Args:
            sheet (xlrd.Sheet): A sheet instance to copy over
            datemode (int): The date mode of the Excel workbook
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            An initialized Worksheet object
        """
        worksheet = cls(name=sheet.name)
        for i in range(sheet.nrows):
            try:
                cur_row = [Cell.from_cell(c, datemode, stripstr) for c in
                           sheet.row(i)]
                worksheet.data.append(cur_row)
            except TypeError as err:
                msg = 'Error in row {}: {}'.format(str(i+1), str(err))
                raise TypeError(msg)
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
        elif len(row) != self.ncol():
            msg = 'Worksheet and supplied row width inconsistent ({} vs. {})'
            msg = msg.format(self.ncol(), len(row))
            raise SpreadsheetError(msg)
        else:
            new_row = [c if isinstance(c, Cell) else Cell(c) for c in row]
            self.data.insert(0, new_row)

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

    def column_headers(self):
        """Get the column headers for this worksheet.

        Returns:
            A tuple of the column headers as strings
        """
        if self.data:
            return tuple(str(i) for i in self.data[0])
        return ()

    def column_pairs(self, indices=None, base=None, start=0):
        """Iterate over pairs within the same row for all rows.

        Args:
            indices (sequence): A sequence of integers or strings, selecting
                which columns to iterate over. Order is preserved. Default of
                None means to use all columns.
            base (int or str): An integer for the column to use as the
                base/reference for pairs, or a string to match the column
                header. Default of None means to use the first of `indices`.
                This integer should be in `indices` if both are supplied.
            start (int): Which row to start yielding with. Defaults to 0,
                meaning iterate over all rows.

        Yields:
            Yields the pairs from the start row to the end of the sheet. They
            are of the form (BaseData, OtherData) and the data is stored in a
            CellData named tuple.
        """
        headers = self.column_headers()
        if indices is None:
            indices = list(range(self.ncol()))
        else:
            result = []
            for i in indices:
                item = i if isinstance(i, int) else headers.index(i)
                if item not in result:
                    result.append(item)
            indices = result
        if not indices:
            return
        if base is None:
            base = indices.pop(0)
        else:
            base = base if isinstance(base, int) else headers.index(base)
            if base in indices:
                indices.remove(base)
        for i, row in enumerate(self):
            if i < start:
                continue
            base_data = {
                'row': i,
                'col': base,
                'header': headers[base],
                'cell': row[base]
            }
            for j in indices:
                other_data = {
                    'row': i,
                    'col': j,
                    'header': headers[j],
                    'cell': row[j]
                }
                yield base_data, other_data

    def column_key(self, key):
        """Return a list of integers corresponding to the input.

        Args:
            key (list, str, or int): Str for lookup by name, int for lookup by
                index, or a list of those.

        Returns:
            A list of integers.
        """
        column_headers = self.column_headers()
        if isinstance(key, (int, str)):
            key = [key]
        result = []
        for item in key:
            if isinstance(item, str):
                try:
                    col = column_headers.index(item)
                    result.append(col)
                except ValueError:
                    raise KeyError(item)
            elif isinstance(item, int):
                result.append(item)
            else:
                raise TypeError(key)
        return result

    def column(self, key, start=0):
        """Iterate over the desired column cell by cell.

        Args:
            key (str or int): Str for lookup by name, int for lookup by index
            start (int): The row to start iterating on

        Yields:
            The cells in the requested column from the start row to the last

        Raises:
            ValueError: The supplied str does not match a column header
            IndexError: The supplied int is out of range
            TypeError: Neither str nor int is passed in as an argument
        """
        cols = self.column_key(key)
        col = cols[0]
        for row in self:
            if start <= 0:
                yield row[col]
            else:
                start -= 1

    def column_str(self, key, start=0):
        """Iterate over the desired column cell by cell and return the string.

        Args:
            key (str or int): Str for lookup by name, int for lookup by index
            start (int): The row to start iterating on

        Yields:
            The cell strings in the requested column from the start row to the
            last
        """
        for cell in self.column(key, start):
            yield str(cell)

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

    def cell_iter(self):
        """Iterate over the cells of a worksheet."""
        for row in self:
            yield from row

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
