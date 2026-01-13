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
    base_port: str
    base_api_uri: str
