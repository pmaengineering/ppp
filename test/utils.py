"""Utilities for tests."""
import os
import unittest
from argparse import ArgumentParser

import doctest

from test.config import TEST_DIR


def get_args():
    """CLI for PPP test runner."""
    desc = 'Run tests for PPP package.'
    parser = ArgumentParser(description=desc)
    doctests_only_help = 'Specifies whether to run doctests only, as ' \
                         'opposed to doctests with unittests. Default is' \
                         ' False.'
    parser.add_argument('-d', '--doctests-only', action='store_true',
                        help=doctests_only_help)
    args = parser.parse_args()
    return args


def get_test_modules(test_package):
    """Get files to test.

    Args:
        test_package (str): The package containing modules to test.

    Returns:
        list: List of all python modules in package.

    """
    if test_package == 'ppp':  # TODO: Make dynamic.
        root_dir = TEST_DIR + "../" + "pmix/ppp"
    elif test_package == 'test':
        root_dir = TEST_DIR
    else:
        raise Exception('Test package not found.')

    test_modules = []
    for dirpath, dummy, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filename = filename[:-3]
                sub_pkg = dirpath.replace(root_dir, '').replace('/', '.')
                test_module = test_package + sub_pkg + '.' + filename
                test_modules.append(test_module)
    return test_modules


def get_test_suite(test_packages):
    """Get suite to test.

    Returns:
        TestSuite: Suite to test.

    """
    suite = unittest.TestSuite()
    for package in test_packages:
        pkg_modules = get_test_modules(test_package=package)
        for pkg_module in pkg_modules:
            suite.addTest(doctest.DocTestSuite(pkg_module))
    return suite
