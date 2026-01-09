"""
Logger
"""

import logging
import logging.config
import os
import sys


class Logger:
    """
    Logger
    """
    __file_handler = None
    __cli_handler = None
    __loggers = []  # links to all created loggers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self, logger_name: str):
        """
        Wrapper over logging class that initializes a logger with the config in 'tools/logger/logging.json'.
        To modify default log level edit in 'tools/logger/logging.json' the parameter json['handlers']['console']['info']
        Logging path is LOG_PATH if defined, else the project root directory.

        Args:
            logger_name (str): although any name can be used, it's recommended to use __name__ python variable
        """
        # creating logger
        if not logger_name.startswith("test"):
            logger_name = f"test.{logger_name}"
        self.__logger = logging.getLogger(logger_name)
        if self.__logger not in Logger.__loggers:
            Logger.__loggers.append(self.__logger)

    def info(self, message: str) -> None:
        """
        INFO log line
        """
        self.__logger.info(message)

    def debug(self, message: str) -> None:
        """
        DEBUG log line
        """
        self.__logger.debug(message)

    def error(self, message: str) -> None:
        """
        ERROR log line
        """
        self.__logger.error(message)

    def warning(self, message: str) -> None:
        """
        WARNING log line
        """
        self.__logger.warning(message)

    def __update_handler(self, logr, handlr) -> None:
        """
        Update the logger's handler with the new log level.
        The method will get all handlers of the logger and change the level
        of the existing logger if the handler is already set up for the logger

        Args:
            logr (logger): logger to be updated
            handlr (handler): handler with required level and config
        """
        for hdlr in logr.handlers:
            if hdlr.name == handlr.name:
                hdlr.level = handlr.level
                break
        else:
            logr.addHandler(handlr)

    def __get_file_handler(self, level: str, file_name: str) -> logging.Handler:
        """
        Method to create a file handler or get it from a cache

        Args:
            level (str): level name
            file_name (str): logger file name

        Returns:
            handler
        """
        if not Logger.__file_handler:
            file_handler = logging.FileHandler(file_name)
            formatter = logging.Formatter(self.log_format)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            file_handler.name = "main_log_file"
            Logger.__file_handler = file_handler
        return Logger.__file_handler

    def __get_cli_handler(self, level: str) -> logging.Handler:
        """
        Method to create a Stream handler or get it from a cache

        Args:
            level (str): level name

        Returns:
            handler
        """
        if not Logger.__cli_handler:
            formatter = logging.Formatter(self.log_format)
            cli_handler = logging.StreamHandler(sys.stdout)
            cli_handler.setFormatter(formatter)
            cli_handler.setLevel(level)
            cli_handler.name = "console"
            Logger.__cli_handler = cli_handler
        return Logger.__cli_handler

    def setup_cli_handler(self, level: str) -> None:
        """
        Method to set up a CLI handler for a particular logger or all available loggers
        If the CLI handler was set up for all loggers, then all new loggers  will be created with the same config

        Args:
            level (str/int): level for the file handler
        """
        cli_handler = self.__get_cli_handler(level)
        root_logger = logging.getLogger()
        self.__update_handler(root_logger, cli_handler)
        root_logger.setLevel(min(cli_handler.level, root_logger.level))

    def setup_filehandler(self, file_name: str, level: str = "DEBUG") -> None:
        """
        Method to set up a file handler for a particular logger or all available loggers
        If the file handler was set up for all loggers, then all new loggers will be created with the same config

        Args:
            file_name (str): path where logs should be stored
            level: (str/int): level for the file handler
            logger_name (str): name of the logger file handler to be applied for
        """
        root_logger = logging.getLogger()
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        loggers_list = []
        loggers_list.append(root_logger)
        file_handler = self.__get_file_handler(level, file_name)
        for logger in loggers_list:
            self.__update_handler(logger, file_handler)
        root_logger.setLevel(min(file_handler.level, root_logger.level))
