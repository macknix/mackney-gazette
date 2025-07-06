"""
Utility modules for data operations.

This package provides comprehensive data generation capabilities including:
- PeopleGenerator: Generate realistic demographic data
- TownGenerator: Generate complete town infrastructure data
"""

from .generate_people import PeopleGenerator
from .generate_town import TownGenerator

__all__ = ['PeopleGenerator', 'TownGenerator']
