"""
File utilities
"""

import os
from datetime import datetime

from utils.logger.logger import Logger


class FileUtils:
    """
    File utilities
    """
    log = Logger(__name__)

    @classmethod
    def timestamped_path(cls, file_name, file_ext, path_to_file=os.getenv("HOST_ARTIFACTS")):
        """
        Args:
            file_name (str): e.g. screenshot
            file_ext (str): file extention, e.g., png
            path_to_file (str): e.g. /home/user/test_dir/artifacts/
        """
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")
        screenshot_path = os.path.join(path_to_file, f"{file_name}-{ts}.{file_ext}")
        cls.log.info(f"Screenshot path: {screenshot_path}")
        return screenshot_path

    @staticmethod
    def ensure_dir(path: str) -> None:
        """
        Creating directories forcely
        """
        os.makedirs(path, exist_ok=True)
