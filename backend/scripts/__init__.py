"""Database population and querying utilities for Culicidae Lab.

This module contains scripts for populating LanceDB with sample data
and querying existing database tables. It provides functionality for
initializing database tables with species, diseases, observations,
regions, and other related data.

The scripts in this module are designed to work with the LanceDB
database system and follow the schema definitions provided by
the database_utils module.

Example:
    To populate the database with sample data:

        python -m backend.scripts.populate_lancedb

    To query a specific table:

        python backend/scripts/query_lancedb.py observations --limit 5
"""
