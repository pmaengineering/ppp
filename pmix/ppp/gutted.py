"""Gutted language stuff."""


@staticmethod
def get_worksheet_languages(header):
    """Get worksheet languages.

    Args:
        header (list): Worksheet header; list of Cell objects.

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
                    lang_fields[lang_field]['has_generic_language_field'] \
                        = True
                else:
                    lang = str(field)[len(lang_field + '::'):]
                    lang_fields[lang_field]['language_list'].append(lang)
    for field, data in lang_fields.items():
        data['language_list'] = sorted(data['language_list'])
    return lang_fields


@staticmethod
def check_for_bad_default_language(default_lang, ws_info):
    """Check for erroneous default language.

    Args:
        default_lang (str): The default language listed in XlsForm.
        ws_info (dict): Parsed information on XlsForm worksheets.

    Raises:
        InvalidLanguageException: If erroneous default language.

    >>> from pmix.ppp.odkform import OdkForm
    >>> OdkForm.check_for_bad_default_language(default_lang='Huh?',
    ... ws_info={'choices': {'language_fields': {'label': {'language_list':
    ... ['a', 'b', 'c']}}}}) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    InvalidLanguageException
    """
    err_msg = 'InvalidLanguageException: Erroneous default language.\n' \
              'The default language \'{}\' was not found in the \'{}\' ' \
              'field of the \'{}\' worksheet.'
    for worksheet in ws_info:
        if worksheet in LANGUAGE_PERTINENT_WORKSHEETS:
            for field, field_info \
                    in ws_info[worksheet]['language_fields'].items():
                if default_lang not in field_info['language_list']:
                    err = err_msg.format(default_lang, field, worksheet)
                    raise InvalidLanguageException(err)


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
    for dummy, v in ws_lang_fields.items():
        if v['has_generic_language_field'] is True:
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


def get_general_language_info(self, wb):
    """Consolidate language information for ODK form.

    Consolidate pertinent language information, such as languages list for
    relevant worksheets. Side Effects are (1) self.
    languages['generic_language_fields_present']: True if generic, (2)
    language field is found in any language field.

    Args:
        wb (Xlsform): Wb.

    Returns:
        dict: Dictionary of general information on form language.
    """
    workbook_languages = {'worksheets': {}}

    for ws in LANGUAGE_PERTINENT_WORKSHEETS:
        if ws in [ws.name for ws in wb.data]:
            workbook_languages['worksheets'][ws] = {
                'language_fields': self.get_worksheet_languages(wb[ws][0]),
                'label_language_list': [],
                'has_generic_language_field': bool()
            }
            ws_data = workbook_languages['worksheets'][ws]
            wslf = ws_data['language_fields']
            ws_data['label_language_list'] = \
                self.get_label_language_list(wslf)
            ws_data['has_generic_language_field'] = \
                self.check_generic_language_fields(wslf)

    return workbook_languages


def check_language_exceptions(self, settings, languages):
    """Check for various language related exceptions.

    Args:
        settings (dict): A dictionary representation of the original
        'settings' worksheet of an ODK XLSForm.
        languages (dict): Form language information rendered on
            initialization.

    Raises:
        InvalidLanguageException: Various.

    >>> from test.test_ppp import MockForm
    >>> MockForm(
    ... mock_file='exceptions/language/ambiguous-default-language.xlsx'
    ... ) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    AmbiguousLanguageError
    """
    self.check_for_bad_default_language(
        default_lang=languages['default_language'],
        ws_info=languages['general_language_info']['worksheets'])

    settings_default = settings['default_language'] \
        if 'default_language' in settings \
           and settings['default_language'] else None

    if settings_default:
        if languages['has_generic_language_field']:
            msg = 'AmbiguousLanguageError: Ambiguous default language.' \
                  ' A \'default_language\' has been specified in the ' \
                  'form settings, but one or more worksheets contains ' \
                  'language-dependent fields that are language agnostic,' \
                  ' e.g. \'label\' rather than \'label::<some language>' \
                  '\'.\n\nPlease correct the issue by using one or the ' \
                  'other, but not both: default language, or language ' \
                  'agnostic language-dependent fields.\n\n' \
                  '* Language-dependent fields: ' + \
                  str(LANGUAGE_DEPENDENT_FIELDS)
            raise AmbiguousLanguageError(msg)
    else:
        # TODO: Handle the following cases, both with (1) cases of a
        # TODO: presence of 'default_language', and (2) not.
        # * A 'label' field by itself on both sheets.
        #   * w/ no default lang given and lang specifics in other fields
        # * Inconsistent 'label' 'label::' in worksheets.
        # * A 'label' field when default_language is listed. Did I do yet?
        #
        # * A 'label' field with 'label::' fields on both sheets, and
        # there is no default language.
        #    * ODK should allow this. So this is ok.
        pass


@staticmethod
# def get_languages(settings_default, lang_info):  # noqa: D207
def get_languages(settings_default, wb):  # noqa: D207
    r"""Get survey languages.

    Args:
        settings_default (str): Default language of form, if specified.
        wb (Xlsform): Wb.

    Returns:
        list: An alphabetically sorted list of languages in the form.
    >>> from test.test_ppp import MockForm
    >>> form = MockForm(mock_file='no-errors.xlsx')
    >>> form.get_languages(settings_default='English', wb=
    ... form.metadata['raw_data']) #doctest: +ELLIPSIS
    ['Ateso', 'English', 'Luganda', ... 'Runyoro-Rutoro']

    Raises:
        InconsistentLabelLanguage: Label languages not match between WS.
    >>> from test.test_ppp import MockForm
    >>> MockForm(mock_file=
    ... 'exceptions/language/InconsistentLabelLanguage.xlsx'
    ... ) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    InconsistentLabelLanguage
    """

    def get_ws_langs(a_wb, an_lpws):
        """Get WS languages.

        Args:
            a_wb (Xlsform): Wb.
            an_lpws (str): A language-pertinent worksheet.

        Returns:
            list: An alphabetically sorted list of languages in the form.
        """
        lang_set = set()
        for header_field in a_wb[an_lpws][0]:
            if header_field == 'label':
                if settings_default:
                    raise InvalidLanguageException
                lang_set.add('')  # Default lang. Does anything?
            elif str(header_field).startswith('label::'):
                lang = str(header_field)[len('label::'):]
                lang_set.add(lang)
        return sorted(list(lang_set))

    err_msg = 'InconsistentLabelLanguage: The languages present for the ' \
              'label field do not match between 2 or more worksheets. ' \
              'Please ensure they match and try again.'
    lang_list = []
    label_languages = {ws.name: [] for ws in wb if ws.name
                       in LANGUAGE_PERTINENT_WORKSHEETS}

    for lpws in LANGUAGE_PERTINENT_WORKSHEETS:
        for ws in wb:
            if lpws == ws.name:
                sorted_ws_langs = get_ws_langs(a_wb=wb, an_lpws=lpws)
                label_languages[ws.name] = sorted_ws_langs
                if not lang_list:
                    lang_list = sorted_ws_langs.copy()
                else:
                    if sorted_ws_langs != lang_list:
                        err_msg = err_msg + '\nWS Label Languages: ' \
                                  + str(label_languages)
                        raise InconsistentLabelLanguage(err_msg)

    # return label_languages
    return lang_list


@staticmethod
def get_default_language(settings_default, language_list):
    """Get default survey language if specified.

    Args:
        settings_default (str): Default language of form, if specified.
        language_list (list): Sorted list of languages in form.

    Returns:
        str: The default language of the form.
    # If default language in form settings.
    >>> from pmix.ppp.odkform import OdkForm
    >>> OdkForm.get_default_language(settings_default='Russian',
    ... language_list=['Ateso', 'English', 'Luganda', 'Luo', 'Russian'])
    'Russian'

    # If no default language in form settings.
    >>> OdkForm.get_default_language(settings_default='',
    ... language_list=['Ateso', 'English', 'Luganda', 'Luo', 'Russian'])
    'Ateso'

    Raises:
        InvalidLanguageException: Default language not found in survey WS.
    >>> OdkForm.get_default_language(settings_default='z', language_list=
    ... ['a', 'b', 'c', 'd', 'e']) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    InvalidLanguageException
    """
    default = settings_default \
        if settings_default and settings_default is not None \
        else language_list[0]
    if default not in language_list:
        msg = 'InvalidLanguageException: \'default_language\' specified ' \
              'was not found in \'survey\' worksheet.'
        raise InvalidLanguageException(msg)
    return default

    # languages_template = {
    #     'general_language_info': {
    #         'worksheets': {
    #             '<worksheet>': {
    #                 'language_fields': {
    #                     'has_generic_language_field': bool(),
    #                     'label_language_list': [
    #                         '<language>',
    #                     ],
    #                     '<field>': {
    #                         'has_generic_language_field': bool(),
    #                         'language_list': [
    #                             '<language>',
    #                         ],
    #                     },
    #                 }
    #             }
    #         }
    #     },
    #     'default_language': None,
    #     'has_generic_language_field': bool(),
    #     'language_list': [],
    # }