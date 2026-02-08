from price_comparison.validation.validation_data import validate_records
from price_comparison.logger_config import setup_logger
from price_comparison.scripts.scraping.com import TCom


logger = setup_logger('com_workflow')
def run_com_workflow():
    """
    Run the T-Com scraping workflow.

    Steps:
    1. Log that the scraping has started.
    2. Run the T-Com scraper to collect data.
    3. Validate the scraped data to ensure all records are correct.
    4. Return data to main_runner.py
    """
    logger.info("Starting T-Com workflow scraping...")
    com = TCom()
    com.run()
    data = com.new_dict
    if not data:
        raise RuntimeError("T-Com returned no data.")
    validate_records(data)
    logger.info("T-Com workflow successfully collected, validated and returned data.")
    return data


if __name__ == '__main__':
    run_com_workflow()