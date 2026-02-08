"""
CSS selectors for scraping Telemach mobile tariffs.

This module defines the `tariffs` dictionary containing all CSS selectors
used to scrape plan information from Telemach’s web pages.

Structure:

- `tariffs['telemach']` : dict[str, dict[str, str]]
    Dictionary containing CSS selectors for different plan sections:

    - `main` : dict[str, str]
        Selectors for main plans:
        - `names` : plan names
        - `gbs` : included data (GB) or dropdown indicators
        - `values` : plan values (e.g., minutes or GB)
        - `prices` : plan prices
    - `add` : dict[str, str]
        Selectors for additional plans:
        - `names` : plan names
        - `gbs` : included data (GB) or dropdown indicators
        - `prices` : plan prices

Example usage:

    main_plan_names = page.locator(tariffs['telemach']['main']['names']).all_inner_texts()
"""
tariffs = {
    'telemach': {
        'main': {
            'names': '.package-title-block.flex.flex-nowrap.align-center',
            'gbs': '.package-dropdown-block-title-arrow-wrap',
            'values': '.font-5.fs-text-16.line-height-8.color-1',
            'prices': '.font-6.fs-text-48.line-height-8.color-1'
        },
        'add': {
            'names': '.package-title-block-left.flex-grow-1',
            'gbs': '.package-dropdown-block-title-arrow-wrap',
            'prices': '.package-price-block'
        }
    }
}