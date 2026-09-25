"""
phone_cleanup_tool.py
 
Normalizes phone numbers into one consistent format, regardless of how
messily they were originally written (with/without country code, spaces,
dashes, brackets, etc).
 
Same as filters.py and fuzzy_dedup_tool.py - plain function, not an @tool.
Normalizing a phone number has one correct answer, nothing for the agent
to reason about.
"""

import phonenumbers

def clean_phone_number(raw_number: str, default_region: str = "PK") -> str | None:
    """
    Takes a messy phone number string and returns it in one clean,
    consistent format (e.g. +923001234567), or None if it's not a
    real, valid number.
 
    default_region: which country to assume if the number doesn't already
    include a country code (e.g. "0300-1234567" with no + sign). Set to
    "PK" since your leads are local Pakistani businesses - change this if
    you ever target a different country.
    """
    if not raw_number:
        return None
 
    try:
        parsed = phonenumbers.parse(raw_number, default_region)
 
        if not phonenumbers.is_valid_number(parsed):
            return None
 
        # E164 is the international standard format: +<countrycode><number>,
        # no spaces, no dashes, no brackets - the cleanest possible form
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
 
    except phonenumbers.NumberParseException:
        # raw_number was too broken/garbled to even attempt parsing
        return None


# Quick manual test
if __name__ == "__main__":
    test_numbers = [
        "+92 327 7088881",   # already has country code, just messy spacing
        "0300-1234567",       # local format, no country code
        "(0300) 1234567",     # local format with brackets
        "not a phone number", # garbage input
    ]
 
    for number in test_numbers:
        cleaned = clean_phone_number(number)
        print(f"{number!r:25} -> {cleaned}")