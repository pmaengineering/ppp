from os import path as os_path
TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__)) + '/files'

if __name__ == '__main__':
    import doctest
    file = TEST_FORMS_DIRECTORY + "/../../" + "pmix/ppp/odkform.py"
    doctest.testfile(filename=file, module_relative=False)
