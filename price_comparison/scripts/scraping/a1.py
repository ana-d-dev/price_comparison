from playwright.sync_api import sync_playwright, Error as PlaywrightError, Browser, Page, ElementHandle
from price_comparison.logger_config import setup_logger
from price_comparison.tariff_selectors.a1 import tariffs
from price_comparison.config.providers import providers
from datetime import date


logger = setup_logger("a1")
class A1:
    def __init__(self):
        # Storing date for last scraping
        self.scraped_date = date.today()

        # Placeholders for Playwright objects (will be created in fetch()).
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.buttons: list[ElementHandle] = []

        # Containers for main scraped data
        self.raw_main_names: list[str] = []
        self.raw_main_prices: list[str] = []
        self.raw_main_values: list[str] = []

        # Containers for additional scraped data
        self.raw_add_names: list[str] = []
        self.raw_add_prices: list[str] = []
        self.raw_add_gbs: list[str] = []

        # Containers for clean main data
        self.clean_main_names: list[str] = []
        self.clean_main_prices: list[str] = []
        self.clean_main_values: list[str] = []

        # Containers for clean additional data
        self.clean_add_names: list[str] = []
        self.clean_add_prices: list[str] = []
        self.clean_add_gbs: list[str] = []

        # List for all combined data (main and additional)
        self.new_dict: list[dict] = []


    def fetch(self):
        """
        Launch browser and open the target A1 prepaid tariffs page.
        """
        try:
            # Launch browser in non-headless mode (set to True for production automation).
            self.browser = self.p.chromium.launch(headless=False)

            # Opening a new browser tab
            self.page = self.browser.new_page()

            # Navigate to prepaid tariffs page (A1 "na bonove").
            self.page.goto(providers['a1']['urls']['main'])
            logger.info('A1 web page reached!')
        except PlaywrightError as e:
            # Raising error if web page not found
            logger.exception(f"Couldn't reach A1 web page. {e}")


    def handling_cookies(self) -> None:
        try:
            assert self.page is not None
            button = self.page.locator(tariffs['a1']['cookie_button'])
            if button.is_visible():
                button.click()
                logger.info("Cookies accepted.")
            else:
                logger.info("No cookies banner found.")
        except PlaywrightError as e:
            logger.exception(f'Cookies not found or clickable. {e}')


    def scraping_data(self) -> None:
        """
        Scrape raw data for main and additional A1 tariffs.
        - Iterates through category buttons to extract main offers (name, price, values).
        - Extracts additional offers (name, price, GB/minutes).
        """
        try:
            assert self.page is not None
            # Collect all tariff-category buttons on the page
            self.buttons = self.page.query_selector_all(tariffs['a1']['buttons'])

            # Click each button to reveal and scrape corresponding tariff data
            for button in self.buttons:
                button.click()

                # Extract main tariff fields after button click
                main_names = self.page.locator(tariffs['a1']['main_names']).all_inner_texts()
                main_values = self.page.locator(tariffs['a1']['main_values']).all_inner_texts()
                main_prices = self.page.locator(tariffs['a1']['main_prices']).all_inner_texts()

                # Appending data into raw containers
                for name in main_names:
                    self.raw_main_names.append(name)

                for value in main_values:
                    self.raw_main_values.append(value)

                for price in main_prices:
                    self.raw_main_prices.append(price)

            # Extract additional tariffs (names, prices, GB/minutes).
            self.raw_add_names = self.page.locator(tariffs['a1']['add_names']).all_inner_texts()
            self.raw_add_prices = self.page.locator(tariffs['a1']['add_prices']).all_inner_texts()
            self.raw_add_gbs = self.page.locator(tariffs['a1']['add_gbs']).all_inner_texts()

            logger.info('All CSS selectors are find and all data is scraped.')
        except PlaywrightError as e:
            # Raising error if selectors doesn't work
            logger.exception(f'CSS selector not working. {e}')


    def calculating(self, gb, price, sms):
        """
        Calculate normalized cost metrics for a tariff.
        """
        try:
            gb = float(gb)
            price = float(price)
        except ValueError:
            return False

        # Special case: gb < 0 return False
        if gb < 0 or price < 0:
            return False

        # Special case: no GB included → only per-minutes price and sms
        elif gb == 0:
            sixty_min_price = round(float(price) / 60, 2)
            units = (int(gb) * 1000) + 0 + int(sms)
            return  sixty_min_price, units

        else:
            # Calculate total units as GB*1000 + minutes + SMS
            units = (int(gb) * 1000) + 0 + int(sms)

            # Calculate price per GB
            one_gb_price = round(float(price) / float(gb), 2)

            # Calculate price per single un
            one_unit = float(price) / units

            # Calculate price per 1000 units
            thousand_units = round(one_unit * 1000, 2)

            # Calculate price per 60 minutes
            sixty_min_price = round(float(price) / 60, 2)

            # returning units, one gb price, a thousand units and sixty min price for later comparison
            return units, one_gb_price, thousand_units, sixty_min_price


    def cleaning_main_names(self) -> None:
        """
        Clean raw main tariff names by stripping extra whitespace.
        Stores results in self.clean_main_names.
        """
        self.clean_main_names = [
            name.strip()
            for name in self.raw_main_names
        ]


    def cleaning_main_prices(self) -> None:
        """
        Normalize raw main prices:
        - Remove text labels (mjesečno, €, /mj., promo statements).
        - Replace ',' with '.' to standardize decimal format.
        - Extract only the numeric part (first token).
        Stores results in self.clean_main_prices.
        """
        self.clean_main_prices = [
            price.replace('\n', '')
            .replace('mjesečno', '')
            .replace('€', '')
            .replace('/mj.', '')
            .replace('Cijena za tri mjeseca', '')
            .replace('Cijena za šest mjeseci', '')
            .replace(',', '.').strip().split(' ')[0] # keep only the numeric portion
            for price in self.raw_main_prices
            if price
        ]


    def cleaning_main_values(self) -> None:
        """
        Normalize raw main values:
        - Remove marketing text (e.g., "Saznaj više").
        - Strip whitespace.
        Stores results in self.clean_main_values.
        """
        self.clean_main_values = [
            value.replace('Saznaj više', '').strip()
            for value in self.raw_main_values
            if value.replace('Saznaj više', '').strip()
        ]


    def cleaning_add_names(self) -> None:
        """
        Cleaning additional names:
        - surplus whitespaces if they are.
        Starting from third place, because of commercial statements.
        """
        self.clean_add_names = [
            name.strip()
            for name in self.raw_add_names[3:]
        ]


    def cleaning_add_prices(self) -> None:
        """
        Cleaning additional prices:
        - replacing '€' with nothing then stripping
        - replacing ',' with '.' so it stays clean float number
        """
        self.clean_add_prices = [
            price.replace('€', '').replace(',', '.').strip()
            for price in self.raw_add_prices
            if price
        ]


    def cleaning_add_gbs(self) -> None:
        """
        Cleaning additional gb:
        - splitting with whitespaces
        - taking the first value for later comparison
        """
        self.clean_add_gbs = [
            gb.split()[0].strip()
            for gb in self.raw_add_gbs
            if gb.strip()
        ]


    def all_together_main(self) -> None:
        """
        Looping through clean main names and prices
        - slicing clean main values for each tariff to be correct
        - start a fresh entry for this plan
        - checking if number is numeric (gb can be unlimited (str) and in calculation it will raise an error)
        - storing calculated data into dictionary
        - same as the rest of data
        - slicing plus +2 so every data will correct for each tariff
        - appending whole dictionary in list
        """
        start = 0
        end = 2
        for name, price in zip(self.clean_main_names, self.clean_main_prices):
            gb, minutes = self.clean_main_values[start:end]
            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['a1']['provider'],
                'name': name,
                'price': str(price),
                'gb' : '',
                'minutes': str(minutes),
                'sms': '',
                'units': '',
                'one_gb_price': '',
                'sixty_min_price': '',
                'thousand_units': ''
            }

            if gb.isnumeric():
                units, one_gb_price, thousand_units, sixty_min_price = self.calculating(gb, price, 0)
                entry['gb'] = str(gb)
                entry['units'] = str(units)
                entry['one_gb_price'] = str(one_gb_price)
                entry['thousand_units'] = str(thousand_units)
                entry['sixty_min_price'] = str(sixty_min_price)
            else:
                sixty_min_price, units = self.calculating(0, price, 0)
                entry['sixty_min_price'] = str(sixty_min_price)
                entry['gb'] = str(gb)

            start += 2
            end += 2
            self.new_dict.append(entry)


    def all_together_add(self) -> None:
        """
        Looping through clean additional names, prices and gbs
        - starting fresh dictionary entry for these tariffs
        - checking gb is number (can be string)
            - checking length of gb because it is actually minutes
            - calculating only minutes and sixty minutes price
            - else calculating the rest data (gb, units, one gb price, a thousand units, sixty minutes price)
        - else handling gb (str)
        - appending dictionary to the list with the rest data
        """
        for name, price, gb in zip(self.clean_add_names, self.clean_add_prices, self.clean_add_gbs):
            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['a1']['provider'],
                'name': name,
                'price': str(price),
                'gb': '',
                'minutes': '',
                'sms': '',
                'units': '',
                'one_gb_price': '',
                'sixty_min_price': '',
                'thousand_units': ''
            }

            if gb.isnumeric():
                # Checking sms values, gb is sms because of scarping
                if len(gb) > 2:
                    sixty_min_price, units = self.calculating(0, price, gb)
                    entry['sms'] = str(gb)
                    entry['units'] = str(units)
                else:
                    units, one_gb_price, thousand_units, sixty_min_price = self.calculating(gb, price, 0)
                    entry['gb'] = str(gb)
                    entry['units'] = str(units)
                    entry['one_gb_price'] = str(one_gb_price)
                    entry['thousand_units'] = str(thousand_units)
            else:
                entry['gb'] = str(gb)

            self.new_dict.append(entry)


    def handling_data(self) -> None:
        """
        Run all cleaning and handling data for main and additional tariffs.

        Steps:
            1. Cleaning main names, prices and values
            2. Cleaning additional names, prices and gb
            3. Storing all main data in one list
            4. Storing all additional data in one list
        """
        self.cleaning_main_names()
        self.cleaning_main_prices()
        self.cleaning_main_values()
        self.cleaning_add_names()
        self.cleaning_add_prices()
        self.cleaning_add_gbs()
        self.all_together_main()
        self.all_together_add()


    def run(self) -> None:
        """
        Run the full scraping workflow for A1 prepaid tariffs.

        - Launch Playwright browser and open the A1 page.
        - Handle cookies/pop-ups.
        - Scrape main and additional tariff data.
        - Close the browser to free resources.
        - Clean and combine scraped data into structured dictionaries.

        Early exits are logged if the page is missing or no data is scraped.
        """
        # Launch Playwright browser and manage lifecycle with context manager
        with sync_playwright() as self.p:
            # Open browser and navigate to A1 prepaid page
            self.fetch()

            # Accept cookies or close pop-ups if present
            self.handling_cookies()

            # Safety check: abort if page wasn't successfully created
            if not self.page:
                logger.exception("Page not created. Aborting scraping.")
                return

            # Scrape main and additional tariffs
            self.scraping_data()

            # Safety check: abort if scraping returned no data
            if not self.raw_main_names or not self.raw_add_names:
                logger.exception("No data scraped. Aborting.")
                return

            # Close the browser to free resources
            assert self.browser is not None  # For mypy/type safety
            self.browser.close()
            logger.info("Browser closed successfully.")

        # Process and clean scraped data after Playwright session ends
        self.handling_data()