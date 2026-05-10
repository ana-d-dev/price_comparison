from playwright.sync_api import sync_playwright, Error as PlaywrightError, Browser, Page
from price_comparison.tariff_selectors.telemach import tariffs
from price_comparison.config.providers import providers
from price_comparison.logger_config import setup_logger
from datetime import date


logger = setup_logger('Telemach')
class Telemach:
    def __init__(self):
        """
        Initialize the Telemach scraper.

        Sets up:
        - Current date and time for logging or database insertion.
        - Placeholders for Playwright browser and page objects.
        - Containers for raw scraped data (main and additional tariffs).
        - Containers for cleaned data.
        - List of tariffs to skip when assigning minutes/SMS.
        - Final dictionary list to store combined tariff information.
        """
        # Storing date for last scraping
        self.scraped_date = date.today()

        # Placeholders for Playwright browser and page objects
        self.browser: Browser | None = None
        self.page: Page | None = None

        # Containers for main scraped data
        self.raw_main_names: list[str] = []
        self.raw_main_gbs: list[str] = []
        self.raw_main_prices: list[str] = []
        self.raw_main_values: list[str] = []

        # Containers for additional scraped data
        self.raw_add_names: list[str] = []
        self.raw_add_prices: list[str] = []
        self.raw_add_gbs: list[str] = []

        # List of tariffs that don't include minutes/SMS
        self.skip_names: list[str] = ['SIM2GO kartica 1 + 9 GB', 'SIM2GO za prijenos broja']

        # Containers for cleaned main data
        self.main_final_minutes: list[str] = []
        self.main_final_sms: list[str] = []
        self.final_gbs: list[str] = []
        self.final_names: list[str] = []
        self.final_prices: list[str] = []

        # Containers for cleaned additional data
        self.clean_add_names = []
        self.clean_add_gbs = []
        self.clean_add_prices = []

        # Final list to store combined tariff dictionaries
        self.new_dict: list[dict] = []


    def fetch(self):
        """
        Launch the Playwright Chromium browser in non-headless mode
        and open a new page for scraping.

        Raises:
            PlaywrightError: If the browser or page fails to launch.

        Notes:
        - The page object is stored in self.page for later navigation and scraping.
        """
        try:
            # Launch browser in non-headless mode.
            self.browser = self.p.chromium.launch(headless=True, args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ])

            # Open a new browser.
            self.page = self.browser.new_page()
            logger.info('Telemach browser launched and page object created successfully.')

        except PlaywrightError as e:
            # Log an exception if browser/page fails to launch
            logger.exception(f"Failed to launch Telemach browser or create page. Exception: {e}")


    def scraping_data(self):
        """
        Navigate to Telemach main and additional packages pages
        and scrape raw data for names, GBs, minutes/SMS, and prices.

        Stores scraped data in:
        - self.raw_main_names, self.raw_main_gbs, self.raw_main_values, self.raw_main_prices
        - self.raw_add_names, self.raw_add_gbs, self.raw_add_prices

        Raises:
            PlaywrightError: If any locator fails or the page structure has changed.
        """
        try:
            assert self.page is not None
            # Navigate to main Telemach prepaid page and scrape all relevant elements
            self.page.goto(providers['telemach']['urls']['main'])

            # Scrape tariff names
            self.raw_main_names = self.page.locator(tariffs['telemach']['main']['names']).all_inner_texts()

            # Scrape GB packages
            self.raw_main_gbs = self.page.locator(tariffs['telemach']['main']['gbs']).all_inner_texts()

            # Scrape minutes/SMS values
            self.raw_main_values = self.page.locator(tariffs['telemach']['main']['values']).all_inner_texts()

            # Scrape prices
            self.raw_main_prices = self.page.locator(tariffs['telemach']['main']['prices']).all_inner_texts()
            logger.info(
                f"Scraped main_names: {len(self.raw_main_names)}, main_gbs: {len(self.raw_main_gbs)}, main_values: {len(self.raw_main_values)}, main prices: {len(self.raw_main_prices)}."
            )

            # Navigate to additional packages page and scrape elements
            self.page.goto(providers['telemach']['urls']['add'])

            # Scrape additional package names
            self.raw_add_names = self.page.locator(tariffs['telemach']['add']['names']).all_inner_texts()

            # Scrape additional GBs
            self.raw_add_gbs = self.page.locator(tariffs['telemach']['add']['gbs']).all_inner_texts()

            # Scrape additional prices
            self.raw_add_prices = self.page.locator(tariffs['telemach']['add']['prices']).all_inner_texts()
            logger.info(f"Scraped additional_names: {len(self.raw_add_names)}, additional_gbs: {len(self.raw_add_gbs)}, additional_prices: {len(self.raw_add_prices)} .")

        except PlaywrightError as e:
            # Log an exception if any locator fails or page changes
            logger.exception(f"Scraping failed. Check CSS selectors. Exception: {e}")


    def calculation(self, value_gb:str, value_sms:str, value_min:str, value_price:str) -> tuple[int, float, float, float]:
        """
        Calculate various pricing metrics for a tariff.

        Args:
            value_gb (int or str): Number of GB in the package.
            value_sms (int or str): Number of SMS included.
            value_min (int or str): Number of minutes included.
            value_price (float or str): Price of the package.

        Returns:
            tuple:
                - units (int): Total units (GB*1000 + minutes + SMS)
                - price_per_gb (float): Price per GB
                - price_per_1000_units (float): Price per 1000 total units
                - price_per_60_min (float): Price per 60 minutes
        """

        # Calculate total units as GB*1000 + minutes + SMS
        calc_units = (int(value_gb) * 1000) + int(value_min) + int(value_sms)

        # Calculate price per GB
        calc_one_gb_price = round(float(value_price) / float(value_gb), 2)

        # Calculate price per single un
        calc_one_unit = float(value_price) / calc_units

        # Calculate price per 1000 units
        calc_thousand_units = round(calc_one_unit * 1000, 2)

        # Calculate price per 60 minutes
        calc_sixty_min_price = round(float(value_price) / 60, 2)

        # Return all calculated metrics
        return calc_units, calc_one_gb_price, calc_thousand_units, calc_sixty_min_price


    def cleaning_main_names(self) -> None:
        """
        Clean main tariff names by:
        - Replacing newlines with spaces
        - Stripping leading and trailing whitespace
        """
        # Replace newlines with spaces and strip extra whitespace from main tariff names
        self.final_names = [
            name.replace('\n', ' ').strip()
            for name in self.raw_main_names
        ]


    def cleaning_main_gbs(self) -> None:
        """
        Clean main GB values by:
        - Removing 'GB' text
        - Summing split values like '5+10' into a single number
        """
        # Removing GB, only number stays.
        clean_gbs = [
            gb.replace('GB', '').strip()
            for gb in self.raw_main_gbs
        ]

        # Split '+' GB values and sum, store as string.
        for gb in clean_gbs:
            if len(gb.split('+')) > 1:
                new_gb = gb.split('+')
                first_value = new_gb[0]
                second_value = new_gb[1]
                self.final_gbs.append(str(int(first_value) + int(second_value)))
            else:
                self.final_gbs.append(gb)


    def cleaning_main_prices(self) -> None:
        """
        Normalize main tariff prices by:
        - Replacing comma with dot
        - Removing euro symbol
        - Stripping extra whitespace
        """
        # Convert price strings to floats
        self.final_prices = [
            price.replace(',', '.').replace('€', '').strip()
            for price in self.raw_main_prices
        ]


    def cleaning_main_values(self) -> None:
        """
        Extract numeric values for minutes and SMS from raw main tariff strings.

        Processing:
        - Remove 'minuta' and 'SMS' text
        - Strip extra whitespace
        - Store every second value as minutes
        - Store every third value as SMS
        """
        # Extract minutes and SMS from raw values
        clean_values = [
            main.replace('minuta', '').replace('SMS', '').strip()
            for main in self.raw_main_values
        ]

        # Stores only minutes
        self.main_final_minutes = clean_values[1::2]

        # Stores only sms
        self.main_final_sms = clean_values[2::2]


    def combining_main_data(self) -> None:
        """
        Combine cleaned main tariff data into structured dictionaries.

        Processing:
        - Iterate over names, GBs, and prices
        - Calculate units, price per GB, price per 1000 units, and price per 60 minutes
        - Assign minutes and SMS only if tariff is not in skip list
        - Append each processed tariff dictionary to self.new_dict
        """
        # Index for minutes/SMS assignment
        pair_idx = 0
        for name, gb, price in zip(self.final_names, self.final_gbs, self.final_prices):

            # Initialize entry with default units and prices
            units, one_gb_price, thousand_units_price, sixty_min_price = self.calculation(gb, str(0), str(0), price)

            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['telemach']['provider'],
                'name': str(name),
                'price': str(price),
                'gb': str(gb),
                'units': str(units),
                'one_gb_price': str(one_gb_price),
                'thousand_units': str(thousand_units_price),
                'minutes': '',
                'sms': '',
                'sixty_min_price': '',
            }

            # Assign minutes/SMS only if tariff not skipped.
            if name not in self.skip_names:
                entry['minutes'] = str(self.main_final_minutes[pair_idx])
                entry['sms'] = str(self.main_final_sms[pair_idx])
                pair_idx += 1

                # Calling and returning a values for entering in dictionary.
                units, one_gb_price, thousand_units_price, sixty_min_price = self.calculation(str(gb), str(entry['sms']), str(entry['minutes']), str(price))

                entry['units'] = str(units)
                entry['one_gb_price'] = str(one_gb_price)
                entry['thousand_units'] = str(thousand_units_price)
                entry['sixty_min_price'] = str(sixty_min_price)

            # Add processed tariff to new_dict.
            self.new_dict.append(entry)


    def cleaning_add_names(self) -> None:
        """
        Clean additional tariff names.

        Processing:
        - Strip leading/trailing whitespace from each raw additional tariff name
        """
        # Strip whitespace from additional tariffs' names
        self.clean_add_names = [
            name.strip()
            for name in self.raw_add_names
        ]


    def cleaning_add_gbs(self) -> None:
        """
        Clean and normalize additional tariff GB values.

        Processing:
        - Remove 'GB' text
        - Split values containing '+' and sum them
        - Strip extra whitespace
        """
        # Remove 'GB' from additional tariffs, sum split values like '5+10', store as strings
        for add in self.raw_add_gbs:

            add_gb = add.replace('GB', '').strip()
            if len(add_gb.split('+')) > 1:
                values = add_gb.split('+')
                values_one = values[0]
                values_two = values[1]
                self.clean_add_gbs.append(str(int(values_one) + int(values_two)))

            else:
                self.clean_add_gbs.append(add_gb)


    def cleaning_add_prices(self) -> None:
        """
        Normalize additional tariff price strings.

        Processing:
        - Replace comma with dot
        - Remove '€' symbol
        - Strip extra whitespace
        """
        # Normalize additional tariff prices: replace ',' with '.', remove '€', strip whitespace
        self.clean_add_prices = [
            price.replace(',', '.').replace('€', ' ').strip()
            for price in self.raw_add_prices
        ]


    def combining_add_data(self) -> None:
        """
        Combine cleaned additional tariff names, GBs, and prices into dictionaries
        with calculated metrics.

        Each dictionary contains:
            - provider
            - date and time of scraping
            - name, price, GB, minutes, SMS
            - calculated units, price per GB, price per 1000 units, price per 60 minutes

        Appends each dictionary to:
            self.new_dict (list[dict])
        """
        # Combine cleaned additional tariffs into dictionaries with calculated metrics
        for name, gbs, price in zip(self.clean_add_names, self.clean_add_gbs, self.clean_add_prices):
            units, one_gb_price, thousand_units_price, sixty_min_price = self.calculation(gbs, str(0), str(0), price)

            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['telemach']['provider'],
                'name': name,
                'price': str(price),
                'gb': str(gbs),
                'units': str(units),
                'one_gb_price': str(one_gb_price),
                'thousand_units': str(thousand_units_price),
                'minutes': '',
                'sms': '',
                'sixty_min_price': ''
            }
            # Append each processed tariff to self.new_dict
            self.new_dict.append(entry)


    def handling_data(self) -> None:
        """
       Run all cleaning and combining steps for both main and additional tariffs
       in proper order.

       Steps:
           1. Clean main tariff names, GBs, prices, and values.
           2. Combine main tariff data into dictionaries.
           3. Clean additional tariff names, GBs, and prices.
           4. Combine additional tariff data into dictionaries.
       """
        # Run all cleaning and combining steps in proper order for main and additional tariffs
        self.cleaning_main_names()
        self.cleaning_main_gbs()
        self.cleaning_main_prices()
        self.cleaning_main_values()
        self.combining_main_data()
        self.cleaning_add_names()
        self.cleaning_add_gbs()
        self.cleaning_add_prices()
        self.combining_add_data()



    def run(self) -> None:
        """
        Orchestrate the full scraping workflow for Telemach prepaid tariffs.

        Steps:
            1. Launch Playwright browser using a context manager.
            2. Navigate to main and additional Telemach package pages and scrape data.
            3. Abort early with logging if the page fails to load or no data is scraped.
            4. Close the browser to release resources.
            5. Clean, normalize, and combine scraped data into structured dictionaries.

        Notes:
            - All data processing (`handling_data()`) occurs after the Playwright session ends
              to avoid accessing live browser objects during cleaning.
            - Assertions and early exits ensure that scraping failures do not cause runtime errors.
            - The final structured dictionaries are stored in `self.new_dict`.
        """
        # Main execution method:
        with sync_playwright() as self.p:
            # Open browser and navigate to Telemach prepaid page
            self.fetch()

            # Safety check: abort if page not created
            if not self.page:
                logger.exception("Page not created. Aborting scraping.")
                return

            # Scrape data from all relevant pages
            self.scraping_data()

            # Abort early if no data scraped
            if not self.raw_main_names or not self.raw_add_names:
                logger.exception("No data scraped. Aborting.")
                return

            # Close browser safely
            assert self.browser is not None  # For mypy/type safety
            self.browser.close()
            logger.info('Telemach browser successfully closed.')

        # Clean, combine, and output final data
        self.handling_data()



