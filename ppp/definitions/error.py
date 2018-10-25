"""Error classes for package."""


class OdkException(Exception):
    """General ODK exception."""


class OdkFormError(OdkException):
    """General OdkForm error."""


class OdkChoicesError(OdkException):
    """General OdkChoices error."""


class InvalidLanguageException(OdkException):
    """General error related to language of ODK form."""


class AmbiguousLanguageError(InvalidLanguageException):
    """Ambiguous language error."""


class InconsistentLabelLanguage(InvalidLanguageException):
    """Inconsistent label language error."""
