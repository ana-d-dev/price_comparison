from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
from price_comparison.config.providers import providers
from price_comparison.tariff_selectors.tcom import tariffs
from price_comparison.logger_config import setup_logger
from datetime import date


logger = setup_logger('T-Com')
class TCom:
    def __init__(self):
        """
        Initializes the TCom scraper.

        Sets current date and time for SQL entries.
        Prepares Playwright browser/page attributes for scraping.
        Prepares lists for storing scraped and cleaned data.
        - `buttons` will hold plan buttons once found.
        - `all_data` will store combined results from all tariff types.

        Note: Importing `logger_config` sets up logging with loguru.
        """
        # Storing date for last scraping
        self.scraped_date = date.today()

        # Playwright browser/page objects and plan buttons container
        self.browser: Browser | None = None           # Playwright browser instance
        self.page: Page | None = None                 # Playwright page object
        self.buttons: list[ElementHandle] = []        # Will hold plan buttons once found

        # Raw scraped main plan data
        self.main_raw_names: list[str] = []           # Names as scraped from the website
        self.main_raw_prices: list[str] = []          # Prices as scraped from the website
        self.main_raw_gbs_minutes: list[str] = []     # GBs and minutes as scraped from the website

        # Raw scraped additional plan data
        self.add_raw_names: list[str] = []            # Names as scraped from the "additional" page
        self.add_raw_prices: list[str] = []           # Prices as scraped from the "additional" page
        self.add_raw_gbs: list[str] = []              # GBs as scraped from the "additional" page

        # Cleaned main tariffs data
        self.main_names: list[str] = []               # Names after stripping whitespace
        self.main_prices: list[str] = []              # Prices extracted and formatted as float strings
        self.main_gbs: list[str] = []                 # GB values extracted from raw strings
        self.main_minutes: list[str] = []             # Minutes extracted from raw strings

        # Cleaned additional tariffs data
        self.add_names: list[str] = []                # Names after stripping whitespace
        self.add_prices: list[str] = []               # Prices extracted and formatted as float strings
        self.add_gbs: list[str] = []                  # GB values extracted from raw strings, cleaned of units

        # Combined data from all tariffs
        self.new_dict: list[dict] = []                # Stores dictionaries for each plan from main, additional, and e-Simpa tariffs


    def calculating(self, price: str, gb: str, mins:str):
        if gb == '0':
            sixty_min_price = round(float(price) / 60, 2)              # 60-minute equivalent price
            units = (int(gb) * 1000) + int(mins)                       # Total units for comparison
            one_unit = float(price) / units                            # Calculate price per unit
            thousand_units = round(one_unit * 1000, 2)                 # Calculate a thousand units price
            return sixty_min_price, units, thousand_units

        else:
            one_gb_price = round(float(price) / int(gb), 2)            # Price per GB
            units = (int(gb) * 1000) + int(mins)                       # Total units for comparison
            one_unit = float(price) / units                            # Calculate price per unit
            thousand_units = round(one_unit * 1000, 2)                 # Calculate price for 1000 units
            sixty_min_price = round(float(price) / 60, 2)              # 60-minute equivalent price

            return one_gb_price, units, thousand_units, sixty_min_price


    def fetch(self) -> None:
        """
        Launch the browser, open a new page, and navigate to the TCom main URL.
        Logs an exception if the page cannot be opened.
        """
        try:
            # Launch browser instance (headless=False for debugging)
            self.browser = self.p.chromium.launch(headless=False)

            # Open a new browser page
            self.page = self.browser.new_page()

            # Navigate to TCom main page
            self.page.goto(providers['t_com']['urls']['main'], wait_until="domcontentloaded", timeout=15000)
            logger.info('T-Com main page loaded.')
        except Exception:
            logger.exception(
                f"Failed to load T-Com main page: {providers['t_com']['urls']['main']}"
            )


    def handling_cookies(self) -> None:
        """
        Finds and clicks the cookies acceptance button.
        Logs an exception if the button is not found.
        """
        try:
            assert self.page is not None
            self.page.click(tariffs['t_com']['cookies'])
            logger.info('Cookies banner accepted.')
        except Exception:
            logger.exception(f"Failed to click cookie banner: selector={tariffs['t_com']['cookies']}")


    def finding_buttons(self) -> None:
        """
        Finds all plan buttons on the page and stores them in self.buttons.
        Logs an exception if no buttons are found.
        """
        try:
            assert self.page is not None
            self.buttons = self.page.query_selector_all(tariffs['t_com']['main']['plan_buttons'])
            logger.info('Main plan buttons located.')
        except Exception:
            logger.exception( f"Failed to query plan buttons: selector={tariffs['t_com']['main']['plan_buttons']}")


    def taking_main_data(self) -> None:
        """
        Scrapes raw text from each main plan button.
        Logs an exception if scraping fails or buttons are missing.
        """
        try:
            assert self.page is not None
            for button in self.buttons[:-2]:
                button.click()
                self.main_raw_names.append(' '.join(self.page.locator(tariffs['t_com']['main']['name']).all_text_contents()))
                self.main_raw_prices.append(' '.join(list(self.page.locator(tariffs['t_com']['main']['price']).all_text_contents())))
                self.main_raw_gbs_minutes.append(' '.join(list(self.page.locator(tariffs['t_com']['main']['gb']).all_text_contents())))
            logger.info('Main tariff data scraped.')
        except Exception:
            logger.exception(
                "Failed scraping main plan data. "
                f"name={tariffs['t_com']['main']['name']} "
                f"price={tariffs['t_com']['main']['price']} " 
                f"gb={tariffs['t_com']['main']['gb']}"
            )

    def taking_add_data(self) -> None:
        """
        Scrapes raw text from additional plan options.
        Logs an exception if the page is not found or selectors are changed.
        """
        try:
            assert self.page is not None
            # Navigate to additional plans page
            self.page.goto(providers['t_com']['urls']['add'])

            # Collect all additional plan info
            self.add_raw_names = self.page.locator(tariffs['t_com']['add']['name']).all_text_contents()
            self.add_raw_prices = self.page.locator(tariffs['t_com']['add']['price']).all_text_contents()
            self.add_raw_gbs = self.page.locator(tariffs['t_com']['add']['gb']).all_text_contents()
            logger.info('Additional plan data scraped.')

        except Exception:
            logger.exception(
                "Failed scraping additional plans. "
                f"name={tariffs['t_com']['add']['name']} "
                f"price={tariffs['t_com']['add']['price']} "
                f"gb={tariffs['t_com']['add']['gb']}"
            )


    def cleaning_main_data(self) -> None:
        """
        Cleans all main scraped data and stores them in dedicated lists for names, prices, GBs, and minutes.
        Assumes that raw strings are in the expected format and contain both GB and minute info.
        """
        # Remove extra spaces from names
        self.main_names = [
            name.strip()
            for name in self.main_raw_names
        ]

        # Extract numeric price
        self.main_prices = [
            price.split(' ')[0].replace(',', '.')
            for price in self.main_raw_prices
        ]

        # Extract GB value
        self.main_gbs = [
            gbs_m.split(' ')[0]
            for gbs_m in self.main_raw_gbs_minutes
        ]

        # Extract minutes value
        self.main_minutes = [
            gbs_m.split(' ')[4]
            for gbs_m in self.main_raw_gbs_minutes
        ]


    def cleaning_add_data(self) -> None:
        """
        Cleans additional scraped data and stores them in dedicated lists for names, prices, and GBs.
        Assumes that raw strings are in the expected format and contain both GB and minute info.
        """
        # Remove extra spaces from names
        self.add_names = [
            name.strip()
            for name in self.add_raw_names
        ]

        # Extract numeric price
        self.add_prices = [
            i.strip().split(' ')[0].replace(',', '.')
            for i in self.add_raw_prices
        ]

        # Clean GB values
        self.add_gbs = [
            gb.replace('GB', ' ').replace('MIN', ' ').strip()
            for gb in self.add_raw_gbs
        ]


    def all_together(self, names: list[str], prices: list[str], gbs: list[str], minutes: list[str]) -> None:
        """
        Combines main and e-Simpa data into a list of dictionaries.
        Each dictionary contains provider info, date/time, plan details, and calculated metrics.
        """
        for name, price, gb, mins in zip(names, prices, gbs, minutes):

            one_gb_price, units, thousand_units, sixty_min_price = self.calculating(price, gb, mins)

            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['t_com']['provider'],    # Provider name
                'name': name,                                  # Plan name
                'price': str(price),                           # Plan price in EUR
                'gb': str(gb),                                 # Plan GB
                'minutes': str(mins),                          # Plan minutes
                'sms': '',                                     # Plan sms
                'units': str(units),                           # Store total units
                'one_gb_price': str(one_gb_price),             # Price per GB for numeric GB plans
                'sixty_min_price': str(sixty_min_price),       # Store 60-min price
                'thousand_units': str(thousand_units),         # Store price for 1000 units
                 }
            self.new_dict.append(entry)


    def all_together_add(self) -> None:
        """
        Combines additional plan data with main and e-Simpa data.
        Handles cases where additional plans may not have minutes.
        """
        # Iterate over each additional plan
        for name, price, gb in zip(self.add_names, self.add_prices, self.add_gbs):
            # Initialize dictionary with basic plan info
            entry = {
                'scraped_date': self.scraped_date,
                'provider': providers['t_com']['provider'],   # Provider name
                'name': name,                                 # Plan name
                'price': price,                               # Plan price in EUR
                'gb': '',                                     # Plan gb
                'minutes': '',                                # Plan minutes
                'sms': '',                                    # Plan sms
                'units': '',                                  # Plan units
                'one_gb_price': '',                           # Store one gb price
                'sixty_min_price': '',                        # Store 60 min price
                'thousand_units': ''                          # Store 1000 units price
            }

            if name == 'Pričam':
                minutes = gb  # Store minutes from GB variable
                sixty_min_price, units, thousand_units = self.calculating(price, '0', minutes)

                entry['sixty_min_price'] = str(sixty_min_price)  # Store 60-min price
                entry['minutes'] = str(minutes)  # Store actual minutes
                entry['units'] = str(units)   # Store calculated units
                entry['thousand_units'] = str(thousand_units) # Store calculated a thousand units

            # Numeric GB plans (calculate price per GB and total units)
            elif gb.isnumeric():
                one_gb_price, units, thousand_units, sixty_min_price = self.calculating(price, gb, '0')

                entry['gb'] = gb                                         # Store GB
                entry['one_gb_price'] = str(one_gb_price)                # Store price per GB
                entry['units'] = str(units)                              # Store total units
                entry['thousand_units'] = str(thousand_units)            # Store thousand units


            # Append plan dictionary to combined data list
            self.new_dict.append(entry)


    def handling_data(self) -> None:
        """
        Calls all cleaning and combining functions to prepare the final dataset.
        Prints all combined data for verification.
        """
        # Clean main plan data
        self.cleaning_main_data()

        # Clean additional plan data
        self.cleaning_add_data()

        # Combine main plan data
        self.all_together(self.main_names, self.main_prices, self.main_gbs, self.main_minutes)

        # Combine additional plan data
        self.all_together_add()




    def run(self) -> None:
        """
        Orchestrate the full scraping workflow for T-Com prepaid plans.

        Steps:
            1. Launch Playwright browser using a context manager.
            2. Navigate to T-Com main page and accept cookies.
            3. Locate all plan buttons on the main page.
            4. Scrape main and additional plan data.
            5. Abort early with logging if the page fails to load or no data is scraped.
            6. Close the browser to release resources.
            7. Clean, normalize, and combine scraped data into structured dictionaries.

        Notes:
            - Data processing (`handling_data()`) happens after Playwright session ends
              to avoid accessing live browser objects during data cleaning.
            - Safety checks and `assert` statements prevent runtime errors when
              scraping fails, ensuring mypy knows objects are not None.
        """
        with sync_playwright() as self.p:
            # Launch browser and go to main T-Com page
            self.fetch()

            # Accept cookies if prompted
            self.handling_cookies()

            # Find all plan buttons on main page
            self.finding_buttons()

            # Safety check: abort if page not created
            if not self.page:
                logger.exception("Page not created. Aborting scraping.")
                return

            # Scrape main plan data
            self.taking_main_data()

            # Scrape additional plan data
            self.taking_add_data()

            # Abort early if no data scraped
            if not self.main_raw_names or not self.add_raw_names:
                logger.exception("No data scraped. Aborting.")
                return

            # Close browser safely after scraping
            assert self.browser is not None   # For mypy/type safety
            self.browser.close()
            logger.info('Browser closed successfully.')

        # Clean and combine all scraped data
        self.handling_data()
