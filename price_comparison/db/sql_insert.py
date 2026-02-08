from sqlalchemy import insert
from price_comparison.db.engine import engine
from price_comparison.db.tables import tariffs


def save_to_db(data):
    """
    Insert a list of dictionaries into the 'tariffs' table in the database.

    Empty strings in the data are converted to None to store as NULL in the database.
    The function ensures the 'tariffs' table exists before inserting and commits the changes.
    """
    for row in data:
        for key, value in row.items():
            if value == '':
                row[key] = None


    stmt = insert(tariffs).values(data)
    with engine.connect() as conn:
        tariffs.create(engine, checkfirst=True)
        conn.execute(stmt)
        conn.commit()



