#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Take a spreadsheet and create a cascading select from it.

Column names must be written as

[identifier]::name
[identifier]::label

Extra columns do not matter
"""


from pmix import constants
from pmix.workbook import Workbook
from pmix.error import CascadeError


class Cascade:

    class Node:
        def __init__(self, *, name, label, identifier):
            self.name = name
            self.label = label
            self.identifier = identifier
            self.children = []

        def add_child(self, node):
            self.children.append(node)

        def child_by_name(self, name):
            pass

        def child_by_label(self, label):
            pass

        def get_node(self, node):
            new_node = None
            for child in self.children:
                name_match = self.name == node.name
                label_match = self.label == node.label
                identifier_match = self.identifier == node.identifier
                if name_match and label_match and identifier_match:
                    new_node = child
                    break
            return new_node

        def append_last(self, node):
            cur_node = self
            while cur_node.children:
                cur_node = cur_node.children[0]
            cur_node.children.append(node)

        def next(self):
            if self.children:
                return self.children[0]
            else:
                raise CascadeError()

        def __iter__(self):
            return self

        def __next__(self):
            if self.children:
                return self.children[0]
            else:
                raise StopIteration

    def __init__(self, f, sheet=None):
        self.data = Cascade.Node(name=None, label=None, identifier=None)
        self.file = f
        wb = Workbook(f)
        if sheet is None:
            ws = wb[0]
        else:
            ws = wb[sheet]
        self.column_names = ws.column_names()
        self.identifiers = {}
        self.identifier_order = []
        for col in self.column_names:
            this_split = col.split(constants.LANGUAGE_SEP, 1)
            try:
                identifier = this_split[0]
                has_name = this_split[1] == constants.NAME
                has_label = this_split[1] == constants.LABEL
                if identifier in self.identifiers:
                    had_name, had_label = self.identifiers[identifier]
                    new_name = had_name or has_name
                    new_label = had_label or has_label
                    self.identifiers[identifier] = new_name, new_label
                else:
                    self.identifiers[identifier] = has_name, has_label
                    self.identifier_order.append(identifier)
            except IndexError:
                pass
        vals = set(self.identifiers.values())
        if len(vals) != 1:
            # if len == 0, then not formatted as e.g. [identifier]::name
            # if len > 1, then too many types
            raise CascadeError()
        self.has_name, self.has_label = vals

        for row in ws[1:]:
            self.add_row_to_tree(row)

    def add_row_to_tree(self, row):
        root = None
        for i in self.identifier_order:
            has_name, has_label = self.identifiers[i]
            name = None
            if has_name:
                name_col = constants.BOTH_COL_FORMAT.format(i, constants.NAME)
                name = row[self.column_names.index(name_col)]
            label = None
            if has_label:
                label_col = constants.BOTH_COL_FORMAT.format(i, constants.LABEL)
                label = row[self.column_names.index(label_col)]
            node = Cascade.Node(name=name, label=label, identifier=i)
            if root is None:
                root = node
            else:
                root.append_last(node)
        self.insert_chain(root)

    def insert_chain(self, chain):
        if self.data.children:
            ref = self.data
            for node in chain:
                ref_node = ref.get_node(node)
                if ref_node:
                    ref = ref_node
                else:
                    ref.add_child(node)
                    break
        else:
            self.data.add_child(chain)


