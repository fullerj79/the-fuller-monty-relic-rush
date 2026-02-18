"""
utils/logger.py

Author: Jason Fuller

Structured, colored logging utility with call-site tracing.

Responsibilities:
- Provide a lightweight, dependency-free logging facility
- Emit structured, human-readable logs with call-site context
- Support consistent logging semantics across all application layers
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library
# ------------------------------------------------------------------

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any
import inspect
import os


# ------------------------------------------------------------------
# Log levels
# ------------------------------------------------------------------

class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARN = auto()
    ERROR = auto()


# ------------------------------------------------------------------
# Global log level configuration
# ------------------------------------------------------------------

def _resolve_default_log_level() -> LogLevel:
    """
    Resolve the default log level from environment configuration.

    Environment variable:
        APP_LOG_LEVEL = DEBUG | INFO | WARN | ERROR

    Defaults:
        INFO (safe for production)
    """
    raw = os.getenv("APP_LOG_LEVEL", "INFO").upper()

    try:
        return LogLevel[raw]
    except KeyError:
        return LogLevel.INFO


DEFAULT_LOG_LEVEL: LogLevel = _resolve_default_log_level()


# ------------------------------------------------------------------
# ANSI color helpers
# ------------------------------------------------------------------

class Ansi:
    RESET = "\033[0m"
    GRAY = "\033[90m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"


# ------------------------------------------------------------------
# Call-site capture
# ------------------------------------------------------------------

@dataclass(frozen=True)
class CallSite:
    """
    Represents the precise location that triggered a log call.
    """

    file: str
    function: str
    line: int

    @property
    def short(self) -> str:
        fname = self.file.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return f"{fname}:{self.line}::{self.function}()"


def _resolve_callsite(skip: int = 3) -> CallSite:
    stack = inspect.stack()
    idx = min(skip, len(stack) - 1)
    frame = stack[idx]

    return CallSite(
        file=frame.filename,
        function=frame.function,
        line=frame.lineno,
    )


# ------------------------------------------------------------------
# Log style strategies
# ------------------------------------------------------------------

class LogStyle(ABC):
    level: LogLevel
    color: str
    label: str

    @abstractmethod
    def format(
        self,
        *,
        logger_name: str,
        site: CallSite,
        timestamp: str,
        message: str,
        fields: dict[str, Any],
    ) -> str:
        raise NotImplementedError


class DebugStyle(LogStyle):
    level = LogLevel.DEBUG
    color = Ansi.GRAY
    label = "DEBUG"

    def format(self, *, logger_name, site, timestamp, message, fields):
        return _format_line(self, logger_name, site, timestamp, message, fields)


class InfoStyle(LogStyle):
    level = LogLevel.INFO
    color = Ansi.BLUE
    label = "INFO"

    def format(self, *, logger_name, site, timestamp, message, fields):
        return _format_line(self, logger_name, site, timestamp, message, fields)


class WarnStyle(LogStyle):
    level = LogLevel.WARN
    color = Ansi.YELLOW
    label = "WARN"

    def format(self, *, logger_name, site, timestamp, message, fields):
        return _format_line(self, logger_name, site, timestamp, message, fields)


class ErrorStyle(LogStyle):
    level = LogLevel.ERROR
    color = Ansi.RED
    label = "ERROR"

    def format(self, *, logger_name, site, timestamp, message, fields):
        return _format_line(
            self,
            logger_name,
            site,
            timestamp,
            message,
            fields,
            bold=True,
        )


def _format_line(
    style: LogStyle,
    logger_name: str,
    site: CallSite,
    timestamp: str,
    message: str,
    fields: dict[str, Any],
    *,
    bold: bool = False,
) -> str:
    parts: list[str] = []

    for key, value in fields.items():
        try:
            parts.append(f"{key}={value!r}")
        except Exception:
            parts.append(f"{key}=<unreprable>")

    suffix = f" | {' '.join(parts)}" if parts else ""
    prefix = f"[{style.label}] {logger_name} | {site.short} | {timestamp} | {message}"

    if bold:
        return f"{Ansi.BOLD}{style.color}{prefix}{suffix}{Ansi.RESET}"

    return f"{style.color}{prefix}{suffix}{Ansi.RESET}"


_STYLES: dict[LogLevel, LogStyle] = {
    LogLevel.DEBUG: DebugStyle(),
    LogLevel.INFO: InfoStyle(),
    LogLevel.WARN: WarnStyle(),
    LogLevel.ERROR: ErrorStyle(),
}


# ------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------

class Logger:
    """
    Lightweight structured logger with call-site tracing.
    """

    def __init__(self, name: str, *, min_level: LogLevel = DEFAULT_LOG_LEVEL):
        self._name = name
        self._min_level = min_level

    def _emit(self, level: LogLevel, message: str, **fields: Any) -> None:
        if level.value < self._min_level.value:
            return

        site = _resolve_callsite()
        style = _STYLES[level]
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        print(
            style.format(
                logger_name=self._name,
                site=site,
                timestamp=timestamp,
                message=message,
                fields=fields,
            )
        )

    def debug(self, message: str, **fields: Any) -> None:
        self._emit(LogLevel.DEBUG, message, **fields)

    def info(self, message: str, **fields: Any) -> None:
        self._emit(LogLevel.INFO, message, **fields)

    def warn(self, message: str, **fields: Any) -> None:
        self._emit(LogLevel.WARN, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit(LogLevel.ERROR, message, **fields)


# ------------------------------------------------------------------
# Logger factory
# ------------------------------------------------------------------

def get_logger(name: str, *, min_level: LogLevel | None = None) -> Logger:
    """
    Logger factory.

    If min_level is not provided, DEFAULT_LOG_LEVEL is used.
    """
    return Logger(name, min_level=min_level or DEFAULT_LOG_LEVEL)
