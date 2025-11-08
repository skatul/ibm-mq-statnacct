"""
IBM MQ Statistics and Accounting Queue Reader

This package provides functionality to read IBM MQ statistics and accounting data,
identify queue readers and writers, and output structured data with timestamps
suitable for time series databases.

Author: GitHub Copilot
Date: November 2025
"""

from .mq_stats_reader import MQStatsReader
from .pcf_parser import PCFParser
from . import config

__version__ = "1.0.0"
__all__ = ["MQStatsReader", "PCFParser", "config"]