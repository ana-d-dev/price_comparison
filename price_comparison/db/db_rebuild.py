"""
Script to drop and recreate all database tables.

WARNING: This will DELETE ALL DATA in the database. User confirmation required.
Logs all steps to logs/db_rebuild.log.
"""
from price_comparison.db.engine import engine, metadata
from price_comparison.logger_config import setup_logger

# IMPORTANT: force load of all table definitions
import price_comparison.db.tables

logger = setup_logger('db_rebuild')

if __name__ == '__main__':
    logger.warning('Database rebuilding started...')

    answer = input('This will DROP ALL TABLES. Say yes to continue: ').strip().lower()
    if answer != 'yes':
        logger.info('Operation quit!')
        exit()

    metadata.drop_all(engine, checkfirst=True)
    logger.info('Tables dropped.')

    metadata.create_all(engine)
    logger.info('Tables recreated.')


