from price_comparison.db.tables import tariffs
from price_comparison.db.engine import engine
from sqlalchemy import select, func


def get_all_data():
    with engine.connect() as conn:
        stmt = select(tariffs).where(
            tariffs.c.scraped_date == (select(func.max(tariffs.c.scraped_date)).scalar_subquery()))
        result = conn.execute(stmt)
        rows = result.mappings().all()

    clean_rows = []
    for row in rows:
        clean_row = {key: (value if value is not None else '-') for key, value in row.items()}
        clean_rows.append(clean_row)
    return clean_rows


def get_provider_data(provider_name):
    if not provider_name:
        raise ValueError("provider_name must be a non-empty string")

    with engine.connect() as conn:
        # noinspection PyTypeChecker
        stmt = select(tariffs).where(
            tariffs.c.provider == provider_name,
                        tariffs.c.scraped_date == (
                            select(func.max(tariffs.c.scraped_date))
                            .where(tariffs.c.provider == provider_name)
                            .scalar_subquery()
                        )
        )
        result = conn.execute(stmt)
        rows = result.mappings().all()

    clean_rows = []
    for row in rows:
        clean_row = {key: (value if value is not None else '-') for key, value in row.items()}
        clean_rows.append(clean_row)
    return clean_rows




