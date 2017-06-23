"""Docstring tests for PPP package."""
from os import path as os_path
TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__)) + '/files'

if __name__ == '__main__':
    # import doctest
    # FILE = TEST_FORMS_DIRECTORY + "/../../" + "pmix/ppp/odkform.py"
    # doctest.testfile(filename=FILE, module_relative=False)

    # TODO: Figure out how to get past the following exception:
    # ValueError: line 380 of the docstring for odkform.py has inconsistent
    # leading whitespace: "'Ngakarimojong', 'Runyankole-Rukiga',
    # 'Runyoro-Rutoro']"
    # - Note: This works for testing as a suite with unit test, but apparently
    # not if the module is loaded directly as a file.

    pass
