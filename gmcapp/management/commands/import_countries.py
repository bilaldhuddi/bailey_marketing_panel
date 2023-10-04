from django.core.management.base import BaseCommand
from gmcapp.models import Country  # Import your Country model


class Command(BaseCommand):
    help = 'Import countries data into the database'

    def handle(self, *args, **kwargs):
        # Data to be imported
        data = [
            {
                'google_url': 'http://www.google.com',
                'country_served': 'United States',
                'intl_country_code': 'us',
            },
            {
                'google_url': 'http://www.google.co.jp',
                'country_served': 'Japan',
                'intl_country_code': 'jp',
            },
            {
                'google_url': 'http://www.google.co.uk',
                'country_served': 'United Kingdom',
                'intl_country_code': 'uk',
            },
            {
                'google_url': 'http://www.google.es',
                'country_served': 'Spain',
                'intl_country_code': 'es',
            },
            {
                'google_url': 'http://www.google.ca',
                'country_served': 'Canada',
                'intl_country_code': 'ca',
            },
            {
                'google_url': 'http://www.google.de',
                'country_served': 'Germany',
                'intl_country_code': 'de',
            },
            {
                'google_url': 'http://www.google.it',
                'country_served': 'Italy',
                'intl_country_code': 'it',
            },
            {
                'google_url': 'http://www.google.fr',
                'country_served': 'France',
                'intl_country_code': 'fr',
            },
            {
                'google_url': 'http://www.google.com.au',
                'country_served': 'Australia',
                'intl_country_code': 'au',
            },
            {
                'google_url': 'http://www.google.com.tw',
                'country_served': 'Taiwan',
                'intl_country_code': 'tw',
            },
            {
                'google_url': 'http://www.google.nl',
                'country_served': 'Netherlands',
                'intl_country_code': 'nl',
            },
            {
                'google_url': 'http://www.google.com.br',
                'country_served': 'Brazil',
                'intl_country_code': 'br',
            },
            {
                'google_url': 'http://www.google.com.tr',
                'country_served': 'Turkey',
                'intl_country_code': 'tr',
            },
            {
                'google_url': 'http://www.google.be',
                'country_served': 'Belgium',
                'intl_country_code': 'be',
            },
            {
                'google_url': 'http://www.google.com.gr',
                'country_served': 'Greece',
                'intl_country_code': 'gr',
            },
            {
                'google_url': 'http://www.google.co.in',
                'country_served': 'India',
                'intl_country_code': 'in',
            },
            {
                'google_url': 'http://www.google.com.mx',
                'country_served': 'Mexico',
                'intl_country_code': 'mx',
            },
            {
                'google_url': 'http://www.google.dk',
                'country_served': 'Denmark',
                'intl_country_code': 'dk',
            },
            {
                'google_url': 'http://www.google.com.ar',
                'country_served': 'Argentina',
                'intl_country_code': 'ar',
            },
            {
                'google_url': 'http://www.google.ch',
                'country_served': 'Switzerland',
                'intl_country_code': 'ch',
            },
            {
                'google_url': 'http://www.google.cl',
                'country_served': 'Chile',
                'intl_country_code': 'cl',
            },
            {
                'google_url': 'http://www.google.at',
                'country_served': 'Austria',
                'intl_country_code': 'at',
            },
            {
                'google_url': 'http://www.google.co.kr',
                'country_served': 'Korea',
                'intl_country_code': 'kr',
            },
            {
                'google_url': 'http://www.google.ie',
                'country_served': 'Ireland',
                'intl_country_code': 'ie',
            },
            {
                'google_url': 'http://www.google.com.co',
                'country_served': 'Colombia',
                'intl_country_code': 'co',
            },
            {
                'google_url': 'http://www.google.pl',
                'country_served': 'Poland',
                'intl_country_code': 'pl',
            },
            {
                'google_url': 'http://www.google.pt',
                'country_served': 'Portugal',
                'intl_country_code': 'pt',
            },
            {
                'google_url': 'http://www.google.com.pk',
                'country_served': 'Pakistan',
                'intl_country_code': 'pk',
            },
        ]

        for entry in data:
            country_name = entry['country_served']
            google_url = entry['google_url']
            intl_country_code = entry['intl_country_code']

            # Check if the country already exists
            existing_country = Country.objects.filter(country_name=country_name).first()

            if existing_country:
                # If the country exists, update its fields
                existing_country.google_url = google_url
                existing_country.intl_country_code = intl_country_code
                existing_country.save()
            else:
                # If the country doesn't exist, create a new one
                Country.objects.create(
                    country_name=country_name,
                    google_url=google_url,
                    intl_country_code=intl_country_code
                )

        self.stdout.write(self.style.SUCCESS('Countries data imported successfully.'))
