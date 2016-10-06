#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Take a spreadsheet and create a cascading select from it


import xlrd
import xlsxwriter

filename=''

with xlrd.open_workbook(filename) as book:
    sheet = book.sheet_by_index(0)
    for col_ind in range(sheet.ncols):
        pass
