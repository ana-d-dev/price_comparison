"""
Definition of the 'tariffs' table for the SQL database.

This module defines the structure of the 'tariffs' table, including all
columns and their types. The table is associated with the metadata from
`db.engine` and can be created in the database using SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Date, Table
from price_comparison.db.engine import metadata

tariffs = Table (
    'tariffs',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('scraped_date', Date),
    Column('provider', String),
    Column('name', String),
    Column('price', String),
    Column('gb', String),
    Column('minutes', String),
    Column('sms', String),
    Column('units', String),
    Column('one_gb_price', String),
    Column('sixty_min_price', String),
    Column('thousand_units', String)
)
