from playwright.sync_api import sync_playwright, Error as PlaywrightError, Browser, Page
from price_comparison.config.providers import providers
from price_comparison.logger_config import setup_logger
from price_comparison.tariff_selectors.bon import tariffs
from datetime import date


logger = setup_logger('Bon-Bon')
class Bon:
    """
    Scraper for Bonbon prepaid packages.

    Uses Playwright to fetch names, values, and prices from the website.
    Cleans raw data and structures it into dictionaries for further use.
    """
    def __init__(self) -> None:
        """
        Initialize scraper state.

        Sets timestamps, prepares browser/page placeholders,
        and initializes storage for scraped and cleaned data.
        """
        # Storing date for last scraping
        self.scraped_date = date.today()

        # Placeholders for Playwright objects (will be created in fetch()).
        self.browser: Browser | None = None
        self.page: Page | None = None

        # Containers for raw scraped data.
        self.raw_names: list[str] = []
        self.raw_values: list[str] = []
        self.raw_prices: list[str] = []
        self.raw_pre_combined_values: list[str] = []
        self.raw_pre_combined_prices: list[str] = []

        # Will hold plan names that weren’t added during main cleaning.
        self.missing_names: list[str] = []

        # Cleaned versions of pre-combined values/prices.
        self.clean_pre_combined_prices: list[str] = []
        self.clean_pre_combined_values: list[str] = []

        # Final result container (list of dicts, each dict = one tariff).
        self.new_dict: list[dict] = []


    def fetch(self) -> None:
        """
        Launch browser and open the Bonbon packages page.

        Raises:
            PlaywrightError: If the page cannot be opened.
        """
        try:
            # Start a Chromium browser (headless=True = no visible window).
            self.browser = self.p.chromium.launch(headless=False)

            # Open a new browser tab/page.
            self.page = self.browser.new_page()

            # Go to the Bonbon prepaid packages page.
            self.page.goto(providers['bon_bon']['urls']['main'], wait_until="networkidle")
            logger.info('Bon-Bon web page reached!')
        except PlaywrightError as e:
            # If browser launch or page load fails → log the error.
            logger.exception(f'Failed to open Bon-Bon main page. {e}')


    def scraping_data(self) -> None:
        """
        Scrape raw names, values, and prices from the page.

        Populates attributes:
            - raw_names
            - raw_values
            - raw_prices
            - raw_pre_combined_values
            - raw_pre_combined_prices
        """

        try:
            assert self.page is not None
            # Extract plan names (all package names).
            self.raw_names = self.page.locator(tariffs['bon_bon']['names']).all_text_contents()

            # Extract plan values (minutes, GB, SMS) - only first 13 entries.
            self.raw_values = self.page.locator(tariffs['bon_bon']['values']).all_inner_texts()[:13]

            # Extract plan prices (corresponding to the first 13 values).
            self.raw_prices = self.page.locator(tariffs['bon_bon']['prices']).all_inner_texts()[:13]

            # Extract pre-combined values (when GB/min/SMS are bundled together).
            self.raw_pre_combined_values = self.page.locator(tariffs['bon_bon']['pre_combined_values']).all_inner_texts()

            # Extract pre-combined prices (special large-format prices).
            self.raw_pre_combined_prices = self.page.locator(tariffs['bon_bon']['pre_combined_prices']).all_inner_texts()

            logger.info('All CSS selectors are find and all data is scraped.')
        except PlaywrightError as e:
            # If scraping fails (e.g., locator not found, page not loaded) → log the error.
            logger.exception(f'Failed to scrape data. {e}')


    def calculating(self, gb, minutes, sms, price):
        # Compute total "units" for the plan: 1 GB = 1000 units + minutes
        units = (int(gb) * 1000) + int(minutes) + int(sms)

        # Price per single unit
        one_unit = float(price) / units

        # Price per 1000 units (for easier comparison across plans)
        thousand_units = round(one_unit * 1000, 2)

        # One gb price
        if gb and gb != "0":
            one_gb_price = round(float(price) / float(gb), 2)
        else:
            one_gb_price = None

        return units, thousand_units, one_gb_price


    def cleaning_main_data(self) -> None:
        """
        Clean main plan data and build structured dictionaries.

        - Strips units (GB, min, SMS).
        - Cleans prices (EUR → float-like string).
        - Handles multiple prices by keeping the latest.
        Appends results into self.new_dict.
        """
        for name, value, price in zip(self.raw_names, self.raw_values, self.raw_prices):
            # Start a fresh entry for this plan.
            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['bon_bon']['provider'],
                'name': name,
                'price': '',
                'gb': '',
                'minutes': '',
                'sms': '',
                'units': '',
                'one_gb_price': '',
                'sixty_min_price': '',
                'thousand_units': ''
            }


            # Clean price → remove "EUR/tj." or "EUR/mj.", replace "," with ".", strip spaces.
            new_price = (price
                         .replace('EUR/tj.', '')
                         .replace('EUR/mj.', '')
                         .replace('EUR', '')
                         .replace(',', '.').strip())

            if 'Flat' in value:             # Internet flat packages
                entry['gb'] = value

            # Check type of value and put it in the correct field.
            elif 'GB' in value:              # Internet
                minutes = str(0)
                sms = str(0)
                gb = str(value.replace('GB', '').strip())
                entry['gb'] = str(gb)

                # Compute units and price per 1000 units
                units, thousand_units, one_gb_price = self.calculating(gb, minutes, sms, new_price)
                entry['units'] = str(units)
                entry['thousand_units'] = str(thousand_units)
                entry['one_gb_price'] = str(one_gb_price)


            elif 'min' in value:                      # Minutes
                minutes = value.replace('min', '').strip()
                sixty_min_price = round(float(new_price) / 60, 2)
                gb = str(0)
                sms = str(0)
                entry['minutes'] = str(minutes)

                # Compute units and price per 1000 units
                units, thousand_units, one_gb_price = self.calculating(gb, minutes, sms, new_price)
                entry['units'] = str(units)
                entry['thousand_units'] = str(thousand_units)
                entry['sixty_min_price'] = str(sixty_min_price)


            elif 'SMS' in value:                              # SMS
                sms = value.replace('SMS', '').strip()
                minutes = str(0)
                gb = str(0)
                entry['sms'] = str(sms)

                # Compute units and price per 1000 units
                units, thousand_units, one_gb_price = self.calculating(gb, minutes, sms, new_price)
                entry['units'] = str(units)
                entry['thousand_units'] = str(thousand_units)


            elif value == 'Video':                            # Special "Video" add-on
                pass

            elif value == 'Music':                            # Special "Music" add-on
                pass

            # Handle plans that have multiple prices (old + new).
            # If multiple → keep the *second* one (the new price).
            if len(new_price.split('\n')) > 1:
                entry['price'] = str(new_price.split('\n')[1])
            else:
                entry['price'] = str(new_price)

            # Save this structured plan into the main list.
            self.new_dict.append(entry)


    def finding_missing_names(self) -> None:
        """
        Find plan names not included in cleaned main data.

        Stores missing names in self.missing_names.
        """
        # Create a set of all names already in new_dict.
        dict_names = set(
            value['name']
            for value in self.new_dict
        )

        # Compare raw names to dict_names → names not yet added.
        self.missing_names = [
            name
            for name in self.raw_names
            if name not in dict_names
        ]


    def cleaning_pre_combined_prices(self) -> None:
        """
        Clean pre-combined prices by removing EUR and replacing ',' with '.'.
        """
        # Clean the list of pre-combined prices from the scraped page.
        # Remove 'EUR', convert commas to dots, and keep the latest price if multiple exist.
        self.clean_pre_combined_prices = [
            price.replace(',', '.').replace('EUR', '').strip().split(' ')[-1]
            for price in self.raw_pre_combined_prices
        ]


    def cleaning_pre_combined_values(self) -> None:
        """
        Clean pre-combined values by stripping units (GB, min, SMS).
        """
        # Clean the list of pre-combined values (like GB, min, SMS) from the scraped page.
        # Remove units and extra whitespace for easier processing later.
        self.clean_pre_combined_values = [
            value.replace('GB', '').replace('min', '').replace('SMS', '').strip()
            for value in self.raw_pre_combined_values
        ]


    def combining_pre_combined_data(self) -> None:
        """
        Combine pre-combined names, values, and prices.

        Groups values into minutes/GB/SMS triples
        and appends structured dicts into self.new_dict.
        """
        # Combine missing plan names with pre-combined prices and values
        # Each plan has 3 values: minutes, GB, SMS
        start = 0
        end = 3
        # Loop through missing names, their prices, and pre-combined values
        for name, price, value in zip(self.missing_names, self.clean_pre_combined_prices, self.clean_pre_combined_values):
            # Slice the next 3 values for minutes, GB, SMS
            minutes, gb, sms = self.clean_pre_combined_values[start:end]

            # Compute units and price per 1000 units
            units, thousand_units, one_gb_price = self.calculating(gb, minutes, sms, price)

            #Calculating sixty min price
            sixty_min_price = round(float(price) / 60, 2)

            # Build the dictionary for this plan
            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['bon_bon']['provider'],
                'name': name,
                'price': str(price),
                'gb': str(gb),
                'minutes': str(minutes),
                'sms': str(sms),
                'units': str(units),
                'one_gb_price': str(one_gb_price),
                'sixty_min_price': str(sixty_min_price),
                'thousand_units': str(thousand_units)
            }

            # Move the slice window for the next iteration
            start += 3
            end += 3

            # Append the structured plan to the final list
            self.new_dict.append(entry)


    def handling_data(self) -> None:
        """
        Run the full cleaning and combining pipeline.

        Prints each structured dictionary for verification.
        """
        # Clean main plan data
        self.cleaning_main_data()

        # Find any missing names that need to be added from pre-combined data
        self.finding_missing_names()

        # Clean the pre-combined prices (removing EUR, normalizing decimals)
        self.cleaning_pre_combined_prices()

        # Clean the pre-combined values (remove units like GB, min, SMS)
        self.cleaning_pre_combined_values()

        # Combine missing names with pre-combined prices/values into dictionaries
        self.combining_pre_combined_data()


    def run(self) -> None:
        """
        Orchestrate the full scraping workflow for Bon-Bon prepaid packages.

        Steps:
           1. Launch Playwright browser using a context manager.
           2. Navigate to the Bon-Bon page.
           3. Scrape main plan data (names, values, prices).
           4. Abort early if the page fails to load or no data is scraped.
           5. Close the browser to release system resources.
           6. Clean, normalize, and combine scraped data into structured dictionaries.

        Notes:
           - The actual data handling (`handling_data()`) is performed after the Playwright
             session ends to avoid accessing live browser objects during processing.
           - Assertions and early exits ensure type safety and prevent runtime errors
             if scraping fails.
        """
        # Launch Playwright and open browser context
        with sync_playwright() as self.p:
            # Open browser and navigate to Bon-Bon prepaid page
            self.fetch()

            # Safety check: abort if page not created
            if not self.page:
                logger.exception("Page not created. Aborting scraping.")
                return

            # Scrape main plan data from the website
            self.scraping_data()

            # Abort early if no data was retrieved
            if not self.raw_names:
                logger.exception("No data scraped. Aborting.")
                return

            # Ensure browser object exists before closing
            assert self.browser is not None  # For mypy/type safety
            self.browser.close()
            logger.info("Browser closed successfully.")

        # Process data ONLY after Playwright is fully done
        self.handling_data()
