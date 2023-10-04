import requests
from bs4 import BeautifulSoup
import html
from gmcapp.utils.extract_phone_numbers import extract_phone_numbers
from gmcapp.utils.validate_number import format_phone_number


def scrape_mobile_numbers_from_website(url, valid_country):
    try:

        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the webpage using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            button = [li.get_text() for li in soup.find_all('button')]
            list_items = [li.get_text() for li in soup.find_all('li')]
            divs = [div.get_text() for div in soup.find_all('div')]

            # Combine the text from different elements into a single variable
            all_text = '\n'.join(button + list_items + divs)
            # Remove HTML entities
            cleaned_text = html.unescape(all_text)

            final_text = cleaned_text.replace(".", "").replace("-", "").replace("(", "").replace(")", "").replace(",", " ")

            phone_numbers = extract_phone_numbers(valid_country, final_text)
            print(phone_numbers)

            # Remove duplicates by converting the list to a set and back to a list
            unique_phone_numbers = list(set(phone_numbers))
            print(unique_phone_numbers)
            formatted_number = ''
            for phone_number in unique_phone_numbers:
                print(phone_number)
                formatted_number = format_phone_number(phone_number, valid_country)
                if formatted_number != '':
                    print("Formatted Number:", formatted_number)
                    break  # Exit the loop after the first valid formatted number is found
            else:
                print("No valid phone number found.")
            return formatted_number  # Return the list of phone numbers and no error
        else:
            f"Request failed with status code {response.status_code}"

    except Exception as e:
        str(e)  # Return None and the error message if an exception occurs
