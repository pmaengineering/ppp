"""Error classes for package."""


class OdkFormError(Exception):
    """General OdkForm error."""

    pass

class OdkChoicesError(Exception):
    """General OdkChoices error."""

    pass


class InvalidLanguageException(OdkFormError):
    """For errors related to language of ODK form."""

    pass
