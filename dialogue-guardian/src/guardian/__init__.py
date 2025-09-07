"""
Dialogue Guardian: Universal Media Censor

A Python package for automatically detecting and censoring profane language 
in video files by processing SRT subtitle files.
"""

__version__ = "1.1.0"
__author__ = "Tony Snearly"

from .core import GuardianProcessor
from .cli import main

__all__ = ["GuardianProcessor", "main"]