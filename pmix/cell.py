"""Module for the Cell class."""
import datetime

import xlrd


class Cell:
    """This class represents a cell from a spreadsheet."""

    def __init__(self, value=None):
        """Initialize cell to have value as Python object.

        Attributes:
            value: A python object that is stored in the cell. Should be
                castable as str.
            highlight: The highlight color for this cell.

        Args:
            value: The value of the cell. Defaults to None for a blank cell.
        """
        self.value = value
        self.highlight = None
        # TODO: More extensive formatting. For now, just support highlight
        # self.formatting = set()

    def __str__(self):
        """Return unicode representation of cell."""
        if self.value is None:
            return ''
        else:
            return str(self.value)

    def __repr__(self):
        """Return a representation of the cell."""
        msg = '<Cell(value="{}")>'.format(self.value)
        return msg

    @classmethod
    def from_cell(cls, cell, datemode=None):
        """Create a Cell object by importing Cell from xlrd.

        Args:
            cell (xlrd.Cell): A cell to copy over.
            datemode (int): The datemode for the workbook where the cell is.

        Returns:
            An intialized cell object.
        """
        value = cls.cell_value(cell, datemode)
        new_cell = cls(value)
        return new_cell

    @staticmethod
    def cell_value(cell, datemode=None):
        """Get python object out of xlrd.Cell value.

        Args:
            cell (xlrd.Cell): The cell
            datemode (int): The date mode for the workbook

        Returns:
            The python object represented by this cell.
        """
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            return None
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            # Trimming whitespace until use-case shows no-need
            val = cell.value.strip()
            return val
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            # Make integer what is equal to an integer
            int_val = int(cell.value)
            return int_val if int_val == cell.value else cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            if datemode is None:
                # set to modern Excel
                datemode = 1
            date_tuple = xlrd.xldate_as_tuple(cell.value, datemode)
            if date_tuple[:3] == (0, 0, 0):
                # must be time only
                return datetime.time(*date_tuple[3:])
            elif date_tuple[3:] == (0, 0, 0):
                # must be date only
                return datetime.date(*date_tuple[:3])
            else:
                return datetime.datetime(*date_tuple)
        else:
            msg = 'Unhandled cell type: {}. Value is: {}'
            msg = msg.format(cell.ctype, cell.value)
            raise TypeError(msg)
