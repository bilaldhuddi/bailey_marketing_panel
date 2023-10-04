import re


def extract_phone_numbers(country, final_text):
    if country == 'US':
        phone_numbers = re.findall(r'(?:(?:\+1\s?)?[2-9]\d{9})', final_text)
    elif country == 'GB':
        phone_numbers = re.findall(r'(?:\+44\s?)?07\d{9}|\(?07\d{3}\)?[-\s]?\d{6,7}', final_text)
    elif country == 'TR':
        phone_numbers = re.findall(r'(?:(?:\+90\s?)?0?\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})', final_text)
    elif country == 'TW':
        phone_numbers = re.findall(r'(?:(?:\+886\s?)?0?\d{9})', final_text)
    elif country == 'CH':
        phone_numbers = re.findall(r'(?:(?:\+41\s?)?0?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2}[-\s]?\d{2})', final_text)
    elif country == 'ES':
        phone_numbers = re.findall(r'(?:\+34\s?)?0?\d{2,3}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}', final_text)
    elif country == 'PT':
        phone_numbers = re.findall(r'(?:(?:\+351\s?)?9\d{8})', final_text)
    elif country == 'PL':
        phone_numbers = re.findall(r'(?:(?:\+48\s?)?0?\d{3}[-\s]?\d{3}[-\s]?\d{3})', final_text)
    elif country == 'PK':
        phone_numbers = re.findall(r'(?:(?:\+92\s?)?0?\d{3}[-\s]?\d{7})', final_text)
    elif country == 'NL':
        phone_numbers = re.findall(r'(?:(?:\+31\s?)?0?6[-\s]?\d{8})', final_text)
    elif country == 'MX':
        phone_numbers = re.findall(r'(?:(?:\+52\s?)?0?\d{2}[-\s]?\d{4}[-\s]?\d{4})', final_text)
    elif country == 'KR':
        phone_numbers = re.findall(r'(\+82|0)[1-9]\d{1,3}-\d{2,4}-\d{4}', final_text)
    elif country == 'JP':
        phone_numbers = re.findall(r'(?:\+81\s?)?0[789]0[-\s]?\d{4}[-\s]?\d{4}', final_text)
    elif country == 'IT':
        phone_numbers = re.findall(r'(?:(?:\+39\s?)?3\d{2}[-\s]?\d{3}[-\s]?\d{4})', final_text)
    elif country == 'IE':
        phone_numbers = re.findall(r'(?:(?:\+353\s?)?0?8[35679][-\s]?\d{3}[-\s]?\d{4})', final_text)
    elif country == 'IN':
        phone_numbers = re.findall(r'(?:(?:\+91\s?)?[6789]\d{4,14})', final_text)
    elif country == 'GR':
        phone_numbers = re.findall(r'(?:(?:\+30\s?)?[67]\d{8})', final_text)
    elif country == 'DE':
        phone_numbers = re.findall(r'(?:(?:\+49\s?)?0?[15789]\d{4,14})', final_text)
    elif country == 'FR':
        phone_numbers = re.findall(r'(?:(?:\+33\s?)?0?[67]\d{8})', final_text)
    elif country == 'DK':
        phone_numbers = re.findall(r'(?:(?:\+45\s?)?0?[689]\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2})', final_text)
    elif country == 'CO':
        phone_numbers = re.findall(r'(?:(?:\+57\s?)?3\d{9})', final_text)
    elif country == 'CL':
        phone_numbers = re.findall(r'(?:(?:\+56\s?)?9\d{8})', final_text)
    elif country == 'CA':
        phone_numbers = re.findall(r'(?:(?:\+1\s?)?[2-9]\d{9})', final_text)
    elif country == 'BR':
        phone_numbers = re.findall(r'(?:(?:\+55\s?)?0?[1-9]{2}\s?\d{4,5}-?\d{4})', final_text)
    elif country == 'BE':
        phone_numbers = re.findall(r'(?:(?:\+32\s?)?0?[1-9]\d{1,2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2})', final_text)
    elif country == 'AT':
        phone_numbers = re.findall(r'(?:(?:\+43\s?)?0?[1-9]\d{1,8})', final_text)
    elif country == 'AU':
        phone_numbers = re.findall(r'(?:(?:\+61\s?)?0?[1-9]\d{8})', final_text)
    elif country == 'AR':
        phone_numbers = re.findall(r'(?:(?:\+54\s?)?9[1-9]\d{7,10})', final_text)
    else:
        phone_numbers = []

    return phone_numbers
