"""
Unit tests
"""

from core.settings import *

# Testing if Settings object can be initialized
if LANGUAGE_CODE != "en-us":
    raise AssertionError(f"Default language is not en-us; current value: {LANGUAGE_CODE}")
