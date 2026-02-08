import pytest
from price_comparison.scripts.scraping.a1 import A1


@pytest.fixture
def a1_instance():
    """Creates a fresh A1 instance for each test (without running Playwright)."""
    return A1.__new__(A1)


def test_calculating_with_gb(a1_instance):
    """Checking the result is correct when there is gb and price."""
    result = a1_instance.calculating(gb=5, price='2.99')
    assert result == (5000, 0.6, 0.6, 0.05)


def test_calculating_without_gb(a1_instance):
    """Checking the result is correct when there is no gb, but price."""
    result = a1_instance.calculating(gb=0, price='3.99')
    assert result == 0.07


def test_calculating_with_negative_gb(a1_instance):
    """Verify calculating() returns False when GB is negative (invalid input)."""
    result = a1_instance.calculating(gb=-5, price='2.99')
    assert result == False, f"Expected False for negative GB, got {result}"


def test_calculating_with_string_price(a1_instance):
    """Checking if price passed as string."""
    result = a1_instance.calculating(gb=8, price='abc')
    assert result == False


def test_calculating_with_string_gb(a1_instance):
    """Checking if gb passed as string."""
    result = a1_instance.calculating(gb='abc', price='8.99')
    assert result == False


def test_cleaning_main_names(a1_instance):
    """Ensure cleaning_main_names() trims whitespace and returns clean tariff names."""

    # Simulated scraped data
    a1_instance.raw_main_names = ['   Flat', 'Full    ', '    Super   ']

    # Call the function we want to test
    a1_instance.cleaning_main_names()

    # Define what we expect
    expect = ['Flat', 'Full', 'Super']

    # Assert that the output matches
    assert a1_instance.clean_main_names == expect, (
        "Tariff names (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.clean_main_names}."
    )


def test_cleaning_main_names_empty(a1_instance):
    """Ensure cleaning_main_names() handles empty input without errors and returns an empty list."""
    a1_instance.raw_main_names = []
    a1_instance.cleaning_main_names()
    assert a1_instance.clean_main_names == []


def test_cleaning_main_prices(a1_instance):
    """Ensure cleaning_main_prices() converts price strings to decimals (e.g. '29,99 €/mj.' → '29.99')."""

    # Simulated scraped data
    a1_instance.raw_main_prices = ['   29,99 €/mj.', '39,99 mjesečno    ', '49,99  €/mj.', '56,99€\nCijena za tri mjeseca']

    # Call the function we want to test
    a1_instance.cleaning_main_prices()

    # Define what we expect
    expect = ['29.99', '39.99', '49.99', '56.99']

    # Assert that the output matches
    assert a1_instance.clean_main_prices == expect, (
        "Main prices (A1) not cleaned correctly: "
        f"Expected: {expect}, but got {a1_instance.clean_main_prices}."
    )


def test_cleaning_main_prices_empty(a1_instance):
    """Ensure cleaning_main_prices() handles empty input without errors and returns an empty list."""
    a1_instance.raw_main_prices = []
    a1_instance.cleaning_main_prices()
    assert a1_instance.clean_main_prices == []


def test_cleaning_main_values(a1_instance):
    """Verify cleaning_main_values() removes filler text and keeps valid numeric or word values."""

    # Simulated scraped data
    a1_instance.raw_main_values = ['  Neograničeni   ', '  Saznaj više ', 'Saznaj više', '  3000 ', ' 20 ', '10']

    # Call the function we want to test
    a1_instance.cleaning_main_values()

    # Define what we expect
    expect = ['Neograničeni', '3000', '20', '10']

    # Assert that the output matches
    assert a1_instance.clean_main_values == expect, (
        "Main values (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.clean_main_values}."
    )


def test_cleaning_main_values_empty(a1_instance):
    """Ensure cleaning_main_values() handles empty input without errors and returns an empty list."""
    a1_instance.raw_main_values = []
    a1_instance.cleaning_main_values()
    assert a1_instance.clean_main_values == []


def test_cleaning_add_names(a1_instance):
    """Ensure cleaning_add_names() filters out promo text and returns valid add-on names."""

    # Simulated scraped data
    a1_instance.raw_add_names = [
        'Promo text 1', 'Promo text 2', 'Promo text 3', # Those tree are always skipped
        '   Weekend unlimited    ',
        '5 GIGA     ',
        '     1 GIGA']

    # Call the function we want to test
    a1_instance.cleaning_add_names()

    # Define what we expect
    expect = ['Weekend unlimited', '5 GIGA', '1 GIGA']

    # Assert that the output matches
    assert a1_instance.clean_add_names == expect, (
        "Add names (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.clean_add_names}."
    )


def test_cleaning_add_names_empty(a1_instance):
    """Ensure cleaning_add_names() handles empty inputs without errors and returns an empty list."""
    a1_instance.raw_add_names = []
    a1_instance.cleaning_add_names()
    assert a1_instance.clean_add_names == []


def test_cleaning_add_prices(a1_instance):
    """Verify cleaning_add_prices() correctly extracts and formats numeric add-on prices."""

    # Simulate scraped data
    a1_instance.raw_add_prices = ['3,99€   ', '      4,99€', '', '5,99€         ']

    # Call the function we want to test
    a1_instance.cleaning_add_prices()

    # Define what we expect
    expect = ['3.99', '4.99', '5.99']

    # Assert that output matches
    assert a1_instance.clean_add_prices == expect, (
        "Add prices (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.clean_add_prices}."
    )


