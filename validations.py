# check fields provided in request are valid
def validate_fields(required_fields, request):
    return [field for field in required_fields if field not in request.json]

# check password is valid
def valid_password(password):
    return 8 <= len(password) <= 16

import re

def valid_email(email: str) -> bool:
    """
    Validates an email address using regex to ensure it has the proper format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    # Regular expression for validating an email
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    # Match the email with the regex
    if re.match(email_regex, email):
        return True
    return False
