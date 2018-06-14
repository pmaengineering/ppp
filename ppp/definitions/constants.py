"""A list of reusable constants for the package.

MEDIA_FIELDS (tuple): Fields that can be set to file names of allowable
    media types for the given field.
LANGUAGE_DEPENDENT_FIELDS (tuple): Fields for which values can vary by
    language. A single ODK XLSForm can have many such fields, suffixed
    by '::language'.
TRUNCATABLE_FIELDS (tuple): Fields that should be limited to a specific
    length. Current limit is 100 chars, which is somewhat arbitrary but
    turns out good in converted forms.
"""
SYNTAX = {
    'xlsforms': {
        'language_field_delimiters': [':', '::']
    }
}
IGNORE_RELEVANT_TOKEN = '#####'
SUPPORTED_FORMATS = ('html', 'doc')
LANGUAGE_PERTINENT_WORKSHEETS = ('survey', 'choices', 'external_choices')
XLSFORM_SUPPORTED_MULTIMEDIA_TYPES = ['image', 'audio', 'video']
# MEDIA_FIELDS = (image, media:image, media::image, ...)
MEDIA_FIELDS = tuple(x for x in XLSFORM_SUPPORTED_MULTIMEDIA_TYPES) + \
   tuple('media' + y + x for x in XLSFORM_SUPPORTED_MULTIMEDIA_TYPES
         for y in SYNTAX['xlsforms']['language_field_delimiters'])
# for x in XLSFORM_SUPPORTED_MULTIMEDIA_TYPES:
#     MEDIA_FIELDS.append(x)
#     for y in SYNTAX['xlsforms']['language_field_delimiters']:
#         MEDIA_FIELDS.append('media' + y + x)
LANGUAGE_DEPENDENT_FIELDS = \
    ('label', 'hint', 'constraint_message', 'ppp_input') + MEDIA_FIELDS
TRUNCATABLE_FIELDS = ('constraint', 'relevant')
MULTI_ARGUMENT_CONVERSION_OPTIONS = ('preset', 'format', 'language')
PRESETS = {
    'full': {
        'field_replacements': (),
        'field_exclusions': (),
        'other_specific_exclusions': (),
        'general_exclusions': False,
        'render_settings': {
            'html': {
                'side_letters': True
            }
        }
    },
    'internal': {
        'field_replacements': (),
        'field_exclusions': (),
        'other_specific_exclusions': (),
        'general_exclusions': False,
        'render_settings': {
            'html': {
                'side_letters': True
            }
        }
    },
    'minimal': {
        'field_replacements': ('label', 'relevant'),
        'field_exclusions':
            ('constraint', 'constraint_message', 'name', 'type'),
        'other_specific_exclusions': ('choice names',),
        'general_exclusions': True,
        'render_settings': {
            'html': {
                'side_letters': False
            }
        }
    },
    'public': {
        'field_replacements': (),
        'field_exclusions': (),
        'other_specific_exclusions': (),
        'general_exclusions': False,
        'render_settings': {
            'html': {
                'side_letters': True
            }
        }
    },
}
PRESETS['developer'] = PRESETS['full']  # alias
PRESETS['standard'] = PRESETS['minimal']  # alias
PRESETS['basic'] = PRESETS['minimal']  # alias
