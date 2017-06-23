"""Error classes for package."""


class OdkFormError(Exception):
    """General OdkForm error."""

    pass


class OdkChoicesError(Exception):
    """General OdkChoices error."""

    pass


class InvalidLanguageException(OdkFormError):
    """General error related to language of ODK form."""

    pass


class AmbiguousLanguageError(InvalidLanguageException):
    """Ambiguous language error."""

    pass
