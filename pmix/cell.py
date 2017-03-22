class Cell:
    """This class represents a cell from a spreadsheet"""

    def __init__(self, value, datemode=None):
        self.value = None
        self.formatting = set()
        
    @classmethod
    def from_cell(cls, cell, datemode=None):


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
            m = 'Unhandled cell type: {}. Value is: {}'
            m = m.format(cell.ctype, cell.value)
            raise TypeError(m)
        

