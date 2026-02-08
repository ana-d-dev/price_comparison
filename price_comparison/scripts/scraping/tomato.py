from playwright.sync_api import sync_playwright, Browser, Page, Error as PlaywrightError
from price_comparison.tariff_selectors.tomato import tariffs
from price_comparison.config.providers import providers
from price_comparison.logger_config import setup_logger
from datetime import date


logger = setup_logger('Tomato')
class Tomato:
    def __init__(self):
        # Storing date for last scraping
        self.scraped_date = date.today()

        # Playwright browser instance and page object
        self.browser: Browser | None = None           # Playwright browser instance
        self.page: Page | None = None                 # Playwright page object

        # Raw scraped main plan data from the website (names, prices, units)
        self.main_raw_names: list[str] = []           # Names as scraped from the website
        self.main_raw_prices: list[str] = []          # Prices as scraped from the website
        self.main_raw_units: list[str] = []           # Units as scraped from the website

        # Lists for cleaned data ready for calculations (names, prices, units)
        self.main_names: list[str] = []               # Names after stripping whitespace
        self.main_prices: list[str] = []              # Prices extracted and formatted as float strings
        self.main_units: list[int] = []               # Units cleaned and summed

        # Combined data in structured dictionaries for each plan
        self.new_dict: list[dict] = []                # Stores dictionaries for each plan


    def fetch(self):
        """
        Launches the browser, opens a new page, and navigates to the Tomato main URL.

        - Uses headless mode by default (`headless=True`).
        - Logs an exception if the page cannot be opened or times out.
        """
        try:
            # Launch browser instance (headless=False for debugging)
            self.browser = self.p.chromium.launch(headless=True)

            # Open a new browser page
            self.page = self.browser.new_page()

            # Navigate to Tomato main page
            self.page.goto(providers['tomato']['urls']['main'], wait_until="domcontentloaded", timeout=15000)
            logger.info('Tomato web page reached successfully.')

        except PlaywrightError as e:
            logger.exception(f'Page not found. {e}')


    def finding_data(self):
        """
        Finds and collects raw tariff data from the Tomato page.

        - Scrapes plan names, units, and prices using CSS locators.
        - Stores raw results in dedicated lists for later cleaning.
        - Logs an exception if locators are missing or invalid.
        """
        try:
            assert self.page is not None
            # Scrape plan names from page and store in raw list
            self.main_raw_names = [
                name
                for name in self.page.locator(tariffs['tomato']['names']).all_text_contents()
            ]

            # Scrape plan prices from page and store in raw list
            assert self.page is not None
            self.main_raw_prices = [
                price
                for price in self.page.locator(tariffs['tomato']['prices']).all_text_contents()
            ]

            # Scrape plan units from page and store in raw list
            assert self.page is not None
            self.main_raw_units = [
                unit
                for unit in self.page.locator(tariffs['tomato']['units']).all_text_contents()
            ]
            logger.info(f'Main data successfully scraped. main_raw_names {len(self.main_raw_names)}, main_raw_prices {len(self.main_raw_prices)}, main_raw_units: {len(self.main_raw_units)}')


        except PlaywrightError as e:
            logger.exception(f'Locator not found. {e}')


    def cleaning_names(self) -> None:
        """
        Cleans scraped plan names by stripping extra whitespace.

        - Converts raw name strings into a clean format for later processing.
        """

        # Remove extra spaces from each raw plan name
        self.main_names = [
            name.strip()
            for name in self.main_raw_names
        ]


    def cleaning_prices(self) -> None:
        """
        Cleans scraped price strings.

        - Strips extra whitespace and replaces commas with dots for numeric conversion.
        - Prepares price data for calculations and storage.
        """

        # Clean each raw price: strip spaces and replace comma with dot for float conversion
        self.main_prices = [
            price.replace(',', '.').strip()
            for price in self.main_raw_prices
        ]


    def cleaning_units(self) -> None:
        """
        Cleans scraped unit strings and converts them to integers.

        - Replaces '\xa0' and the word 'jedinica' with spaces.
        - Splits values on '+' and strips extra whitespace.
        - Adds both parts together to calculate total units.

        Assumes each unit string contains two numeric parts.
        """
        for unit in self.main_raw_units:
            # Replace 'jedinica' and non-breaking spaces, then strip extra spaces
            clean_unit = unit.replace('jedinica', ' ').replace('\xa0', ' ').strip()

            # Split the string on '+' and remove remaining spaces
            parts = [
                part.strip().replace(' ', '')
                for part in clean_unit.split('+')
            ]

            # Convert both parts to int and sum to get total units
            self.main_units.append(int(parts[0]) + int(parts[1]))


    def all_together(self) -> None:
        """
        Combines cleaned tariff data into a list of dictionaries.

        Each dictionary includes:
        - Provider info, date, and time
        - Plan name, price, units, and derived values:
          * GB equivalent
          * Price per GB
          * Price per unit
          * Price for 1000 units
          * Price for 60 minutes
        """
        for name, unit, price in zip(self.main_names, self.main_units, self.main_prices):

            # Calculate GB equivalent
            gb = int(unit / 1000)

            # Calculate price per GB
            one_gb_price = round(float(price) / float(gb), 2)

            # Calculate price per unit
            one_unit = float(price) / float(unit)

            # Calculate price for 1000 units
            thousand_units = round(one_unit * 1000, 2)

            # Calculate price for 60 minutes
            sixty_min_price = round(float(price) / 60, 2)

            # Append dictionary with all plan details and calculated metrics
            self.new_dict.append(
                {
                    'scraped_date': self.scraped_date,
                    'provider': providers['tomato']['provider'],  # Provider name
                    'name':name,                                  # Plan name
                    'price': str(price),                          # Plan price
                    'gb': str(gb),                                # Plan GB
                    'one_gb_price':str(one_gb_price),             # Price per GB for numeric GB plans
                    'units': str(unit),                           # Store total units
                    'thousand_units': str(thousand_units),        # Store price for 1000 units
                    'sixty_min_price':str(sixty_min_price),       # Store 60-min price
                    'minutes': '',
                    'sms': '',
                }
            )


    def handling_data(self) -> None:
        """
        Calls all cleaning and combining functions to prepare the final dataset.

        - Cleans names, prices, and units.
        - Merges results into structured dictionaries.
        - Prints all intermediate and final values for debugging.
        """
        # Clean plan names from raw data
        self.cleaning_names()

        # Clean plan prices from raw data
        self.cleaning_prices()

        # Clean plan units from raw data
        self.cleaning_units()

        # Combine all cleaned data into structured dictionaries
        self.all_together()


    def run(self) -> None:
        """
        Orchestrate the full scraping workflow for Tomato prepaid plans.

        Steps:
            1. Launch a Playwright browser and navigate to the Tomato main page.
            2. Scrape raw plan data including names, units, and prices.
            3. Abort early with logging if the page fails to load or no data is scraped.
            4. Close the browser to release resources.
            5. Clean and normalize scraped data, then combine it into structured dictionaries.

        Notes:
            - All post-processing (`handling_data()`) occurs after the Playwright session ends
              to avoid live browser dependency during cleaning.
            - The final structured plan dictionaries are stored in `self.new_dict`.
            - Safety checks prevent runtime errors if scraping fails.
        """
        with sync_playwright() as self.p:
            # Launch browser and navigate to main Tomato page
            self.fetch()

            # Abort if page not created
            if not self.page:
                logger.exception("Page not created. Aborting scraping.")
                return

            # Scrape raw plan data (names, units, prices)
            self.finding_data()

            # Abort early if no data was scraped
            if not self.main_raw_names:
                logger.exception("No data scraped. Aborting.")
                return

            # Close browser safely
            assert self.browser is not None  # For mypy/type safety
            self.browser.close()
            logger.info('Tomato browser successfully closed.')

        # Clean scraped data and combine into final structured dataset
        self.handling_data()
