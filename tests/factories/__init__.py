"""
Test factories package for centralized mock creation.

This package provides reusable mock factories and test data generators
for all service classes and Pydantic schemas in the application.
"""

from .mock_factory import MockFactory

__all__ = ["MockFactory"]