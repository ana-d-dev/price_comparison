"""
CSS selectors for scraping Bonbon mobile tariffs.

This module defines the `tariffs` dictionary containing CSS selectors
used to scrape plan information from Bonbon’s web pages.

Structure:

- `tariffs['bon_bon']` : dict[str, str]
    Dictionary of CSS selectors for different elements:
    - `names` : plan names
    - `values` : plan values (e.g., GB or minutes)
    - `prices` : plan prices
    - `pre_combined_values` : values for pre-combined plans
    - `pre_combined_prices` : prices for pre-combined plans

Example usage:

    plan_names = page.locator(tariffs['bon_bon']['names']).all_inner_texts()
"""
tariffs = {
    'bon_bon': {
        'names': '.name.opt-head.option__name.ng-star-inserted',
        'values': '.value-text.option__data',
        'prices': '.price-text.option__price.ng-star-inserted',
        'pre_combined_values': '.value-text.option__data.ng-star-inserted',
        'pre_combined_prices': '.price-text.option__price.option__price--large'
    }
}