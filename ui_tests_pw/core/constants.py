"""
Constants
"""

class LocaleConsts:
    """
    Locale constants
    """
    ENGLISH_US = "en-US"
    UKRAINIAN= "uk-UA"
    ESTONIAN = "et-EE"
    FINNISH = "fi-FI"
    CZECH = "cs-CZ"
    POLISH = "pl-PL"
    SPANISH = "es-ES"

    # Locales available in the website
    ALL_AVAILABLE_LOCALES = [ENGLISH_US, UKRAINIAN, ESTONIAN, FINNISH, CZECH, POLISH, SPANISH]
    # Locales supported by the automation framework for testing
    ALL_SUPPORTED_LOCALES = ALL_AVAILABLE_LOCALES


class ThemeConsts:
    """
    Theme constants
    """
    LIGHT = "light"
    DARK = "dark"

    # Themes available in the website
    ALL_AVAILABLE_THEMES = [LIGHT, DARK]
    # Themes supported by the automation framework for testing
    ALL_SUPPORTED_THEMES = ALL_AVAILABLE_THEMES
