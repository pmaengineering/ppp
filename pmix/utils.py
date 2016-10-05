#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 James K. Pringle
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import constants

import re
import json
import unicodedata


class TransformRule:

    def __init__(self, params):
        self.transform = self.determine_transform(params)

    @staticmethod
    def determine_transform(params):
        try:
            transform_type = params[constants.TYPE]
            if transform_type == constants.STRIP:
                return lambda x: x.strip()
            elif transform_type == constants.REPLACE:
                args = params[constants.ARGS]
                regex = args[0]
                replacement = args[1]
                return lambda x: re.sub(regex, replacement, x)
            elif transform_type == constants.NORMALIZE:
                return lambda x: unicodedata.normalize('NFKD', x).encode(
                    'ascii', 'ignore').decode('ascii')
            elif transform_type == constants.SUBSTR:
                args = params[constants.ARGS]
                if args[0] == None:
                    start_ind = 0
                else:
                    start_ind = args[0]
                if args[1] == None:
                    return lambda x: x[start_ind:]
                else:
                    end_ind = args[1]
                    return lambda x: x[start_ind:end_ind]
            elif transform_type == constants.LOWER:
                return lambda x: x.lower()
            else:
                return id
        except (KeyError, IndexError):
            return id

    def apply(self, string):
        return self.transform(string)


def string_transform(s, rules):
    for rule in rules:
        s = rule.apply(s)
    return s


def decode_json(json_text, **kwargs):
    obj = json.loads(json_text, **kwargs)
    return obj


# col should be a zero-indexed integer
def number_to_excel_column(col):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if len(letters) * len(letters) < col:
        raise ValueError(col)
    remainder = col % len(letters)
    primary_letter = letters[remainder]
    quotient = col // len(letters)
    if quotient > 0:
        return letters[quotient - 1] + primary_letter
    else:
        return primary_letter


def write_out_worksheet(ws, lines):
    for i, line in enumerate(lines):
        ws.write_row(i, 0, line)


def format_header(s):
    inner_header = " {} "
    section_header = "{:*^80}"
    return section_header.format(inner_header.format(s))


# important for switching between google docs and xlsx
def newline_space_fix(s):
    newline_space = '\n '
    fix = '\n'
    while newline_space in s:
        s = s.replace(newline_space, fix)
    return s


def space_newline_fix(s):
    space_newline = ' \n'
    fix = '\n'
    while space_newline in s:
        s = s.replace(space_newline, fix)
    return s

if __name__ == '__main__':
    text_rules = """
        [
            {"TYPE": "STRIP"},
            {"TYPE": "REPLACE", "ARGS": ["[ ]+","_"]},
            {"TYPE": "REPLACE", "ARGS": ["[_]+","_"]},
            {"TYPE": "SUBSTR", "ARGS": [null, 18]},
            {"TYPE": "STRIP"}

        ]
    """
    obj = decode_json(text_rules)
    print(obj)

    rules = [TransformRule(params) for params in obj]

    strings = [" a b é c ф d ","01234567890123456789012345678901234567890"]
    for s in strings:
        print("'{}' -> '{}'".format(s, string_transform(s, rules)))
