"""
CSS selectors for scraping T-COM mobile tariffs.

This module defines the `tariffs` dictionary containing all CSS selectors
used to scrape plan information from T-COM’s web pages.

Structure:

- `tariffs['t_com']` : dict[str, Any]
    Dictionary containing the CSS selectors for different plan sections:

    - `main` : dict[str, str]
        Selectors for main plans:
        - `plan_buttons` : plan selection radio buttons
        - `name` : plan name
        - `price` : plan price
        - `gb` : included GB or data
        - `min` : included minutes
    - `add` : dict[str, str]
        Selectors for additional plans:
        - `name` : plan name
        - `price` : plan price
        - `gb` : included GB or data
    - `e_simpa` : dict[str, str]
        Selectors for e-Simpa plans:
        - `name` : plan name
        - `price` : plan price
        - `gb_min` : included GB or minutes
    - `cookies` : str
        Selector for the cookie consent button.

Example usage:

    main_plan_names = page.locator(tariffs['t_com']['main']['name']).all_inner_texts()
"""
from typing import Dict, Any

tariffs: Dict[str, Dict[str, Any]] = {
    't_com' : {
        'main': {
            'plan_buttons': '.confbtn-container .confbtn-gray',
            'name': '.headline-container',
            'price': '.price-total',
            'gb': '.general p',
            'min': '.general p'
        },
        'add' : {
            'name': '.l',
            'price': '.price-total',
            'gb': "div.p-i-content > div:nth-child(1)"
        },
        'e_simpa': {
            'name': '.l',
            'price': '.price-total >> visible=true',
            'gb_min': '.text-bold >> visible=true'
        },
        'cookies': '#cookies-notification-accept-cookie'

    }
}


