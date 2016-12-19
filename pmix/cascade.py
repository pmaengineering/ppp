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

    class Iter:
        def __init__(self, node):
            self.queue = [node]

        def __next__(self):
            try:
                next = self.queue.pop(0)
                self.queue.extend(next.children)
                return next
            except IndexError:
                raise StopIteration

        def levels(self):
            current = self.queue
            while current:
                yield current
                next = []
                for node in current:
                    next.extend(node.children)
                current = next

    class Node:
        def __init__(self, *, name, label, identifier):
            self.name = name
            self.label = label
            self.identifier = identifier
            self.children = []

            self.rename = None
            self.parent = None

        def add(self, node):
            node.parent = self
            self.children.append(node)

        # returns None if not found
        def node(self, node):
            for child in self.children:
                name_match = child.name == node.name
                label_match = child.label == node.label
                identifier_match = child.identifier == node.identifier
                if name_match and label_match and identifier_match:
                    return child

        def add_last(self, node):
            cur_node = self
            while cur_node.children:
                cur_node = cur_node.children[0]
            cur_node.add(node)

        def __iter__(self):
            return Cascade.Iter(self)

        def get_name(self, name=None):
            if name is None:
                return self.rename if self.rename else self.name
            else:
                self.name = name

        def __str__(self):
            m = "Id: {}, name: {}, label: {}"
            return m.format(self.identifier, self.get_name(), self.label)

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
        self.has_name, self.has_label = list(vals)[0]

        for row in ws[1:]:
            self.add_row_to_tree(row)

        self.rename_data()

    def add_row_to_tree(self, row):
        root = Cascade.Node(name=None, label=None, identifier=None)
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
            root.add_last(node)
        self.insert_chain(root)

    def insert_chain(self, chain):
        ref = self.data
        for i, node in enumerate(chain):
            if i == 0:
                continue
            ref_node = ref.node(node)
            if ref_node:
                ref = ref_node
            else:
                ref.add(node)
                break

    def rename_data(self):
        for level in Cascade.Iter(self.data).levels():
            level_names = set()
            for node in level:
                if node.name in level_names:
                    i = 1
                    next_name = node.name + "_{}".format(i)
                    while next_name in level_names:
                        i += 1
                        next_name = node.name + "_{}".format(i)
                    node.rename = next_name
                    level_names.add(node.rename)
                else:
                    level_names.add(node.name)

    def to_rows(self):
        rows = []
        for i, node in enumerate(self.data):
            if i == 0:
                continue
            list_name = "{}_list".format(node.identifier)
            name = node.get_name()
            label = node.label
            row_filter = node.parent.get_name()
            row = [list_name, name, label, row_filter]
            rows.append(row)
        return rows

    def __iter__(self):
        return iter(self.data)

if __name__ == '__main__':
    f = 'test/files/rj_cascade.xlsx'
    c = Cascade(f)
    for c in c.to_rows():
        print(c)
