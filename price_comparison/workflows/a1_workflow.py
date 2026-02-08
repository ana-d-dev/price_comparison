from price_comparison.validation.validation_data import validate_records
from price_comparison.logger_config import setup_logger
from price_comparison.scripts.scraping.a1 import A1


logger = setup_logger('a1_workflow')
def run_a1_workflow():
    """
    Run the A1 scraping workflow.

    Steps:
    1. Log that scraping has started.
    2. Fetch data from A1 scraper.
    3. Validate the scraped data using validate_records().
    4. Return data to main_runner.py
    """
    logger.info("Starting A1 workflow scraping...")
    a1 = A1()
    a1.run()
    data = a1.new_dict
    if not data:
        raise RuntimeError("A1 returned no data.")
    validate_records(data)
    logger.info('A1 data has been successfully collected, validated and returned.')
    return data



if __name__ == '__main__':
    run_a1_workflow()
