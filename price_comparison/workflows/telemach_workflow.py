from price_comparison.validation.validation_data import validate_records
from price_comparison.scripts.scraping.telemach import Telemach
from price_comparison.logger_config import setup_logger


logger = setup_logger('telemach_workflow')
def run_telemach_workflow():
    """
    Run the Telemach scraping workflow.

    Steps:
    1. Log that scraping has started.
    2. Run the Telemach scraper to collect data.
    3. Validate the scraped data to ensure all records meet requirements.
    4. Return data to main_runner.py
    """
    logger.info("Starting Telemach workflow scraping...")
    telemach = Telemach()
    telemach.run()
    data = telemach.new_dict
    if not data:
        raise RuntimeError("Telemach returned no data.")
    validate_records(data)
    logger.info('Telemach data has been successfully collected, validated and returned.')
    return data



if __name__ == '__main__':
    run_telemach_workflow()