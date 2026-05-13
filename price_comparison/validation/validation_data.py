ALLOWED_PROVIDERS = ['A1', 'BONBON', 'T-COM', 'TELEMACH', 'TOMATO']
ALLOWED_GB = ['Neograničen', 'Neograničeni', 'Neograničeni internet', 'Flat', 'Unlimited', 'Flat rate', 'All you can use', 'Unlimited data']
REQUIRED_KEYS = {'scraped_date', 'provider', 'name', 'price', 'gb', 'minutes', 'sms', 'units', 'one_gb_price', 'sixty_min_price', 'thousand_units'}


class ValidationError(Exception):
    """Raised when a record or dataset fails validation."""
    pass


def validate_records(records):
    """
    Validate a list of data records.

    Each record must be a dictionary containing all required keys
    and valid values. If any record fails validation, a ValidationError
    is raised with details about the specific row and issue.

    Args:
        records (list): A list of dictionaries representing records
                        to validate.

    Returns:
        list: A list of validated records (same as input if all pass).

    Raises:
        ValidationError: If `records` is not a list, if any row is
                         not a dictionary, if required keys are missing,
                         or if any value fails validation.
    """

    # Check that the input is a list
    if not isinstance(records, list):
        raise ValidationError(f"Data is not a list. New dict: {records} Type: {type(records)}")


    validated = []      # Store valid rows here

    # Iterate over all rows with their index
    for idx, row in enumerate(records):
        try:
            # Ensure each row is a dictionary
            if not isinstance(row, dict):
                raise ValidationError(f"Row is not a dict: Row: {row}, Type: {type(row)}")
            else:
                # Validate the row and append to validated list
                validated.append(validate_row(row))
        except ValidationError as e:
            # Raise error with row index for easier debugging
            raise ValidationError(f"One row validation didn't pass. Index: {idx}, \n Row: {row}") from e

    # Check that at least one record is valid
    if not validated:
        raise ValidationError(f'No valid records. Validated: {validated}')


    return validated


def validate_row(row):
    """
   Validate all fields of a single record (dictionary).

   Checks for missing keys, provider validity, name, price, GB,
   and optional numeric fields (minutes, sms). Raises ValidationError
   if any check fails.
   """
    validate_missing_keys(row)                # Ensure all required keys are present
    validate_provider(row)                    # Check if provider is allowed
    validate_name(row)                        # Ensure name is a non-empty string
    validate_price(row)                       # Validate price format and range
    validate_gb(row)                          # Validate GB value (number or allowed strings)
    validate_optional_numbers(row['minutes'], 'minutes', row)  # Validate minutes if provided
    validate_optional_numbers(row['sms'], 'sms', row)          # Validate SMS if provided

    return row


def validate_missing_keys(row):
    """
    Check that the record contains all REQUIRED_KEYS.

    Raises ValidationError if any keys are missing.
    """
    missing = REQUIRED_KEYS - row.keys()      # Determine missing keys
    if missing:
        raise ValidationError(f"Invalid key. Missing keys: {missing}")


def validate_provider(row):
    """
    Validate the 'provider' field against ALLOWED_PROVIDERS.

    Raises ValidationError if the provider is not in the allowed list.
    """
    if row['provider'] not in ALLOWED_PROVIDERS:
        raise ValidationError(f"Invalid provider. Row: {row['provider']}")


def validate_name(row):
    """
    Ensure the 'name' field is a non-empty string.

    Raises ValidationError if empty or not a string.
    """
    name = row['name']
    if not isinstance(name, str) or not name.strip():
        raise ValidationError(f"Empty string. Row: {row['name']}")


def validate_price(row):
    """
    Validate the 'price' field.

    Checks that it is a string representing a number between 0 and 200.
    Raises ValidationError if invalid or out of range.
    """
    price = row['price']
    if not isinstance(price, str) or not price.strip():
        raise ValidationError(f"Invalid price. Row: {row['price']}")
    try:
        price = float(price)      # Convert to float
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Price is not number. Row: {row['price']}") from e

    if price < 0 or price > 200:     # Check range
        raise ValidationError(f"Invalid price. Row: {row['price']}")


def validate_gb(row):
    """
    Validate the 'gb' field.

    Accepts numeric string <= 500 or values in ALLOWED_GB.
    Empty string is allowed. Raises ValidationError if invalid.
    """
    gb_raw = row['gb']
    if gb_raw == '':       # Empty GB is allowed
        return

    if not isinstance(gb_raw, str) or not gb_raw.strip():
        raise ValidationError(f"Invalid GB. Row: {row['gb']}")

    if gb_raw.isdigit():         # Numeric GB
        if int(gb_raw) > 500:
            raise ValidationError(f"GB are too high. Row: {row['gb']}")
    elif gb_raw not in ALLOWED_GB:        # Allowed string GB values
        raise ValidationError(f"Invalid GB value. Row: {row['gb']}")


def validate_optional_numbers(value, field_name, row):
    """
    Validate optional numeric fields like 'minutes' or 'sms'.

    Empty string is allowed. Raises ValidationError if not an integer.
    """
    if value == '':        # Empty value is fine
        return

    try:
        int(value)         # Try to convert to integer
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid data. Value: {value}, Field name: {field_name}, Row: {row}.")








