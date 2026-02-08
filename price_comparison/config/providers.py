"""
Configuration for mobile tariff providers.

This module defines the `providers` dictionary containing metadata
for each provider and their relevant URLs for scraping or reference.

Data structure:

- `providers` : dict[str, ProviderConfig]
    A dictionary where each key is a short identifier for a provider
    (e.g., 't_com', 'tomato') and each value is a ProviderConfig dictionary
    containing:

    - `provider` : str
        The official name of the provider.
    - `urls` : ProviderURLs
        A dictionary of relevant URLs for the provider. Possible keys:
        - `main` (str) : Main page for the provider’s tariffs.
        - `add` (str, optional) : Additional tariffs page, if available.
        - `e_simpa` (str, optional) : Specific page for e-Simpa options, if available.

Example usage:

    from providers import providers

    tomato_main_url = providers['tomato']['urls']['main']
"""
from typing import TypedDict


class ProviderURLs(TypedDict, total=False):
    main: str
    add: str
    e_simpa: str


class ProviderConfig(TypedDict):
    provider: str
    urls: ProviderURLs

# Links for every tariff and PROVIDER name
providers: dict[str, ProviderConfig] = {
    't_com': {
        'provider':'T-COM',
        'urls':{
            'main':'https://www.hrvatskitelekom.hr/simpa-opcije',
            'add':'https://www.hrvatskitelekom.hr/dodatne-simpa-opcije#internet',
            'e_simpa': 'https://www.hrvatskitelekom.hr/e-simpa-opcije',
            }
        },

    'tomato': {
        'provider': 'TOMATO',
        'urls': {
            'main': 'https://www.tomato.com.hr/tarife-na-bonove'
            },
        },
    'bon_bon': {
        'provider': 'BONBON',
        'urls': {
            'main': 'https://www.bonbon.hr/ponuda/na-bonove/paketi#/'
            }
        },
    'telemach': {
        'provider': 'TELEMACH',
        'urls':{
            'main':'https://telemach.hr/mobilna-telefonija/paketi-na-bonove',
            'add': 'https://telemach.hr/mobilni-internet/paketi-na-bonove'
            },
        },
    'a1': {
        'provider': 'A1',
        'urls': {
            'main': 'https://www.a1.hr/privatni/mobiteli/a1-na-bonove'
        }
    }
}
