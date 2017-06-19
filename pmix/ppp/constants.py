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
MEDIA_FIELDS = ('image', 'media::image', 'audio', 'media::audio',
                'video', 'media::video')
LANGUAGE_DEPENDENT_FIELDS = \
    ('label', 'hint', 'constraint_message', 'ppp_input') + MEDIA_FIELDS
TRUNCATABLE_FIELDS = ('constraint', 'relevant')
