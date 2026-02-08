from price_comparison.scripts.scraping.bon import Bon
import pytest


@pytest.fixture()
def bon_instance():
    """Create new clean instance without triggering playwright."""
    return Bon.__new__(Bon)


def test_calculating_gb(bon_instance):
    """Verify calculating() returns correct results when GB value is provided."""
    result = bon_instance.calculating(gb=2, minutes=3000, sms=100, price=3.99)
    assert result == (5100, 0.78, 2.0)


def test_calculating_gb_zero(bon_instance):
    """Verify calculating() handles GB value of zero correctly."""
    result = bon_instance.calculating(gb=0, minutes=2000, sms=500, price=2.99)
    assert result == (2500, 1.2, None)


def test_cleaning_main_data(bon_instance):
    """Verify cleaning_main_data() correctly creates dictionaries from main data."""
    bon_instance.raw_names = ['Mali tjedni internet', 'Jako jako veliki internet', 'Veliki razgovori']
    bon_instance.raw_prices = ['  2,99EUR/tj.             ', '3,99EUR/tj.                   ', '                    4,99EUR/tj.']
    bon_instance.raw_values = ['  8GB                     ', '500min                        ', '                    200SMS']
    bon_instance.new_dict = []
    bon_instance.cleaning_main_data()

    expect = [
        {
            'provider': 'BONBON',
            'name': 'Mali tjedni internet',
            'price': '2.99',
            'gb': '8',
            'minutes': '',
            'sms': '',
            'music': '',
            'video': '',
            'units': '8000',
            'one_gb_price': '0.37',
            'sixty_min_price': '',
            'thousand_units': '0.37'
        },
        {
            'provider': 'BONBON',
            'name': 'Jako jako veliki internet',
            'price': '3.99',
            'gb': '',
            'minutes': '500',
            'sms': '',
            'music': '',
            'video': '',
            'units': '500',
            'one_gb_price': '',
            'sixty_min_price': '0.07',
            'thousand_units': '7.98'
        },
        {
            'provider': 'BONBON',
            'name': 'Veliki razgovori',
            'price': '4.99',
            'gb': '',
            'minutes': '',
            'sms': '200',
            'music': '',
            'video': '',
            'units': '200',
            'one_gb_price': '',
            'sixty_min_price': '',
            'thousand_units': '24.95'
        }
    ]
    assert bon_instance.new_dict == expect, (
        f"Expect: {expect}, but got: {bon_instance.new_dict}."
    )


def test_cleaning_main_data_empty(bon_instance):
    """Verify cleaning_main_data() handles empty lists without errors."""
    bon_instance.new_dict = []
    bon_instance.raw_names = []
    bon_instance.raw_prices = []
    bon_instance.raw_values = []
    bon_instance.cleaning_main_data()
    assert bon_instance.new_dict == []


def test_finding_missing_names(bon_instance):
    """Verify finding_missing_names() correctly identifies missing names."""
    bon_instance.raw_names = ['Jako veliki internet', 'Veliki razgovori', 'Mali sms']
    bon_instance.new_dict = [
        {'name': 'Jako veliki internet'},
        {'name': 'Mali sms'}
    ]
    bon_instance.finding_missing_names()
    expect = ['Veliki razgovori']
    assert bon_instance.missing_names == expect, (
        f"Expect: {expect}, but got: {bon_instance.missing_names}."
    )


def test_finding_missing_names_empty(bon_instance):
    """Verify finding_missing_names() handles empty lists without errors."""
    bon_instance.raw_names = []
    bon_instance.new_dict = []
    bon_instance.finding_missing_names()
    assert bon_instance.missing_names == []


def test_cleaning_pre_combined_prices(bon_instance):
    """Verify cleaning_pre_combined_prices() extracts and cleans the correct price values."""
    bon_instance.raw_pre_combined_prices = ['16,00 EUR 13,50 EUR', '21,00 EUR 16,50 EUR']
    bon_instance.cleaning_pre_combined_prices()
    expect = ['13.50', '16.50']
    assert bon_instance.clean_pre_combined_prices == expect, (
        f"Expect: {expect}, but got: {bon_instance.clean_pre_combined_prices}."
    )


def test_cleaning_pre_combined_prices_empty(bon_instance):
    """Verify cleaning_pre_combined_prices() handles empty lists without errors."""
    bon_instance.raw_pre_combined_prices = []
    bon_instance.cleaning_pre_combined_prices()
    assert bon_instance.clean_pre_combined_prices == []


def test_cleaning_pre_combined_values(bon_instance):
    """Verify cleaning_pre_combined_values() removes text and keeps only numeric values."""
    bon_instance.raw_pre_combined_values = ['   4000 min', '   14 GB', '500 SMS    ', '    4000 min     ', '25     GB', '500     SMS']
    bon_instance.cleaning_pre_combined_values()
    expect = ['4000', '14', '500', '4000', '25', '500']
    assert bon_instance.clean_pre_combined_values == expect, (
        f"Expect: {expect}, but got: {bon_instance.clean_pre_combined_values}."
    )


def test_cleaning_pre_combined_values_empty(bon_instance):
    """Verify cleaning_pre_combined_values() handles empty lists without errors."""
    bon_instance.raw_pre_combined_values = []
    bon_instance.cleaning_pre_combined_values()
    assert bon_instance.clean_pre_combined_values == []


def test_combining_pre_combined_data(bon_instance):
    """Verify combining_pre_combined_data() creates complete dictionaries from pre-cleaned data."""
    bon_instance.new_dict = []
    bon_instance.current_date = '02.11.2025.'
    bon_instance.current_time = '05:35:25'
    bon_instance.missing_names = ['Velika kombinacija', 'Jako velika kombinacija']
    bon_instance.clean_pre_combined_prices = ['13.50', '16.50']
    bon_instance.clean_pre_combined_values = ['4000', '14', '500', '4000', '25', '500']

    def mock_calculating(gb, minutes, sms, price):
        return 18500, 0.73, 0.96

    bon_instance.calculating = mock_calculating
    bon_instance.combining_pre_combined_data()


    expect = [
        {
            'provider': 'BONBON',
            'name': 'Velika kombinacija',
            'price': '13.50',
            'gb': '14',
            'minutes': '4000',
            'sms': '500',
            'music': '',
            'video': '',
            'units': '18500',
            'one_gb_price': '0.96',
            'sixty_min_price': '0.23',
            'thousand_units': '0.73'
        },
        {
            'provider': 'BONBON',
            'name': 'Jako velika kombinacija',
            'price': '16.50',
            'gb': '25',
            'minutes': '4000',
            'sms': '500',
            'music': '',
            'video': '',
            'units': '18500',
            'one_gb_price': '0.96',
            'sixty_min_price': '0.28',
            'thousand_units': '0.73'
        }

    ]
    assert bon_instance.new_dict == expect, (
        f"Expect: {expect}, but got: {bon_instance.new_dict}."
    )


def test_combining_pre_combined_data_empty(bon_instance):
    """Verify combining_pre_combined_data() handles empty input lists without errors."""
    bon_instance.new_dict = []
    bon_instance.missing_names = []
    bon_instance.clean_pre_combined_prices = []
    bon_instance.clean_pre_combined_values = []
    bon_instance.combining_pre_combined_data()
    assert bon_instance.new_dict == []