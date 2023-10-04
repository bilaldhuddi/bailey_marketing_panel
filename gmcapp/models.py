from django.db import models


class OpenAIAPI(models.Model):
    openai_api_key = models.CharField(max_length=500)

    def __str__(self):
        return "OpenAI API Key"

    class Meta:
        db_table = 'openai_api_keys'


class SerpAPI(models.Model):
    serp_api_key = models.CharField(max_length=500)

    def __str__(self):
        return "Serp API Key"

    class Meta:
        db_table = 'serp_api_keys'


class MessageTemplate(models.Model):
    message_text = models.TextField()
    additional_info = models.TextField()

    def __str__(self):
        return "Message", "Additional Info"

    class Meta:
        db_table = 'message_templates'


class Country(models.Model):
    country_name = models.CharField(max_length=255, unique=True)
    google_url = models.URLField(default='www.google.com')  # Manually define the default value
    intl_country_code = models.CharField(max_length=2)
    country_code = models.CharField(max_length=3)
    valid_country = models.CharField(max_length=2)
    re = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.country_name} ({self.intl_country_code}) - {self.google_url}"


class City(models.Model):
    city_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.city_name


class PrimaryContact(models.Model):
    name = models.CharField(max_length=300)
    contact_type = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    phone_source = models.CharField(max_length=20, default='search')
    website = models.URLField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default="ready")
    message_status = models.CharField(max_length=20, default='Default')


class WebPageTemp(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    website_link = models.URLField(blank=True, null=True)
    page_link = models.URLField(blank=True, null=True)
    Sub_Heading = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'Title: {self.title}, Website Link: {self.website_link}, Sub Heading: {self.Sub_Heading}'


class FacebookPageTemp(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    page_link = models.URLField(blank=True, null=True)
    source = models.CharField(max_length=255, null=True)  # Set the default source to 'Facebook'

    def __str__(self):
        return f'Title: {self.title}, Page Link: {self.page_link}, Source: {self.source}'


class MessangerPrimary(models.Model):
    title = models.CharField(max_length=255)
    messenger_link = models.URLField(unique=True)
    source = models.CharField(max_length=20, default='search')
    message = models.TextField()
    message_status = models.CharField(max_length=20, default='Default')
    status = models.CharField(max_length=50, default="ready")

    def __str__(self):
        return self.title
