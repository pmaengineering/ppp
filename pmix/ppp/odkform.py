"""Module for the OdkForm class."""
import datetime
import os.path
from pmix.ppp.constants import LANGUAGE_DEPENDENT_FIELDS
from pmix.ppp.config import TEMPLATE_ENV
from pmix.ppp.error import OdkFormError, InvalidLanguageException
from pmix.ppp.odkchoices import OdkChoices
from pmix.ppp.odkgroup import OdkGroup
from pmix.ppp.odkprompt import OdkPrompt
from pmix.ppp.odkrepeat import OdkRepeat
from pmix.workbook import Workbook


class OdkForm:
    """Class to represent an entire XLSForm.

    Attributes:
        settings (dict): A dictionary represetnation of the original 'settings'
            worksheet of an ODK XLSForm.
        title (str): Title of the ODK form.
        languages (list): List of languages used in the ODK form. This is taken
            from the 'survey' worksheet.
        choices (dict): A list of rows from the 'choices' worksheet.
        ext_choices (dict): A list of rows from the 'external_choices'
            worksheet.
        metadata (dict): A dictionary of metadata for the original and
            converted ODK forms.
        questionnaire (list): An ordered representation of the ODK form,
            comprised of OdkPrompt, OdkGroup, OdkRepeat, and OdkTable objects.
    """

    def __init__(self, file=None, wb=None):
        """Initialize the OdkForm.

        Create an instance of an ODK form, including survey representation,
        choice options, settings, and metadata.

        Args:
            file (str): The path for the source file of the ODK form,
                typically an '.xlsx' file meeting the XLSForm specification.
            wb (Workbook): A Workbook object meeting XLSForm specification.
        Raises:
            OdkformError: No ODK form is supplied.
        """
        if file is None and wb is None:
            raise OdkFormError
        elif file is not None:
            wb = Workbook(file)

        self.settings = {str(k): str(v) for k, v in
                         self.get_settings(wb).items()}
        self.title = self.settings.get('form_title', os.path.split(wb.file)[1])
        self.metadata = {  # TODO Finish filling this out.
            'last_author': None,
            'last_updated': None,
            'changelog': None,
            'info': None,
            'raw_data': wb
        }
        self.languages = {
            'general_language_info': self.get_general_language_info(),
            'has_generic_language_field': False,
            'language_list': self.get_languages(wb),
            # 'default_language': self.get_default_language()
        }
        self.choices = self.get_choices(wb, 'choices')
        self.ext_choices = self.get_choices(wb, 'external_choices')
        conversion_start = datetime.datetime.now()
        self.metadata = {
            **self.metadata,
            **{
                'file_name': os.path.split(wb.file)[1],
                'form_id': self.settings.get('form_id'),
                'country': self.settings.get('form_id')[3:5],
                'round': self.settings.get('form_id')[6:7],
                'type_of_form': self.settings.get('form_id')[0:2],
                'conversion_start': conversion_start,
                'conversion_start_formatted':
                    str(conversion_start.date()) +
                    ' ' + str(conversion_start.time())[0:8],
                'conversion_end': None,
                'conversion_end_formatted': None,
                'conversion_time': None
            }
        }

        self.questionnaire = self.convert_survey(wb, self.choices,
                                                 self.ext_choices)

    unhandled_token_types = \
        ['calculate', 'start', 'end', 'deviceid', 'simserial',
         'phonenumber', 'hidden', 'hidden string', 'hidden int',
         'hidden geopoint']
    warnings = None
    conversion_info = None

    @staticmethod
    def get_settings(wb):
        """Get the XLSForm settings as a settings_dict.

        Args:
            wb (Workbook): A workbook object representing ODK form.

        Returns:
            dict: Form settings.:
        """
        settings_dict = {}
        try:
            settings = wb['settings']
            header = settings[0]
            details = settings[1]
            settings_dict = {k: v for k, v in zip(header, details)}
        except (KeyError, IndexError):
            # KeyError: Worksheet does not exist.
            # IndexError: Does not have the correct rows.
            pass
        return settings_dict

    @staticmethod
    def get_choices(wb, ws):
        """Extract choices from an XLSForm.

        Args:
            wb (Workbook): A Workbook object representing ODK form.
            ws (Worksheet): One of 'choices' or 'external_choices'.

        Returns:
            dict: A dictionary of choice list names with list of choices
                options for each list.

        Raises:
            OdkformError: Catches instances where list specified in the
                'survey' worksheet, but the list does not appear in the
                designated 'choices' or 'external_choices' worksheet.
        """
        formatted_choices = {}
        try:
            choices = wb[ws]
            header = [str(x) for x in choices[0]]
            if 'list_name' not in header:
                msg = 'Column "list_name" not found in {} tab'.format(ws)
                raise OdkFormError(msg)
            for i, row in enumerate(choices):
                if i == 0:
                    continue
                dict_row = {str(k): str(v) for k, v in zip(header, row)}
                list_name = dict_row['list_name']
                if list_name in formatted_choices:
                    formatted_choices[list_name].add(dict_row)
                elif list_name:  # Not "else:" because possibly blank rows.
                    odkchoices = OdkChoices(list_name)
                    odkchoices.add(dict_row)
                    formatted_choices[list_name] = odkchoices
        except KeyError:  # Worksheet does not exist.
            pass
        return formatted_choices

    @staticmethod
    def get_worksheet_languages(header):
        """Get worksheet languages.

        Args:
            header (list): Worksheet header.

        Returns:
            list: An alphabetically sorted list of languages.
        """
        lang_fields = {}
        for field in header:
            for lang_field in LANGUAGE_DEPENDENT_FIELDS:
                if str(field).startswith(lang_field) \
                        and not str(field).startswith('ppp_'):
                    if lang_field not in lang_fields:
                        lang_fields[lang_field] = {
                            'language_list': [],
                            'has_generic_language_field': False
                        }
                    if lang_field == str(field):
                        lang_fields[lang_field]['has_generic_language_field']\
                            = True
                    else:
                        lang = str(field)[len(lang_field + '::'):]
                        lang_fields[lang_field]['language_list'].append(lang)
        for field, data in lang_fields.items():
            data['language_list'] = sorted(data['language_list'])
        return lang_fields

    @staticmethod
    def check_generic_language_fields(ws_lang_fields):
        """Check for presense of generic language fields.

        Generic language fields are defined as ODK fields such as 'label',
        'hint', 'constraint_message', or media fields which have no
        corresponding '::<language>' assigned. In an XlsForm, for example, a
        field named 'label' would be an example of a generic language field. A
        field named 'label::Chinese' would not.

        Args:
            ws_lang_fields (dict): A dictionary of language field information
            for a given worksheet.

        Returns:
            bool: True if any language field in worksheet has generic language
            field. Otherwise returns False.
        """
        for k, v in ws_lang_fields.items():
            if k[v]['has_generic_language_field'] is True:
                return True
        return False

    @staticmethod
    def get_label_language_list(ws_lang_fields):
        """Get list of label languages for worksheet.

        Args:
            ws_lang_fields (dict): A dictionary of language field information
            for a given worksheet.

        Returns:
            list: An alphabetically sorted list of languages.
        """
        return sorted(ws_lang_fields['label']['language_list'])

    def get_general_language_info(self):
        """Consolidate language information for ODK form.

        Consolidate pertinent language information, such as languages list for
        relevant worksheets.

        Side Effects:
            self.languages['generic_language_fields_present']: True if generic
            language field is found in any language field.

        Returns:
            dict: Dictionary of general information on form language.
        """
        # TODO: Handle the following cases, both with (1) cases of a
        # TODO: presence of 'default_language', and (2) not.
        # * A 'label' field by itself on both sheets.
        # * A 'label' field with 'label::' fields on both sheets.
        # * Inconsistent 'label' 'label::' in worksheets.
        wb = self.metadata['raw_data']
        language_pertinent_worksheets = ['survey', 'choices',
                                         'external_choices']
        workbook_languages = {'worksheets': {}}

        # Set self.languages['general_language_info']
        for ws in language_pertinent_worksheets:
            if ws in [ws.name for ws in wb.data]:
                workbook_languages['worksheets'][ws] = {
                    'language_fields': self.get_worksheet_languages(wb[ws][0]),
                    'label_language_list': [],
                    'has_generic_language_field': False
                }
                ws_data = workbook_languages['worksheets'][ws]
                wslf = ws_data['language_fields']
                ws_data['label_language_list'] = \
                    self.get_label_language_list(wslf)
                ws_data['has_generic_language_fields'] = \
                    self.check_generic_language_fields(wslf)

        # Set self.languages['has_generic_language_field']
        for k, v in workbook_languages['worksheets'].items():
            if v['has_generic_language_field'] is True:
                self.languages['has_generic_language_field'] = True
                break
        return workbook_languages

    def get_languages(self, wb):
        """Get survey languages.

        Args:
            wb (Workbook): A Workbook object representing ODK form.

        Returns:
            list: An alphabetically sorted list of languages in the form.
        """
        header = wb['survey'][0]
        langs = set()
        for field in header:
            # TODO: Handle the following cases, both with (1) cases of a
            # TODO: presence of 'default_language', and (2) not.
            # * A 'label' field by itself on both sheets.
            # * A 'label' field with 'label::' fields on both sheets.
            # * Inconsistent 'label' 'label::' in worksheets.
            if field == 'label':
                if self.settings['default_language']:
                    raise InvalidLanguageException
                langs.add('')  # Default language. / Does this do anything?
            elif str(field).startswith('label::'):
                lang = str(field)[len('label::'):]
                langs.add(lang)
        return sorted(list(langs))

    def get_default_language(self):
        """Get default survey language if specified.

        Returns:
            str: The default language of the form.

        Raises:
            InvalidLanguageException: Various.
        """
        default = self.settings['default_language'] \
            if 'default_language' in self.settings \
            else self.languages['languages_list'][0]
        if not default:
            msg = 'InvalidLanguageException: \'default_language\' cannot be ' \
                  'empty.'
            msg += str(self.languages['languages_list'])
            raise InvalidLanguageException(msg)
        elif default not in self.languages['languages_list']:
            msg = 'InvalidLanguageException: \'default_language\' specified ' \
                  'was not found in \'survey\' worksheet.'
            raise InvalidLanguageException(msg)
        return default

    # Currently unused.
    # def set_conversion_end(self):
    #     """Set conversion end time."""
    #     # self.metadata['conversion_end'] = datetime.datetime.now()
    #     # self.metadata['conversion_end_formatted'] = \
    #     #     str(self.metadata['conversion_end'].date()) + ' ' + \
    #     #     str(self.metadata['conversion_end'].time())[0:8]
    #     pass

    def get_running_conversion_time(self):
        """Get running conversion time at this point in time.

        Returns:
            str: Total time taken to convert form.
        """
        self.metadata['conversion_time'] = \
            str(self.metadata['conversion_end'] - self.metadata[
                'conversion_start'])[5:10] + ' ' + 'seconds'

        return self.metadata['conversion_time']

    def to_text(self, **kwargs):
        """Get the text representation of an entire XLSForm.

        Args:
            **lang (str): The language.

        Returns:
            str: The full string of the XLSForm, ready to print or save.
        """
        lang = kwargs['lang'] if 'lang' in kwargs \
            else self.languages['languages_list']['default_language']
        title_lines = (
            '+{:-^50}+'.format(''),
            '|{:^50}|'.format(self.title),
            '+{:-^50}+'.format('')
        )
        title_box = '\n'.join(title_lines)

        q_text = (q.to_text(lang) for q in self.questionnaire)
        sep = '\n\n' + '=' * 52 + '\n\n'
        result = sep.join(q_text)
        return title_box + sep + result + sep # TODO: Finish below to_dict or
    # TODO: change debug feature. If fixed, change to_json to
    # TODO: call dump return of this method instead of raw data.

    # def to_dict(self, lang):
    #     """Get the dictionary representation of an entire XLSForm.
    #
    #     Args:
    #         lang (str): The language.
    #
    #     Returns:
    #         dict: A full dictionary representation of the XLSForm.
    #     """
    #     lang = lang if lang \
    #         else self.languages['languages_list']['default_language']
    #     html_questionnaire = {
    #         'title': self.title,
    #         'questions': []
    #     }
    #     for item in self.questionnaire:
    #         html_questionnaire['questions'].append(item.to_dict(lang))
    #     return html_questionnaire

    def to_json(self, pretty=False):
        """Get the JSON representation of raw ODK form.

        Args:
            pretty (bool): Activates prettification, involving insertion of
                several kinds of whitespace for readability.

        Returns:
            json: A full JSON representation of the XLSForm.
        """
        import json
        # lang = lang if lang \
        #     else self.languages['languages_list']['default_language']
        raw_survey = []
        header = self.metadata['raw_data']['survey'][0]
        for i, row in enumerate(self.metadata['raw_data']['survey']):
            if i == 0:
                continue
            raw_survey.append({str(k): str(v) for k, v in zip(header, row)})

        if pretty:
            return json.dumps(raw_survey, indent=2)
        else:
            return json.dumps(raw_survey)

    def to_html(self, **kwargs):
        """Get the JSON representation of an entire XLSForm.

        Args:
            **lang (str): The language.
            **highlight (bool): For color highlighting of various components
                of html template.
            **debug (bool): For inclusion of debug information to be printed
                in the JavaScript console.

        Returns:
            str: A full HTML representation of the XLSForm.
        """
        # Currently not logging conversion time.
        # conversion_start = datetime.datetime.now()
        lang = kwargs['lang'] if 'lang' in kwargs else \
            self.languages['languages_list']['default_language']
        html_questionnaire = ''
        data = {
            'header': {
                'title': self.title
            },
            'footer': {
                'data':
                    self.to_json(pretty=True) if kwargs['debug']
                    else 'false'
            },
            'questionnaire': self.questionnaire
        }
        # pylint: disable=no-member
        header = TEMPLATE_ENV.get_template('header.html')\
            .render(data=data['header'])
        # pylint: disable=no-member
        grp_spc = TEMPLATE_ENV\
            .get_template('content/group/group-spacing.html').render()
        html_questionnaire += header
        prev_item = None
        for index, item in enumerate(data['questionnaire']):
            if prev_item is not None and isinstance(item, OdkGroup):
                html_questionnaire += grp_spc
            elif isinstance(prev_item, OdkGroup) \
                    and not isinstance(item, OdkGroup):
                html_questionnaire += grp_spc
            if isinstance(item, OdkPrompt) and item.is_section_header and \
                    isinstance(data['questionnaire'][index+1], OdkGroup):
                html_questionnaire += item.to_html(lang, kwargs['highlight'],
                                                   bottom_border=True)
            else:
                html_questionnaire += item.to_html(lang, kwargs['highlight'])
            prev_item = item
        self.set_conversion_end()
        OdkForm.warnings = OdkForm.warnings if OdkForm.warnings is not None \
            else 'false'
        # Currently not logging conversion time.
        OdkForm.conversion_info = {} if OdkForm.conversion_info is 'false' \
            else OdkForm.conversion_info
        self.get_running_conversion_time()
        # pylint: disable=no-member
        footer = TEMPLATE_ENV.get_template('footer.html')\
            .render(info=OdkForm.conversion_info, warnings=OdkForm.warnings,
                    conversion_time=str(self.metadata['conversion_time']),
                    data=data['footer']['data'])
        html_questionnaire += footer
        return html_questionnaire

    @staticmethod
    def parse_select_type(row, choices, ext_choices):
        """Extract relevant information from a select_* ODK prompt.

        Build a dictionary that distills the main details of the row. The
        select type questions can have a token type of 'prompt' or 'table'.
        The prompt type is default, and table type is if the appearance of the
        question has either 'label' or 'list-nolabel'.

        Args:
            row (dict): A row as a dictionary. Keys and values are strings.
            choices (dict): A dictionary with list_names as keys. Represents
                the choices found in 'choices' tab.
            ext_choices (dict): A dictionary with list_names as keys.
                Represents choices found in 'external_choices' tab.

        Returns:
            A dictionary with the simple information about this prompt.

        Raises:
            OdkFormError: If the row is not select_[one|multiple](_external)?
            KeyError: If the select question's choice list is not found.
        """
        simple_row = {'token_type': 'prompt'}
        simple_type = 'select_one'
        row_type = row['type']
        if row_type.startswith('select_one_external '):
            list_name = row_type.split(maxsplit=1)[1]
            choice_list = ext_choices[list_name]
        elif row_type.startswith('select_multiple_external '):
            simple_type = 'select_multiple'
            list_name = row_type.split(maxsplit=1)[1]
            choice_list = ext_choices[list_name]
        elif row_type.startswith('select_one '):
            list_name = row_type.split(maxsplit=1)[1]
            choice_list = choices[list_name]
        elif row_type.startswith('select_multiple '):
            simple_type = 'select_multiple'
            list_name = row_type.split(maxsplit=1)[1]
            choice_list = choices[list_name]
        else:
            raise OdkFormError()

        simple_row['simple_type'] = simple_type
        simple_row['choice_list'] = choice_list

        appearance = row.get('appearance', '')
        if 'label' in appearance or 'list-nolabel' in appearance:
            simple_row['token_type'] = 'table'

        return simple_row

    @staticmethod
    def parse_group_repeat(row):
        """Extract relevant information about a begin/end group/repeat.

        Args:
            row (dict): A row as a dictionary. Keys and values are strings.

        Returns:
            A dictionary with the simple information about this prompt.

        Raises:
            OdkFormError: If type is not begin/end group/repeat.
        """
        row_type = row['type']
        token_type = row_type
        appearance = row.get('appearance', '')
        good = ('begin group', 'end group', 'begin repeat', 'end repeat')
        if row_type == 'begin group' and 'field-list' not in appearance:
            token_type = 'context group'
        elif row_type not in good:
            raise OdkFormError()
        simple_row = {'token_type': token_type}
        return simple_row

    @staticmethod
    def make_simple_prompt(row_type):
        """Extract relevant information from an ODK prompt.

        Make the simplest dictionary: token_type is set to 'prompt',
        simple_type is copied from the row type, and choices is set to None.

        Args:
            row_type (str): The type of the row.

        Returns:
            A dictionary with the simple information about this prompt.
        """
        simple_row = {
            'token_type': 'prompt',
            'simple_type': row_type,
            'choice_list': None
        }
        return simple_row

    @staticmethod
    def parse_type(row, choices, ext_choices):
        """Describe the 'type' column of a row XLSForm.

        Args:
            row (dict): A row as a dictionary. Keys and values are strings.
            choices (dict): A dictionary with list_names as keys. Represents
                the choices found in 'choices' tab.
            ext_choices (dict): A dictionary with list_names as keys.
                Represents choices found in 'external_choices' tab.

        Returns:
            dict: simple_row information from parsing.
        """
        row_type = row['type']
        simple_types = OdkPrompt.response_types + OdkPrompt.non_response_types
        if row_type in simple_types:
            simple_row = OdkForm.make_simple_prompt(row_type)
        elif row_type.startswith('select_'):
            simple_row = OdkForm.parse_select_type(row, choices, ext_choices)
        elif row_type.startswith('begin ') or row_type.startswith('end '):
            simple_row = OdkForm.parse_group_repeat(row)
        else:  # Note - Some unhandled token types remain.
            simple_row = {'token_type': 'unhandled', 'simple_type': row_type}
        return simple_row

    @staticmethod
    def convert_survey(wb, choices, ext_choices):
        """Convert rows and strings of a workbook into object components.

        Main types are:

        - prompt
        - begin group
        - end group
        - begin repeat
        - end repeat
        - table
        - context group (group without field-list appearance)

        Args:
            wb (Workbook): A Workbook object representing an XLSForm.

        Returns:
            list: A list of objects representing form components.

        Raises:
            OdkformError: Handle several errors, including: mismatched groups
                or repeat groups, errors when appending to groups or repeat
                groups, erroneously formed tables, duplicate context group
                names, and groups nested within a field-list group.
        """
        context = OdkForm.ConversionContext()
        try:
            survey = wb['survey']
            header = survey[0]

            for i, row in enumerate(survey):
                if i == 0:
                    continue
                dict_row = {str(k): str(v) for k, v in zip(header, row)}
                token = OdkForm.parse_type(dict_row, choices, ext_choices)

                if token['token_type'] == 'prompt':
                    dict_row['simple_type'] = token['simple_type']
                    choice_list = token['choice_list']
                    this_prompt = OdkPrompt(dict_row, choice_list)
                    context.add_prompt(this_prompt)
                elif token['token_type'] == 'begin group':
                    this_group = OdkGroup(dict_row)
                    context.add_group(this_group)
                elif token['token_type'] == 'context group':
                    # Possibly make an OdkGroup here...
                    context.add_context_group()
                elif token['token_type'] == 'end group':
                    context.end_group()
                elif token['token_type'] == 'begin repeat':
                    this_repeat = OdkRepeat(dict_row)
                    context.add_repeat(this_repeat)
                elif token['token_type'] == 'end repeat':
                    context.end_repeat()
                elif token['token_type'] == 'table':
                    dict_row['simple_type'] = token['simple_type']
                    choice_list = token['choice_list']
                    this_prompt = OdkPrompt(dict_row, choice_list)
                    context.add_table(this_prompt)
                elif token['token_type'] == 'unhandled':
                    # Intentionally no handling for these types.
                    # possibly start logging
                    pass
                else:
                    # make an error
                    pass
        except KeyError:  # No survey found.
            pass
        return context.result

    class ConversionContext:
        """A class to help questionnaire conversion.

        This class is the context during questionnaire conversion. It
        remembers state, adds components in the correct order, and enforces
        rules during conversion.

        Instance attributes:
            result (list): The list of survey components that is built up
            pending_stack (list): A stack for tracking nested groups and
                repeats.
            group_stack (list): A stck for tracking nested groups and context
                groups.
        """

        def __init__(self):
            """Initialize a conversion context before parsing."""
            self.result = []
            self.pending_stack = []
            self.group_stack = []

        def add_prompt(self, prompt):
            """Add a prompt to the questionnaire.

            If there is an item on the pending stack, it is added there,
            otherwise it is added to the list of components.

            Args:
                prompt (OdkPrompt): A prompt to add.
            """
            if self.pending_stack:
                self.pending_stack[-1].add(prompt)
            else:
                self.result.append(prompt)

        def add_group(self, group):
            """Add a group to the pending stack.

            A group can be added to the pending stack as long as it is empty
            or the last pending stack item is a repeat. This is triggered by a
            'begin group' row with a 'field-list' in the appearance.

            Args:
                group (OdkGroup): The group to add to the pending stack.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if self.pending_stack:
                last = self.pending_stack[-1]
                if isinstance(last, OdkGroup):
                    msg = 'Groups cannot be nested in each other.'
                    raise OdkFormError(msg)
            self.pending_stack.append(group)
            self.group_stack.append(group)

        def add_context_group(self):
            """Add a context group to the group stack.

            Context groups are tracked only to help popping groups correctly
            from the pending stack.
            """
            self.group_stack.append(None)

        def end_pending_group(self):
            """End a pending group.

            A pending group is a group on the pending stack. This is not a
            context group. This function is only called internally in response
            to receiving and dealing with an 'end group' type.

            If the pending group is nested in a repeat, then it is added to
            that repeat.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if self.pending_stack:
                last_pending = self.pending_stack.pop()
                if not isinstance(last_pending, OdkGroup):
                    msg = 'Found end group but no group in pending stack'
                    raise OdkFormError(msg)
                last_pending.add_pending()
                if self.pending_stack:
                    self.pending_stack[-1].add(last_pending)
                else:
                    self.result.append(last_pending)
            else:
                msg = 'Found end group but nothing pending stack.'
                raise OdkFormError(msg)

        def end_group(self):
            """Finish a group after seeing 'end group' type.

            The 'end group' type can finish a field-list group or a context
            group. This function handles the logic for finishing both types.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if self.group_stack:
                last_group = self.group_stack.pop()
                if isinstance(last_group, OdkGroup):
                    self.end_pending_group()
            else:
                msg = 'Begin/end group mismatch'
                raise OdkFormError(msg)

        def add_repeat(self, repeat):
            """Add a repeat to the pending stack.

            The pending stack must first be empty because a repeat cannot be
            nested in a group or other repeat.

            Args:
                repeat (OdkRepeat): The repeat to deal with.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if not self.pending_stack:
                self.pending_stack.append(repeat)
            else:
                msg = 'Unable to nest repeat inside a group or repeat.'
                raise OdkFormError(msg)

        def end_repeat(self):
            """Finish a repeat in this questionniare.

            A repeat can be ended only if it is first on the pending stack.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if self.pending_stack:
                last_pending = self.pending_stack.pop()
                if isinstance(last_pending, OdkRepeat):
                    self.result.append(last_pending)
                else:
                    msg = 'Found end repeat but no repeat in pending stack.'
                    raise OdkFormError(msg)
            else:
                msg = 'Found end repeat but nothing in pending stack.'
                raise OdkFormError(msg)

        def add_table(self, prompt):
            """Add a table row to the questionnaire.

            The table can only be added if there is a group on the pending
            stack.

            Args:
                prompt (OdkPrompt): The prompt representing the table row.

            Raises:
                OdkFormError: If the parsing rules are broken based on the
                    current context.
            """
            if self.pending_stack:
                last_pending = self.pending_stack[-1]
                if not isinstance(last_pending, OdkGroup):
                    msg = 'A table can only be in a group.'
                    raise OdkFormError(msg)
                last_pending.add_table(prompt)
            else:
                msg = 'A table can only be in a group, no group found.'
                raise OdkFormError(msg)
