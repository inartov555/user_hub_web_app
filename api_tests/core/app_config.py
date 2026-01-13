"""
App config from the pytest.ini config file
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    """
    App config from ini config file
    """
    base_url: str
    admin_user_login: str
    admin_user_password: str
    regular_user_login: str
    regular_user_password: str
