from price_comparison.validation.validation_data import validate_records
from price_comparison.scripts.scraping.tomato import Tomato
from price_comparison.logger_config import setup_logger


logger = setup_logger('tomato_workflow')
def run_tomato_workflow():
    """
    Run the Tomato scraping workflow.

    Steps:
    1. Log that scraping has started.
    2. Run the Tomato scraper to collect data.
    3. Validate the scraped data to ensure all records meet requirements.
    4. Return data to main_runner.py
    """
    logger.info("Starting Tomato workflow scraping...")
    tomato = Tomato()
    tomato.run()
    data = tomato.new_dict
    if not data:
        raise RuntimeError("Tomato returned no data.")
    validate_records(data)
    logger.info('Tomato data has been successfully collected, validated and returned.')
    return data


if __name__ == '__main__':
    run_tomato_workflow()