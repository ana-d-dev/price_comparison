"""
CSS selectors for scraping A1 mobile tariffs.

This module defines the `tariffs` dictionary containing the CSS selectors
used to scrape plan information from A1’s web pages.

Structure:

- `tariffs['a1']` : dict[str, str]
    Dictionary of CSS selectors for different elements:
    - `buttons` : plan selection radio buttons
    - `main_names` : main plan names
    - `main_values` : main plan values (e.g., GB or minutes)
    - `main_prices` : main plan prices
    - `add_names` : additional plan names
    - `add_prices` : additional plan prices
    - `add_gbs` : additional GB values
    - `cookie_button` : cookie consent button

Example usage:

    main_plan_names = page.locator(tariffs['a1']['main_names']).all_inner_texts()
"""
tariffs = {
    'a1': {
        'buttons': '.field-radio__indicator',
        'main_names': '.card-prepaid__title.font-serif',
        'main_values': '.text-red.font-bold',
        'main_prices': '.card-prepaid__top',
        'add_names': '.title',
        'add_prices': '.price',
        'add_gbs': '.description',
        'cookie_button': 'button#onetrust-accept-btn-handler'
    }
}
