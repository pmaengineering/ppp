"""Module for Cell class."""
import datetime
import xlrd


class Cell:
    """Representative class for spreadsheet cell."""

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

    def is_blank(self):
        """Test whether cell is blank."""
        return self.value is None or self.value == ''

    def equals(self, other, whitespace=True):
        """Return string equality of the two cells.

        Args:
            other (Cell): The other cell
            whitespace (bool): If False, give equality disregarding whitespace
        """
        if whitespace:
            return str(self) == str(other)
        this_str = ''.join(str(self).split())
        other_str = ''.join(str(other).split())
        return this_str == other_str

    def set_highlight(self, color='HL_YELLOW'):
        """Highlight this cell.

        Args:
            color (str): The highlight color
        """
        self.highlight = color

    def __bool__(self):
        """Get truthiness of the cell.

        Returns:
            Returns the truthiness of the cell value.
        """
        return bool(self.value)

    def __eq__(self, other):
        """Define equality comparison for Cells."""
        if isinstance(other, Cell):
            return self.value == other.value
        return False

    def __str__(self):
        """Return unicode representation of cell."""
        if self.value is None:
            return ''
        return str(self.value)

    def __repr__(self):
        """Return a representation of the cell."""
        msg = '<Cell(value={!r})>'.format(self.value)
        return msg

    @classmethod
    def from_cell(cls, cell, datemode=None, stripstr=True):
        """Create a Cell object by importing Cell from xlrd.

        Args:
            cell (xlrd.Cell): A cell to copy over.
            datemode (int): The datemode for the workbook where the cell is.
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            An intialized cell object.
        """
        value = cls.cell_value(cell, datemode, stripstr)
        new_cell = cls(value)
        return new_cell

    @staticmethod
    def cell_value(cell, datemode=None, stripstr=True):
        """Get python object out of xlrd.Cell value.

        Args:
            cell (xlrd.Cell): The cell
            datemode (int): The date mode for the workbook
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            The python object represented by this cell.
        """
        value = None
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            value = True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            # value = None  # ... redundant
            pass
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            if stripstr:
                value = cell.value.strip()
            else:
                value = cell.value
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            # Make integer what is equal to an integer
            int_val = int(cell.value)
            value = int_val if int_val == cell.value else cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            value = Cell.parse_datetime(cell.value, datemode)
        elif cell.ctype == xlrd.XL_CELL_ERROR:
            msg = 'Error cell found. Please correct or erase error cell from '\
                  'file and try again.\n\nError cells are likely to be one of'\
                  ' the following: #N/A, #NULL!, #DIV/0!, #VALUE!, #REF!, ' \
                  '#NAME?, #NUM!, #GETTING_DATA'
            raise TypeError(msg)
        else:
            msg = 'Unhandled cell exception.\nType: {}\nValue: {}'\
                .format(cell.ctype, cell.value)
            raise TypeError(msg)
        return value

    @staticmethod
    def parse_datetime(value, datemode):
        """Convert an xlrd cell value to a date time object.

        Args:
            value: The cell value
            datemode (int): The date mode of the Excel workbook
        """
        if datemode is None:
            # set to modern Excel
            datemode = 1
        date_tuple = xlrd.xldate_as_tuple(value, datemode)
        if date_tuple[:3] == (0, 0, 0):
            # must be time only
            value = datetime.time(*date_tuple[3:])
        elif date_tuple[3:] == (0, 0, 0):
            # must be date only
            value = datetime.date(*date_tuple[:3])
        else:
            value = datetime.datetime(*date_tuple)
        return value
