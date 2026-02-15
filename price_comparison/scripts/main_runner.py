"""
Main runner script to execute provider workflows.

This script:
  1. Runs scraping workflows for the selected providers.
  2. Collects and validates all data from each workflow.
  3. Stops insertion to the database if any provider fails.
  4. Logs all actions, errors, and exceptions.
  5. Error-level logs trigger notifications automatically.

Usage:
    python main_runner.py a1 bon com telemach tomato
"""

from price_comparison.workflows.telemach_workflow import run_telemach_workflow
from price_comparison.workflows.tomato_workflow import run_tomato_workflow
from price_comparison.workflows.bon_workflow import run_bon_workflow
from price_comparison.workflows.com_workflow import run_com_workflow
from price_comparison.workflows.a1_workflow import run_a1_workflow
from price_comparison.logger_config import setup_logger
from price_comparison.db.sql_insert import save_to_db
from datetime import datetime
import sys


logger = setup_logger("main_runner")

now = datetime.now()
date = now.date().strftime('%d.%m.%Y.')
time = now.time().strftime('%H:%M:%S')

PROVIDERS = {
    "a1": run_a1_workflow,
    "bon": run_bon_workflow,
    "com": run_com_workflow,
    "telemach": run_telemach_workflow,
    "tomato": run_tomato_workflow,
}


def main() -> None:
    """
    Run workflows for all specified providers.

    Steps:
       1. Parse provider arguments from the command line.
       2. Execute each workflow sequentially.
       3. Collect data from all successful workflows.
       4. Skip database insertion if any workflow fails.
       5. Log all actions, errors, and failures.
    """
    args = [arg.strip().lower() for arg in sys.argv[1:] if arg.strip()]
    all_data: list[dict] = []
    failed_providers: list[str] = []

    if not args:
        logger.error('No provider specified. Usage: python -m price_comparison.scripts.main_runner a1 bon com telemach tomato')
        sys.exit(1)

    for provider in args:
        if provider not in PROVIDERS:
            logger.error(f"Invalid provider '{provider}'. ")
            continue

        try:
            logger.info(f"Starting workflow '{provider}'")
            data = PROVIDERS[provider]()
            all_data.extend(data)
            logger.info(f"Workflow '{provider}' finished successfully")

        except Exception:
            # ONE place where failures are handled
            logger.exception(f"Workflow '{provider}' failed")
            # continue with next provider
            failed_providers.append(provider)


    if not all_data and args:
        logger.error("No valid providers specified. Nothing to do.")
        sys.exit(1)

    if failed_providers:
        logger.error(
            f"Not inserting any data. Failed providers: {', '.join(failed_providers)}"
        )
    else:
        save_to_db(all_data)
        with open('lastupdate.txt', 'w') as f:
            f.write(f"{date} {time}")
        logger.info(
            f"All providers successfully inserted into database."
        )

if __name__ == "__main__":
    main()
