import re



def validate_fields(required_fields, request) -> list:
    """
    Validates that all required fields are present in the request JSON data.

    Args:
        required_fields (list of str): A list of field names that are required to be present in the request JSON data.
        request (Request): The request object containing JSON data to be validated.

    Returns:
        list: A list of field names that are missing from the request JSON data. If all required fields are present,
              an empty list is returned.

    Example:
        required_fields = ['first_name', 'last_name', 'email_address']
        request_json = {'first_name': 'John', 'email_address': 'john@example.com'}
        missing_fields = validate_fields(required_fields, request)
        # missing_fields would be ['last_name']
    """
    return [field for field in required_fields if field not in request.json]


def valid_password(password: str) -> bool:
    """
    Validates a password to ensure it meets certain security criteria.

    Args:
        password (str): The password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.

    Password Criteria:
    - Length between 8 and 16 characters.
    - Contains at least one numerical character.
    - Contains at least one non-alphanumerical character (excluding whitespace).
    """
    # Check length
    if not (8 <= len(password) <= 16):
        return False

    # Check for at least one numerical character
    if not re.search(r"[0-9]", password):
        return False

    # Check for at least one non-alphanumerical character (excluding whitespace)
    if not re.search(r"[\W_]", password):
        return False

    return True


def valid_email(email: str) -> bool:
    """
    Validates an email address using regex to ensure it has the proper format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    if re.match(email_regex, email):
        return True
    return False
