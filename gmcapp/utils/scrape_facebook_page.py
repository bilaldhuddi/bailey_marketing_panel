import requests
from bs4 import BeautifulSoup
import re
from gmcapp.utils.validate_fb_url import is_facebook_url


def facebook_page_url_from_website(url):
    try:
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the webpage using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links on the page
            links = soup.find_all('a', href=True)
            print(links)
            # Search for the Facebook page link in the list of links
            facebook_page_url = None
            for link in links:
                if re.search(r'facebook\.com/([^/?]+)', link['href']):
                    print('re.search', link)
                    if is_facebook_url(link['href']):
                        facebook_page_url = link['href']
                        print('facebook_page_url:' ,facebook_page_url)
                    break  # Exit the loop after finding the Facebook page URL

            if facebook_page_url:
                print('Facebook URL', facebook_page_url)
                return facebook_page_url
            else:
                return "Facebook page link not found on the website."

        else:
            return f"Request failed with status code {response.status_code}"

    except Exception as e:
        return str(e)  # Return the error message if an exception occurs
