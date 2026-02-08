"""
CSS selectors for scraping Tomato mobile tariffs.

This module defines the `tariffs` dictionary containing all CSS selectors
used to scrape plan information from Tomato’s web pages.

Structure:

- `tariffs['tomato']` : dict[str, str]
    Dictionary of CSS selectors for Tomato prepaid plans:
    - `names` : plan names
    - `units` : included units (e.g., minutes or MB/GB)
    - `prices` : plan prices

Example usage:

    plan_names = page.locator(tariffs['tomato']['names']).all_inner_texts()
    plan_units = page.locator(tariffs['tomato']['units']).all_inner_texts()
    plan_prices = page.locator(tariffs['tomato']['prices']).all_inner_texts()
"""
tariffs = {
    'tomato': {
        'names': '.tariff-listing-card__subtitle',
        'units': '.tariff-listing-card__title',
        'prices': '.tariff-price__amount'
    }
}