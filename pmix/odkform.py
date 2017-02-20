import argparse

from pmix.error import OdkformError
from pmix.odkchoices import Odkchoices
from pmix.odkprompt import Odkprompt
from pmix.workbook import Workbook

class Odkform:
    """
    A json row is

      {
        "name": "question1",
        "type": "integer",
        "label": {
          "English": "text here",
          "Spanish": "palabras aquí"
        },
        "hint": {
          "English": "text here",
          "Spanish": "palabras aquí"
        },
        "choices": "CHOICE_LIST",
        "constraint_message": {
          "English": "text here",
          "Spanish": "palabras aquí"
        },
        "constraint": "EQUATION",
        "relevant": "EQUATION",
        ...
      }

    A json choice list is object

      {
        "name": [
          "option_name1",
          "option_name2",
          ...
        ]
        "label": {
          "English": [
            "Option 1",
            "Option 2",
            ...
          ],
          "Spanish": [
            "Opción 1",
            "Opción 2",
            ...
          ]
        },
        "filter1": [
          "expression1",
          "expression2",
          ...
        ]
      }
    """

    select_types = (
        'select_one',
        'select_multiple',
        'select_one_external',
        'select_multiple_external',
    )

    select_alias = {
        'select_one_external': 'select_one',
        'select_multiple_external': 'select_multiple'
    }

    all_types = (
        # STANDARD PROMPTS
        'integer',
        'decimal',
        'note',
        'calculate',
        'geopoint',
        'image',
        'text',
        'date',
        'dateTime',
        # GROUPS and REPEATS
        'begin group',
        'begin repeat',
        'end group',
        'end repeat',
        # HIDDEN
        'hidden',
        'hidden string',
        'hidden geopoint',
        # METADATA
        'start',
        'end',
        'deviceid',
        'simserial'
    )

    def __init__(self, *, f=None, wb=None):
        if f is None and wb is None:
            raise OdkformError()
        elif f is not None:
            wb = Workbook(f)

        self.choices = self.get_choices(wb, 'choices')
        self.external_choices = self.get_choices(wb, 'external_choices')
        self.questionnaire = self.convert_survey(wb)

    def to_text(self):
        q_text = (q.to_text() for q in self.questionnaire)
        sep = '\n' + '=' * 50 + '\n'
        result = sep.join(q_text)
        return result


    def convert_survey(self, wb):
        """Convert rows and strings of a workbook into better python objects

        :param wb: Workbook object representing an XLSForm.
        :return: A list of better python objects
        """
        result = []
        try:
            survey = wb['survey']
            header = survey[0]
            for i, row in enumerate(survey):
                if i == 0:
                    continue
                json_row = {k: v for k, v in zip(header, row)}
                token = self.parse_type(json_row)
                if token['token_type'] == 'prompt':
                    json_row['simple_type'] = token['simple_type']
                    if 'choice_list' in token:
                        choices = token['choice_list']
                    else:
                        choices = None
                    this_prompt = Odkprompt(json_row, choices)
                    result.append(this_prompt)
        except KeyError:
            # no survey found
            pass
        return result

    def parse_type(self, row):
        row_type = row['type']
        if row_type in Odkprompt.response_types + Odkprompt.non_response_types:
            return {
                'token_type': 'prompt',
                'simple_type': row_type
            }
        elif row_type.startswith('select_one_external '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
        elif row_type.startswith('select_multiple_external '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
        elif row_type.startswith('select_one '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
        elif row_type.startswith('select_multiple '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
        # TODO add in support for "begin group", "end group", "begin repeat",
        # TODO "end repeat", and "table" here
        else:
            return {'token_type': None}

    @staticmethod
    def get_choices(wb, ws):
        """Extract choices from an XLSForm

        :param wb: Source workbook
        :param ws: One of 'choices' or 'external_choices'
        :return: Dict with keys as list names
        """
        d = {}
        try:
            choices = wb[ws]
            header = choices[0]
            if 'list_name' not in header:
                m = 'Column "list_name" not found in {} tab'.format(ws)
                raise OdkformError(m)
            for i, row in enumerate(choices):
                if i == 0:
                    continue
                json_row = {k: v for k, v in zip(header, row)}
                list_name = json_row['list_name']
                if list_name in d:
                    d[list_name].add(json_row)
                elif list_name: # not "else:" because possibly blank rows
                    odkchoices = Odkchoices(list_name)
                    odkchoices.add(json_row)
                    d[list_name] = odkchoices
        except KeyError:
            # worksheet does not exist
            pass
        return d


if __name__ == '__main__':
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    language_help = 'Language to write the paper version in.'
    parser.add_argument('-l', '--language', help=language_help)

    format_help = ('Format to generate. Currently "text" is supported. Future '
                   'formats include "html" and "pdf".')
    parser.add_argument('-f', '--format', action='append', help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    odkform = Odkform(f=args.xlsxfile)
