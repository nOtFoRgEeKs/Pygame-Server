import logging
import logging.config

logging.config.fileConfig(fname='logger/.conf', disable_existing_loggers=True)


class Logger:

    def __init__(self, name: str):
        self._msg_sep = ' '
        self._tag = ''
        self._logger = logging.getLogger(name)

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        self._tag = '[' + tag + '] '

    def _prepare_msg(self, *args):
        msg = [str(arg) for arg in args]
        return self._tag + self._msg_sep.join(msg)

    def debug(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.debug(message, **kwargs)

    def info(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.info(message, **kwargs)

    def warning(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.warning(message, **kwargs)

    def error(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.error(message, **kwargs)

    def critical(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.critical(message, **kwargs)

    def exception(self, *msg, **kwargs):
        message = self._prepare_msg(*msg)
        self._logger.exception(message, **kwargs)
