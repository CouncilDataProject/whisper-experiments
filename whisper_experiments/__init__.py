# -*- coding: utf-8 -*-

"""Top-level package for whisper_experiments."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("whisper-experiments")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Eva Maxfield Brown"
__email__ = "evamaxfieldbrown@gmail.com"
