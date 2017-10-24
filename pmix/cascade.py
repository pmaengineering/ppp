#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Take a spreadsheet and create a cascading select from it.

Column names must be written as

    [identifier]|name
    [identifier]|label

    # TODO language support
    [identifier]|label::language

Extra columns do not matter. Identifer should be a able to become a list_name

name and label are optional, but at least one must exist
"""

import os.path
import argparse

import xlsxwriter

from pmix.workbook import Workbook
from pmix.error import CascadeError


class Cascade:
    """Class to represent a cascading select.

    There are two formats.

    (1) Wide: one row for the smallest geography (EA, typically). The higher
        level geographies are repeated because, for example, there are many
        EAs in a state.
    (2) Tall: one row for each identifier. The identifier is associated with
        the geographic level above it. For example, a city is in a county.
        In this format, there is no duplication.

    PMA team members often give data in the "wide" format. ODK requires the
    tall format.

    Currently (2017-06-01) this class accepts Wide and converts to Tall.

    TODO:
        Accept Tall and convert to Wide.
    """

    def __init__(self, path, sheet=None):
        """Initialize a Cascade object from file and sheet.

        Args:
            path (str): The path to where to find the .xlsx workbook
            sheet (str or int): The sheet in the Workbook to use.
        """
        self.data = Cascade.Node(name=None, label=None, identifier=None)
        self.file = path
        wb = Workbook(self.file)
        if sheet is None:
            ws = wb[0]
        else:
            ws = wb[sheet]
        self.column_names = ws.column_headers()
        self.identifiers = {}
        self.identifier_order = []
        self.parse_identifiers()
        vals = set(self.identifiers.values())
        if len(vals) != 1:
            # if len == 0, then not formatted as e.g. [identifier]|name
            # if len > 1, then too many types
            raise CascadeError()
        self.has_name, self.has_label = list(vals)[0]

        for row in ws[1:]:
            self.add_row_to_tree(row)

        self.rename_data()

    def parse_identifiers(self):
        """Parse the identifiers from the column headers."""
        for col in self.column_names:
            this_split = col.split('|', 1)
            try:
                # e.g. level1|label::English
                identifier = this_split[0]
                has_name = this_split[1] == 'name'
                has_label = this_split[1] == 'label'
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

    def add_row_to_tree(self, row):
        """Add a row from the tall format to the geographic identifier tree.

        Args:
            row (list of Cell): A row from the Worksheet.
        """
        root = Cascade.Node(name=None, label=None, identifier=None)
        for i in self.identifier_order:
            has_name, has_label = self.identifiers[i]
            name = None
            if has_name:
                name_col = '{}|{}'.format(i, 'name')
                name = str(row[self.column_names.index(name_col)])
            label = None
            if has_label:
                label_col = '{}|{}'.format(i, 'label')
                label = str(row[self.column_names.index(label_col)])
            node = Cascade.Node(name=name, label=label, identifier=i)
            root.add_last(node)
        self.insert_chain(root)

    def insert_chain(self, chain):
        """Add a chain of geographic identifiers to the tree.

        A chain is derived from a row in the "wide" format.

        Args:
            chain (Cascade.Node): A linked list of nodes. This argument is the
                root of the linked list.
        """
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
        """Rename ODK names where there are colisions."""
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
        """Convert to rows in the tall format.

        Returns:
            A list of rows. Each row is a list of string.
        """
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
        """Iterate over the data as a Cascade Node iterator."""
        return iter(self.data)

    def write_out(self, path):
        """Write this cascading select in tall format.

        Args:
            path (str): The path where to write the Excel book.

        TODO:
            - Add this method Workbook methods. i.e. create a workbook from
              the results here then call the write_out method of the workbook.
            - Generalize formatting.
        """
        wb = xlsxwriter.Workbook(path)
        highlight = wb.add_format()
        highlight.set_bg_color('#FDFD96')
        ws = wb.add_worksheet("cascade")
        for i, node in enumerate(self.data):
            if i == 0:
                to_write = ["list_name", "name", "label", "filter_list"]
                ws.write_row(i, 0, to_write)
            else:
                list_name = "{}_list".format(node.identifier)
                name = node.get_name()
                label = node.label
                row_filter = node.parent.get_name()
                row = [list_name, name, label, row_filter]
                ws.write_row(i, 0, row)
                if node.rename is not None:
                    ws.write(i, 1, node.rename, highlight)

    class Iter:  # pylint: disable=too-few-public-methods
        """A class for BFS iterating over this Cascade data structure."""

        def __init__(self, node):
            """Initialize the iterator.

            Args:
                node (Cascade.Node): The node to start searching at.
            """
            self.queue = [node]

        def __next__(self):
            """Get the next item for the iterator in BFS.

            This supports the iterator protocol.
            """
            try:
                next_item = self.queue.pop(0)
                self.queue.extend(next_item.children)
                return next_item
            except IndexError:
                raise StopIteration

        def levels(self):
            """Yield the levels of the iterator."""
            current = self.queue
            while current:
                yield current
                next_item = []
                for node in current:
                    next_item.extend(node.children)
                current = next_item

    class Node:
        """Class to represent a node in the Cascade data structure.

        This is in essence a tree where each node can have any number of
        children.
        """

        def __init__(self, *, name, label, identifier):
            """Initialize the node with a name, label, and identifier.

            The name and label are the ODK name and label. The identifier
            roughly corresponds to the ODK list_name.

            Args:
                name (str): The ODK name
                label (str): The ODK label
                identifer (str): The geographic identifier
            """
            self.name = name
            self.label = label
            self.identifier = identifier
            self.children = []

            self.rename = None
            self.parent = None

        def add(self, node):
            """Add a node as the child of this node.

            Args:
                node (Node): The node to add
            """
            node.parent = self
            self.children.append(node)

        def node(self, node):
            """Get the node that matches the input.

            Args:
                node (Node): The node to match

            Returns:
                The node among the children of this node that matches. Returns
                None if no match is found.
            """
            for child in self.children:
                name_match = child.name == node.name
                label_match = child.label == node.label
                identifier_match = child.identifier == node.identifier
                if name_match and label_match and identifier_match:
                    return child

        def add_last(self, node):
            """Add a node to the very bottom of this tree.

            Start at the root, and go child to child to child until the end.
            Then add the input node.

            Args:
                node (Node): The node to add
            """
            cur_node = self
            while cur_node.children:
                cur_node = cur_node.children[0]
            cur_node.add(node)

        def __iter__(self):
            """Return an iterator starting at this node."""
            return Cascade.Iter(self)

        def get_name(self):
            """Get the name of this node."""
            return self.rename if self.rename else self.name

        def __str__(self):
            """Return the string representation of this node."""
            msg = "Id: {}, name: {}, label: {}"
            return msg.format(self.identifier, self.get_name(), self.label)


def cascade_cli():
    """Run the command-line interface for this module."""
    prog_desc = 'Make a cascading select for geographic identifiers'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm containing geographic identifiers.'
    parser.add_argument('xlsxfile', help=file_help)

    sheet_help = ('Supply the worksheet name here. If not, then the first '
                  'worksheet is assumed.')
    parser.add_argument('-s', '--sheet', help=sheet_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    base, file = os.path.split(args.xlsxfile)
    name, ext = os.path.splitext(file)
    if args.outpath is not None:
        outpath = args.outpath
    else:
        outpath = os.path.join(base, name) + "-cascade" + ext

    cascade = Cascade(args.xlsxfile, args.sheet)
    cascade.write_out(outpath)
    print("Successfully saved file to: {}".format(outpath))


if __name__ == '__main__':
    cascade_cli()
