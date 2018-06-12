"""Error classes for package."""


class OdkException(Exception):
    """General ODK exception."""

    pass


class OdkFormError(OdkException):
    """General OdkForm error."""

    pass


class OdkChoicesError(OdkException):
    """General OdkChoices error."""

    pass


class InvalidLanguageException(OdkException):
    """General error related to language of ODK form."""

    pass


class AmbiguousLanguageError(InvalidLanguageException):
    """Ambiguous language error."""

    pass


class InconsistentLabelLanguage(InvalidLanguageException):
    """Inconsistent label language error."""

    pass
