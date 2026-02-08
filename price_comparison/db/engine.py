"""
Database engine and metadata setup.

- Loads the database URL from the environment.
- Creates a SQLAlchemy engine for connecting to the database.
- Provides metadata to manage and ensure the existence of tables.
- Exposes `engine` and `metadata` for use in other modules.
"""
from sqlalchemy import create_engine, MetaData
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()