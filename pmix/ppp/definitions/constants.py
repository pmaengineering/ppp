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
IGNORE_RELEVANT_TOKEN = '#####'
SUPPORTED_FORMATS = ('html', 'doc')
LANGUAGE_PERTINENT_WORKSHEETS = ('survey', 'choices', 'external_choices')
MEDIA_FIELDS = ('image', 'media::image', 'audio', 'media::audio',
                'video', 'media::video')
LANGUAGE_DEPENDENT_FIELDS = \
    ('label', 'hint', 'constraint_message', 'ppp_input') + MEDIA_FIELDS
TRUNCATABLE_FIELDS = ('constraint', 'relevant')
MULTI_ARGUMENT_CONVERSION_OPTIONS = ('preset', 'format', 'language')
PRESETS = {
    'full': {  # Alias for 'developer'.
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
    'developer': {  # Alias for 'full'.
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
