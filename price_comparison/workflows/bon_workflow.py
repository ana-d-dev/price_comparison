from price_comparison.validation.validation_data import validate_records
from price_comparison.logger_config import setup_logger
from price_comparison.scripts.scraping.bon import Bon


logger = setup_logger('bon_workflow')
def run_bon_workflow():
    """
    Run the Bon-Bon scraping workflow.

    Steps:
    1. Log that the scraping has started.
    2. Run the Bon-Bon scraper to collect data.
    3. Validate the scraped data to ensure all records are correct.
    4. Return data to main_runner.py
    """
    logger.info("Starting Bon-Bon workflow scraping...")
    bon = Bon()
    bon.run()
    data = bon.new_dict
    if not data:
        raise RuntimeError("Bon-Bon returned no data.")
    validate_records(data)
    logger.info('Bon-Bon data has been successfully collected, validated and returned.')
    return data


if __name__ == '__main__':
    run_bon_workflow()