def test_cleaning_add_prices_empty(a1_instance):
    """Ensure cleaning_add_prices() handles empty input without errors and returns an empty list."""

    a1_instance.raw_add_prices = []
    a1_instance.cleaning_add_prices()
    assert a1_instance.clean_add_prices == []


def test_cleaning_add_gbs(a1_instance):
    """Ensure cleaning_add_gbs() extracts only numeric GB or unit values from text."""

    # Simulate scraped data
    a1_instance.raw_add_gbs = [
        '   10 GB interneta koji traju 30 dana.   ',
        '5 GB interneta koji traju 30 dana.',
        '   500 min/SMS koji traju 30 dana.   ']

    # Call the function we want to test
    a1_instance.cleaning_add_gbs()

    # Define what we expect
    expect = ['10', '5', '500']

    # Assert that output matches
    assert a1_instance.clean_add_gbs == expect, (
        "Add gbs (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.clean_add_gbs}."
    )


def test_cleaning_add_gbs_empty(a1_instance):
    """Ensure cleaning_add_gbs() handles empty input without errors and returns an empty list."""

    a1_instance.raw_add_gbs = []
    a1_instance.cleaning_add_gbs()
    assert a1_instance.clean_add_gbs == []


def test_all_together_main(a1_instance):
    """Verify all_together_main() correctly builds dictionaries from main plan data and mock calculations."""

    # Define list which will hold dictionaries
    a1_instance.new_dict = []

    # Define mocking names
    a1_instance.clean_main_names = ['Super', 'Fer']

    # Define mocking prices
    a1_instance.clean_main_prices = ['2.99', '3.99']

    # Define mocking values
    a1_instance.clean_main_values = ['5', '5000', '4', '4000']

    def mock_calculating(gb, price):
        """Returns units, one_gb_price, thousand_units, sixty_min_price."""
        return 1000, 2.0, 2000.0, 3.0

    # Define instance calculating with mock_calculating
    a1_instance.calculating = mock_calculating

    # Calling the function we want to test
    a1_instance.all_together_main()

    # Define what we expect
    expect = [
        {
        'provider': 'A1',
        'name': 'Super',
        'price': '2.99',
        'gb': '5',
        'minutes': '5000',
        'sms': '',
        'music': '',
        'video': '',
        'units': '1000',
        'one_gb_price': '2.0',
        'sixty_min_price': '3.0',
        'thousand_units': '2000.0'
        },
        {
        'provider': 'A1',
        'name': 'Fer',
        'price': '3.99',
        'gb': '4',
        'minutes': '4000',
        'sms': '',
        'music': '',
        'video': '',
        'units': '1000',
        'one_gb_price': '2.0',
        'sixty_min_price': '3.0',
        'thousand_units': '2000.0'
        }
    ]

    # Assert that output matches
    assert a1_instance.new_dict == expect, (
        "All together main (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.new_dict}."
    )


def test_all_together_main_empty(a1_instance):
    """Ensure all_together_main() handles empty input without errors and returns an empty list."""
    a1_instance.new_dict = []
    a1_instance.clean_main_names = []
    a1_instance.clean_main_prices = []
    a1_instance.clean_main_values = []
    a1_instance.all_together_main()
    assert a1_instance.new_dict == []


def test_all_together_add(a1_instance):
    """Verify all_together_add() correctly builds dictionaries from add-on plan data and mock calculations."""

    # Define list which will hold dictionaries
    a1_instance.new_dict = []

    # Define mocking add names
    a1_instance.clean_add_names = ['Uzmi 9', 'Tjedni flat']

    # Define mocking add prices
    a1_instance.clean_add_prices = ['3.99', '4.99']

    # Define mocking add gbs
    a1_instance.clean_add_gbs = ['9', '10']


    def mock_calculating(gb, price):
        """Returns units, one_gb_price, thousand_units, sixty_min_price."""
        return 2000, 0.2, 2000.0, 0.34

    # Define instance calculating with mock_calculating
    a1_instance.calculating = mock_calculating

    # Calling function we want to test
    a1_instance.all_together_add()

    # Define what we expect
    expect = [
        {
        'provider': 'A1',
        'name': 'Uzmi 9',
        'price': '3.99',
        'gb': '9',
        'minutes': '',
        'sms': '',
        'music': '',
        'video': '',
        'units': '2000',
        'one_gb_price': '0.2',
        'sixty_min_price': '0.34',
        'thousand_units': '2000.0'
        },
        {
        'provider': 'A1',
        'name': 'Tjedni flat',
        'price': '4.99',
        'gb': '10',
        'minutes': '',
        'sms': '',
        'music': '',
        'video': '',
        'units': '2000',
        'one_gb_price': '0.2',
        'sixty_min_price': '0.34',
        'thousand_units': '2000.0'
        }
    ]

    # Assert that output matches
    assert a1_instance.new_dict == expect, (
        "All together add (A1) not cleaned correctly: "
        f"Expected: {expect}, but got: {a1_instance.new_dict}."
    )


def test_all_together_add_empty(a1_instance):
    """Ensure all_together_add() handles empty input without errors and returns an empty list."""
    a1_instance.new_dict = []
    a1_instance.clean_add_names = []
    a1_instance.clean_add_prices = []
    a1_instance.clean_add_gbs = []
    a1_instance.all_together_add()
    assert a1_instance.new_dict == []




