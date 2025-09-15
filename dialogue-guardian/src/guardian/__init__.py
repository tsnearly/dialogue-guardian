# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Dialogue Guardian: Universal Media Censor

A Python package for automatically detecting and censoring profane language
in video files by processing SRT subtitle files.
"""

__version__ = "1.1.4"
__author__ = "Tony Snearly"

from .cli import main
from .core import GuardianProcessor

__all__ = ["GuardianProcessor", "main"]
