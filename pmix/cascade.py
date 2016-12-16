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
            self.rename = None
            self.label = label
            self.identifier = identifier
            self.children = []
            self.parent = None

        def add_child(self, node):
            node.parent = self
            self.children.append(node)

        def get_node(self, node):
            new_node = None
            for child in self.children:
                name_match = child.name == node.name
                label_match = child.label == node.label
                identifier_match = child.identifier == node.identifier
                if name_match and label_match and identifier_match:
                    new_node = child
                    break
            return new_node

        def append_last(self, node):
            cur_node = self
            while cur_node.children:
                cur_node = cur_node.children[0]
            cur_node.add_child(node)

        def next(self):
            if self.children:
                return self.children[0]
            else:
                raise CascadeError()

        def gen(self):
            cur = self
            while True:
                try:
                    yield cur
                    cur = cur.next()
                except CascadeError:
                    break

        def get_name(self):
            return self.rename if self.rename else self.name

        def __str__(self):
            return "Id: {}, name: {}".format(self.identifier, self.name)

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
            for node in chain.gen():
                ref_node = ref.get_node(node)
                if ref_node:
                    ref = ref_node
                else:
                    ref.add_child(node)
                    break
        else:
            self.data.add_child(chain.next())

    def rename_data(self):
        queue = self.data.children
        level_names = set()
        next_queue = []
        while queue:
            for node in queue:
                next_queue.extend(node.children)
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
            queue = next_queue
            next_queue = []
            level_names = set()

    def to_rows(self):
        rows = []
        queue = self.data.children
        next_queue = []
        while queue:
            for node in queue:
                next_queue.extend(node.children)
                list_name = "{}_list".format(node.identifier)
                name = node.get_name()
                label = node.label
                row_filter = node.parent.get_name()
                row = [list_name, name, label, row_filter]
                rows.append(row)
            queue = next_queue
            next_queue = []
        return rows

if __name__ == '__main__':
    f = 'test/files/rj_cascade.xlsx'
    c = Cascade(f)
    for c in c.to_rows():
        print(c)
