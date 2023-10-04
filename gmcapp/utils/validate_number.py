import phonenumbers


def format_phone_number(phone_number, country_code):
    try:
        parsed_number = phonenumbers.parse(phone_number, country_code)
        if phonenumbers.is_possible_number(parsed_number) and phonenumbers.is_valid_number(parsed_number):
            number_type = phonenumbers.number_type(parsed_number)
            if number_type == phonenumbers.PhoneNumberType.MOBILE:
                formatted_number = phonenumbers.format_number(parsed_number,
                                                              phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                formatted_number = formatted_number.replace(" ", "")
                return formatted_number

            else:
                return ''  # Not a mobile number
        else:
            return ''  # Invalid or impossible number
    except phonenumbers.phonenumberutil.NumberParseException:
        return ''  # Number format exception
