"""
App config from ini config file
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:  # pylint: disable=too-many-instance-attributes
    """
    App config from ini config file
    """
    wait_to_handle_capture_manually: bool
    action_timeout: int
    navigation_timeout: int
    assert_timeout: int
    browser: str
    base_url: str
    is_headless: bool
    width: int
    height: int
    username: str
    password: str
