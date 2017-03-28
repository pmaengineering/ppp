"""Module for the Cell class"""
import datetime


class Cell:
    """This class represents a cell from a spreadsheet"""

    def __init__(self, value=None):
        """Initialize cell to have value as Python object"""
        self.value = value
        self.highlight = None
        # TODO: More extensive formatting. For now, just support highlight
        # self.formatting = set()

    def __str__(self):
        """Return unicode representation of cell"""
        if self.value is None:
            return ''
        else:
            return str(self.value)
        
    @classmethod
    def from_cell(cls, cell, datemode=None):
        """Create a Cell object by importing Cell from xlrd"""
        value = cls.cell_value(cell, datemode)
        new_cell = cls(value)
        return new_cell

    @staticmethod
    def cell_value(cell, datemode=None):
        """Get python object out of xlrd Cell"""
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            return None
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            # Trimming whitespace until use-case shows no-need
            s = cell.value.strip()
            return s
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
                py_date = datetime.time(*date_tuple[3:]))
            else:
                py_date = datetime.datetime(*date_tuple)
            return py_date
        else:
            m = 'Unhandled cell type: {}. Value is: {}'
            m = m.format(cell.ctype, cell.value)
            raise TypeError(m)
        

