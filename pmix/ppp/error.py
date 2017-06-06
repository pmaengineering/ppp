"""Error classes for package."""


class OdkFormError(Exception):
    """General Odkform error."""

    pass


class InvalidLanguageException(OdkFormError):
    """For errors related to language of ODK form."""

    pass
