"""Module defining Xlsform class to work with ODK XLSForms."""

import argparse
import os.path

from pmix.numbering import NumberingContext
from pmix.xlstab import Xlstab
import pmix.verbiage
from pmix.workbook import Workbook


class Xlsform(Workbook):
    """Class to represent an Xlsform spreadsheet.

    The Xlsform class extends the Workbook class to provide functionality
    related specifically to Xlsforms and would not be expected for a general-
    purpose Workbook.

    Note: Analogously, the Xlstab class extends the Worksheet class.
    """

    def __init__(self, path, stripstr=True):
        """Initialize workbook and cache Xlsform-specific info.

        Args:
            path (str): The path where to find the Xlsform file.
            stripstr (bool): Remove trailing / leading whitespace from text?
        """
        super().__init__(path, stripstr)
        self.data = [Xlstab.from_worksheet(ws) for ws in self]
        self.settings = {}
        self.init_settings()

    def init_settings(self):
        """Get settings from Xlsform.

        Post-condition: the Xlsform's settings are stored in the instance.
        """
        try:
            local_settings = self['settings']
            headers = local_settings[0]
            values = local_settings[1]
            self.settings = {str(k): str(v) for k, v in zip(headers, values) if
                             not k.is_blank() and not v.is_blank()}
        except (KeyError, IndexError):
            self.settings = {}

    @property
    def form_id(self):
        """Return form_id setting value."""
        self.init_settings()
        form_id = self.settings['form_id']
        return form_id

    @property
    def form_title(self):
        """Return form_title setting value."""
        self.init_settings()
        form_title = self.settings['form_title']
        return form_title

    @property
    def settings_language(self):
        """Return default language from settings or None if not found."""
        self.init_settings()
        default_language = self.settings.get('default_language', None)
        return default_language

    @property
    def survey_languages(self):
        """Retur sorted languages from headers for survey worksheet."""
        return self['survey'].sheet_languages()

    @property
    def form_language(self):
        """Return default language for a form.

        Considers settings tab first, then gets language from survey tab.

        Returns:
            A string for the default language or None if there is no language
            specified.
        """
        language = self.settings_language
        if language is None:
            try:
                language = self.survey_languages[0]
            except KeyError:
                # Keep language as None
                pass
        return language

    def add_language(self, language):
        """Add appropriate language columns to an Xlsform.

        Args:
            language (str): The language to add to all relevant sheets.
        """
        for sheet in self:
            sheet.add_language(language)

    def merge_translations(self, translations, ignore=None, carry=False):
        """Merge translations."""
        for sheet in self:
            sheet.merge_translations(translations, ignore, carry=carry)


def compute_prepend_numbers(inpath, col, outpath):
    """Compute numbers based on mini-language and prepend to all labels.

    This program highlights cells in the following two specific cases:

    (1) The numbering column says there should be a number in the label, but
        there is no number found in the original label. In this case, the
        number is add to the label.
    (2) The numbering column does not produce a number, but the original label
        has a number. In this case, the number is removed.

    Adding a number means to join the number, the string '. ', and the text of
    the cell.

    Args:
        inpath (str): The path where to find the source file.
        col (str): The name of the column where to find numbering.
        outpath (str): The path where to write the new xlsxfile.
    """
    xlsform = Xlsform(inpath)
    survey = xlsform['survey']
    context = NumberingContext()
    td_split_text = pmix.verbiage.TranslationDict.split_text
    for cell in survey.column(col):
        context.next(str(cell))
    for i, header in enumerate(survey.column_headers()):
        if header.startswith('label') or header.startswith('ppp_label'):
            header_skipped = False
            for num, cell in zip(context.string_iter(), survey.column(i)):
                if not header_skipped:
                    header_skipped = True
                    continue
                if num:
                    cell_num, the_rest = td_split_text(str(cell))
                    new_text = '. '.join((num, the_rest))
                    cell.value = new_text
                    if not cell_num:
                        cell.set_highlight()
                elif cell:
                    cell_num, the_rest = td_split_text(str(cell))
                    if cell_num:
                        cell.value = the_rest
                        cell.set_highlight()
    xlsform.write_out(outpath)


def xlsform_cli():
    """Run the command line interface for this module."""
    prog_desc = 'Utilities for XLSForms, depending on the options provided'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)


    numbering_help = ('Compute numbering based on a column in the "survey" '
                      'tab. If this option string is given with no argument, '
                      'then a default of "N" is assumed for the column '
                      'header. This program updates label and ppp_label '
                      'columns.')
    parser.add_argument('-n', '--numbering', help=numbering_help, nargs='?',
                        const='N')
    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)
    args = parser.parse_args()

    if args.numbering:
        filename, extension = os.path.splitext(args.xlsxfile)
        if args.outpath is None:
            outpath = os.path.join(filename+'-num'+extension)
        else:
            outpath = args.outpath
        compute_prepend_numbers(args.xlsxfile, args.numbering, outpath)
        print('Renumbered labels and wrote file to "{}"'.format(outpath))
    else:
        parser.error('No action requested. Use "-n".')


if __name__ == '__main__':
    xlsform_cli()
