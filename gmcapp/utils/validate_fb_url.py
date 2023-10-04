import re


def is_facebook_url(url):
    # Define regular expressions to match common Facebook URL patterns
    facebook_patterns = [
        r'^https?://(www\.)?facebook\.com/.*$',  # Matches general Facebook URLs
        r'^https?://(www\.)?fb\.com/.*$',  # Matches shortened "fb.com" URLs
        r'^https?://(m\.)?facebook\.com/.*$',  # Matches mobile Facebook URLs (m.facebook.com)
        r'^https?://(web\.)?facebook\.com/.*$',  # Matches web Facebook URLs (web.facebook.com)
    ]

    # Check if the URL matches any of the Facebook patterns
    for pattern in facebook_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True

    return False
