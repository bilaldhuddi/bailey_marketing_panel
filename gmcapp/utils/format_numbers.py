import re
from gmcapp.models import Country


def add_country_code(country, phone_number):
    # Query the Country model to get the country code for the specified country
    try:
        country_obj = Country.objects.get(country_name=country)
        country_code = country_obj.country_code
    except Country.DoesNotExist:
        country_code = ''

    cleaned_number = re.sub(r'\D', '', phone_number)

    # Check if the phone number already contains the country code
    if cleaned_number.startswith(country_code):
        updated_number = cleaned_number
    else:
        updated_number = country_code + cleaned_number

    return updated_number
