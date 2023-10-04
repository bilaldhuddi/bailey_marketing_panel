import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from gmcapp.utils.default_message import get_default_message
from gmcapp.utils.create_messenger_contact import create_messenger_contact
from .forms import OpenAIAPIForm, SerpAPIForm, MessageTemplateForm
from serpapi import GoogleSearch
import re
from gmcapp.utils.generate_excel_file import generate_excel_file
from gmcapp.utils.message_generation import generate_unique_message
from .models import OpenAIAPI, SerpAPI, Country, City, PrimaryContact, WebPageTemp, FacebookPageTemp, MessangerPrimary, \
    MessageTemplate
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from gmcapp.utils.scrape_facebook_page import facebook_page_url_from_website
from gmcapp.utils.scrape_mobile_numbers import scrape_mobile_numbers_from_website
from gmcapp.utils.validate_fb_url import is_facebook_url
from gmcapp.utils.validate_number import format_phone_number


def get_all_objects():
    openai_api, _ = OpenAIAPI.objects.get_or_create(pk=1)
    serp_api, _ = SerpAPI.objects.get_or_create(pk=1)
    message_template, _ = MessageTemplate.objects.get_or_create(pk=1)
    countries = Country.objects.all()
    cities = City.objects.all()
    primary_contacts = PrimaryContact.objects.all()
    web_page_temp = WebPageTemp.objects.all()
    facebook_page_temp = FacebookPageTemp.objects.all()

    return {
        'openai_api': openai_api,
        'serp_api': serp_api,
        'message_template': message_template,
        'countries': countries,
        'cities': cities,
        'primary_contacts': primary_contacts,
        'web_page_temp': web_page_temp,
        'facebook_page_temp': facebook_page_temp,

    }


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def get(self, request):
        # Count contacts for each status

        messanger_contacts = MessangerPrimary.objects.all()
        whatsapp_contacts = PrimaryContact.objects.all()

        contact_counts = PrimaryContact.objects.values('status').annotate(count=Count('status'))

        messenger_counts = MessangerPrimary.objects.values('status').annotate(count=Count('status'))

        # Prepare data for the pie chart
        labels = [entry['status'] for entry in contact_counts]
        data = [entry['count'] for entry in contact_counts]

        messenger_labels = [entry['status'] for entry in messenger_counts]
        messenger_data = [entry['count'] for entry in messenger_counts]

        context = {
            'labels': labels,
            'data': data,
            'messenger_labels': messenger_labels,
            'messenger_data': messenger_data,
            'messanger_contacts': messanger_contacts,
            'whatsapp_contacts': whatsapp_contacts
        }

        return render(request, self.template_name, context)


class SettingsView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def __init__(self):
        super(SettingsView, self).__init__()
        self.all_objects = get_all_objects()  # Assuming you have a function to get all objects

    def get(self, request):
        openai_form = OpenAIAPIForm(instance=self.all_objects['openai_api'])
        serp_form = SerpAPIForm(instance=self.all_objects['serp_api'])
        message_form = MessageTemplateForm(instance=self.all_objects['message_template'])

        success_message = None
        error_message = None

        context = {
            'openai_form': openai_form,
            'serp_form': serp_form,
            'message_form': message_form,
            'countries': self.all_objects['countries'],
            'cities': self.all_objects['cities'],
            'success_message': success_message,
            'error_message': error_message,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        openai_form = OpenAIAPIForm(request.POST, instance=self.all_objects['openai_api'])
        serp_form = SerpAPIForm(request.POST, instance=self.all_objects['serp_api'])
        message_form = MessageTemplateForm(request.POST, instance=self.all_objects['message_template'])
        context = {}
        success_message = None
        error_message = None

        try:
            if openai_form.is_valid():
                openai_form.save()
                success_message = "OpenAI settings saved successfully."
            else:
                error_message = "Error saving OpenAI settings. Please check the form."

            if serp_form.is_valid():
                serp_form.save()
                response_data = {'success': True, 'message': 'Success message here'}
            else:
                response_data = {'success': False, 'errors': 'error'}

            if message_form.is_valid():
                message_form.save()
                success_message = "Message template saved successfully."
            else:
                error_message = "Error saving message template. Please check the form."

            cities_data = request.POST.get('cities_data', '')

            if cities_data:
                city_lines = cities_data.split('\n')
                for city_name in city_lines:
                    city_name = city_name.strip()
                    if city_name:
                        _, created = City.objects.get_or_create(city_name=city_name)
                        if created:
                            success_message = f"City '{city_name}' added successfully."
                        else:
                            error_message = f"City '{city_name}' already exists in the database."

        except Exception as e:
            error_message = str(e)  # Handle any exceptions and set error_message

        response_data = {
            'success': True,  # Set to True if the operation was successful
            'message': 'Success message here',  # Customize this message
        }

        return redirect('settings')


class AutoResearchView(LoginRequiredMixin, View):
    template_name = 'auto_research.html'

    def __init__(self):
        super(AutoResearchView, self).__init__()
        self.all_objects = get_all_objects()

    def get(self, request):
        # Initialize the context variable
        results = []
        total_results = ''

        context = {
            'countries': self.all_objects['countries'],
            'cities': self.all_objects['cities'],
            'primary_contacts': self.all_objects['primary_contacts'],
            'results': results,
            'total_results': total_results

        }

        return render(request, self.template_name, context)

    def post(self, request):
        # Your existing post method logic for AutoResearchView
        query = request.POST.get('query', '')
        selected_country_name = request.POST.get('country', '')
        city = request.POST.get('city', '')
        num_results_str = (request.POST.get('num_results', ''))
        number_of_results = int(num_results_str) if num_results_str else 20
        print('num_results_str:', num_results_str)
        print('number_of_results:', number_of_results)

        context = {}

        # Fetch the SERP API key from the database
        serp_api_key = SerpAPI.objects.first()

        selected_country = get_object_or_404(Country, country_name=selected_country_name)
        google_url = selected_country.google_url
        intl_country_code = selected_country.intl_country_code

        # Check if an API key is available
        if serp_api_key:
            api_key = serp_api_key.serp_api_key
        else:
            api_key = ""  # Provide a default API key if none is available

        # Calculate the number of iterations based on the selected value
        num_iterations = (number_of_results + 19) // 20  # Round up to the nearest multiple of 20
        contacts_to_append = []
        total_results = ''
        # Loop based on the number of iterations
        for _ in range(num_iterations):
            params = {
                "engine": "google",
                "q": query + ' ' + 'in' + ' ' + city,
                "location": selected_country_name,
                "google_domain": google_url,
                "gl": intl_country_code,
                "hl": "en",
                "tbm": "lcl",
                "num": "20",  # Fetch 20 results at a time
                "start": str(_ * 20),  # Calculate the offset based on the iteration
                "api_key": api_key,
            }

            try:
                # Make the API request and get results
                search = GoogleSearch(params)
                results = search.get_dict()
                results = results

                # Process the results and update your models as needed
                if results.get('local_results'):
                    # Create a list to store contacts to append

                    valid_country_code = selected_country.valid_country

                    for result in results['local_results']:
                        # Remove spaces and dashes from the phone number
                        phone = result.get('phone', '')
                        phone_number = format_phone_number(phone, valid_country_code)
                        if phone_number is None:
                            phone_number = ''
                        title = result.get('title', '')
                        website = result.get('links', {}).get('website', '')
                        address = result.get('address', '')

                        map_title = title.split()
                        final_title = map_title[:2]

                        # Join the remaining words back together
                        result_name = ' '.join(final_title)

                        message = get_default_message(result_name)

                        existing_contact = PrimaryContact.objects.filter(address=address).first()
                        if not existing_contact:
                            # Create a new PrimaryContact record
                            contact = PrimaryContact(
                                name=result_name,
                                contact_type=result.get('type', ''),
                                address=address,
                                phone=phone_number,
                                phone_source='search',
                                website=website,
                                status='ready',
                                message=message,
                                message_status='Default'
                            )
                            # Append the contact to the list but do not save it yet
                            contacts_to_append.append(contact)

                    # After the loop, bulk insert all the new contacts at once
                    PrimaryContact.objects.bulk_create(contacts_to_append)

                    # num_results_in_iteration = len(results.get('local_results', []))

                    # Add the number of results in this iteration to total_results
                    total_results = len(contacts_to_append)

                    print('Total Results Fetched:', total_results)

            except Exception as e:
                context['error'] = str(e)

            try:
                contacts_to_update = PrimaryContact.objects.filter(website__icontains='http://')

                for contact in contacts_to_update:
                    contact.website = contact.website.replace('http://', 'https://')
                    contact.save()
                print('saved')

                contacts_to_scrape = PrimaryContact.objects.filter(phone='').exclude(website='')

                for contact in contacts_to_scrape:
                    title = contact.name
                    default_message = contact.message
                    message_status = contact.message_status
                    website_url = contact.website
                    valid_country = selected_country.valid_country

                    try:
                        if is_facebook_url(website_url):
                            create_contact = create_messenger_contact(title, website_url, default_message,
                                                                      message_status,
                                                                      source='WhatAppList')
                            if create_contact == 'success':
                                PrimaryContact.objects.filter(website=website_url).delete()

                        else:
                            valid_number = scrape_mobile_numbers_from_website(website_url, valid_country)
                            print(valid_number)
                            contact.phone = valid_number
                            contact.phone_source = 'website'
                            contact.save()

                    except Exception as e:
                        context['error'] = str(e)

                contacts_to_add_in_messanger = PrimaryContact.objects.filter(phone__exact='')
                for contact in contacts_to_add_in_messanger:
                    title = contact.name
                    message = contact.message
                    website_url = contact.website
                    message_status = contact.message_status
                    print('contacts_to_add_in_messanger>', title)

                    try:
                        facebook_page_url = facebook_page_url_from_website(website_url)
                        print('fburl>', facebook_page_url)

                        if facebook_page_url:
                            create_contact = create_messenger_contact(title, facebook_page_url, message, message_status,
                                                                      source='website')
                            if create_contact == 'success':
                                PrimaryContact.objects.filter(website=website_url).delete()

                    except Exception as e:
                        context['error'] = str(e)

                contacts_to_delete = PrimaryContact.objects.filter(phone__exact='')
                contacts_to_delete.delete()
                contacts_to_delete = PrimaryContact.objects.filter(website__icontains='instagram.com')
                contacts_to_delete.delete()

                primary_contacts = PrimaryContact.objects.filter(message_status='Default')

                for contact in primary_contacts:
                    # Generate a unique message for each contact using the imported function
                    username = contact.name
                    generated_message = generate_unique_message(username)

                    # Update the contact's message field with the generated message
                    contact.message = generated_message

                    # Set the contact's message_status to 'Generated'
                    contact.message_status = 'Generated'

                    # Save the updated contact
                    contact.save()

                context['success'] = True
                context['message'] = 'Messages generated and saved successfully'

            except Exception as e:
                # Handle API request errors
                context['error'] = str(e)
                print(f"An error occurred: {e}")

            context['countries'] = self.all_objects['countries']
            context['cities'] = self.all_objects['cities']
            context['primary_contacts'] = self.all_objects.get('primary_contacts')
            context['results'] = results
            context['total_results'] = total_results

        return render(request, self.template_name, context)


class WebScrapingView(LoginRequiredMixin, View):
    template_name = 'web_scraping.html'

    def __init__(self):
        super(WebScrapingView, self).__init__()
        self.all_objects = get_all_objects()

    def get_context(self, request):
        return {
            'countries': self.all_objects['countries'],
            'cities': self.all_objects['cities'],
            'fb_data_temp': self.all_objects['facebook_page_temp'],
            'web_data_temp': self.all_objects['web_page_temp'],
        }

    def get(self, request):
        context = self.get_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        webdata = False
        fbdata = False

        context = self.get_context(request)

        # Your existing post method logic for handling web scraping
        query = request.POST.get('query', '')
        selected_country_name = request.POST.get('country', '')
        city = request.POST.get('city', '')
        search_type = request.POST.get('search_type', '')

        # Fetch the SERP API key from the database
        serp_api_key = SerpAPI.objects.first()

        selected_country = get_object_or_404(Country, country_name=selected_country_name)
        google_url = selected_country.google_url
        intl_country_code = selected_country.intl_country_code

        q = query + ' in ' + city

        # Check if the search type is 'facebook pages'
        if search_type == 'facebook':
            q += ' facebook'

            with transaction.atomic():
                # Delete all records in the FacebookPageTemp model
                FacebookPageTemp.objects.all().delete()

        if serp_api_key:
            api_key = serp_api_key.serp_api_key
        else:
            api_key = ""
        if search_type == 'web':
            with transaction.atomic():
                WebPageTemp.objects.all().delete()

        # Loop based on the number of iterations (five times)
        for _ in range(5):
            params = {
                "engine": "google",
                "q": q,
                "location": selected_country_name,
                "google_domain": google_url,
                "gl": intl_country_code,
                "hl": "en",
                "num": "10",
                "start": str(_ * 10),
                "api_key": api_key,
            }

            try:
                # Make the API request and get results
                search = GoogleSearch(params)
                results = search.get_dict()

                if search_type == 'web' and results.get('organic_results'):
                    # Iterate over the results and save them to WebPageTemp
                    for result in results['organic_results']:
                        webpage = WebPageTemp(
                            title=result.get('title', ''),
                            website_link=result.get('source', ''),
                            page_link=result.get('link', ''),
                        )
                        webpage.save()
                        webdata = True

                elif search_type == 'facebook' and results.get('organic_results'):

                    for result in results['organic_results']:
                        title = result.get('title', '')
                        map_title = title.split()
                        print('map_title:', map_title)
                        final_title = map_title[:2]
                        print('final_title:', final_title)
                        # Join the remaining words back together
                        result_title = ' '.join(final_title)

                        print('result_name:', result_title)

                        facebook_page = FacebookPageTemp(
                            title=result_title,
                            page_link=result.get('link', ''),
                            source=result.get('source', '')
                        )
                        facebook_page.save()
                        fbdata = True

                context['results'] = results
            except Exception as e:
                # Handle API request errors and return an error message
                context['error'] = str(e)

        context = {
            'webdata': webdata,
            'fbdata': fbdata,
            'countries': self.all_objects['countries'],
            'cities': self.all_objects['cities'],
            'fb_data_temp': self.all_objects['facebook_page_temp'],
            'web_data_temp': self.all_objects['web_page_temp'],
        }

        return render(request, self.template_name, context)


class EditRecordView(LoginRequiredMixin, View):

    def post(self, request):
        record_id = request.POST.get('id')
        table_id = request.POST.get('table_id', '')
        title = request.POST.get('title')
        website_link = request.POST.get('website_link')
        city_name = request.POST.get('city_name')

        try:

            if table_id == 'web-data-table':
                obj = WebPageTemp
                record = get_object_or_404(WebPageTemp, id=record_id)

                record.title = title
                record.website_link = website_link

                record.save()
            elif table_id == 'facebook-data-table':
                obj = FacebookPageTemp
                record = get_object_or_404(FacebookPageTemp, id=record_id)

                record.name = title
                record.page_link = website_link

                record.save()

            elif table_id == 'whatsapp-data-table':
                obj = PrimaryContact
                record = get_object_or_404(PrimaryContact, id=record_id)

                record.name = title
                record.website = website_link

                record.save()

            elif table_id == 'messanger-data-table':
                obj = PrimaryContact
                record = get_object_or_404(MessangerPrimary, id=record_id)

                record.title = title
                record.messenger_link = website_link

                record.save()

            elif table_id == 'cities-table':
                obj = City
                record = get_object_or_404(City, id=record_id)

                record.city_name = city_name

                record.save()

            # Return a success JSON response
            return JsonResponse({'success': True})
        except obj.DoesNotExist:
            # Return a failure JSON response if the record does not exist
            return JsonResponse({'success': False})


class DeleteRecordView(LoginRequiredMixin, View):

    def post(self, request):
        table_id = request.POST.get('table_id', '')
        record_id = request.POST.get('id', '')
        print(table_id)

        try:
            if table_id == 'web-data-table':
                record = get_object_or_404(WebPageTemp, id=record_id)
                record.delete()
                return JsonResponse({'success': True})

            elif table_id == 'facebook-data-table':
                record = get_object_or_404(FacebookPageTemp, id=record_id)
                record.delete()
                return JsonResponse({'success': True})

            elif table_id == 'whatsapp-data-table':
                record = get_object_or_404(PrimaryContact, id=record_id)
                record.delete()
                return JsonResponse({'success': True})

            elif table_id == 'messanger-data-table':
                record = get_object_or_404(MessangerPrimary, id=record_id)
                record.delete()
                return JsonResponse({'success': True})

            elif table_id == 'cities-table':
                record = get_object_or_404(City, id=record_id)
                record.delete()
                return JsonResponse({'success': True})

            else:
                return JsonResponse({'success': False, 'error_message': 'Invalid table_id'})

        except Exception as e:
            # Handle exceptions and return a JSON response indicating failure
            return JsonResponse({'success': False, 'error_message': str(e)})


class ExportSelectedRecordsView(LoginRequiredMixin, View):

    def post(self, request):
        table_id = request.POST.get('table_id', '')
        selected_ids = request.POST.getlist('selected_ids[]')

        try:
            print(selected_ids)
            print(table_id)
            if table_id == 'web-data-table':
                selected_records = WebPageTemp.objects.filter(id__in=selected_ids)

            elif table_id == 'facebook-data-table':
                selected_records = FacebookPageTemp.objects.filter(id__in=selected_ids)

            elif table_id == 'whatsapp-data-table':
                selected_records = PrimaryContact.objects.filter(id__in=selected_ids)

            elif table_id == 'messanger-data-table':
                selected_records = MessangerPrimary.objects.filter(id__in=selected_ids)

            response = generate_excel_file(table_id, selected_records, table_id)

            return response

        except Exception as e:
            # Handle exceptions and return a JSON response indicating failure
            return JsonResponse({'success': False, 'error_message': str(e)})


class CreateMessengerContactView(LoginRequiredMixin, View):

    def post(self, request):

        response_data = {}

        try:
            facebook_pages = FacebookPageTemp.objects.all()  # Replace with your actual query

            # Iterate through each Facebook page and extract usernames
            for page in facebook_pages:
                title = page.title
                page_link = page.page_link
                message_status = 'Default'

                default_message = get_default_message(title)

                created = create_messenger_contact(title, page_link, default_message, message_status, source='Search')
                print(created)

            messenger_contacts = MessangerPrimary.objects.filter(message_status='Default')

            for contact in messenger_contacts:
                # Generate a unique message for each contact using the imported function
                username = contact.title

                generated_message = generate_unique_message(username)

                # Update the contact's message field with the generated message
                contact.message = generated_message

                contact.source = 'search'

                contact.message_status = 'Generated'

                # Save the updated contact
                contact.save()

            response_data['success'] = True
            response_data['message'] = 'Messages generated and saved successfully'
        except Exception as e:
            # Handle any exceptions that may occur during contact creation
            response_data['success'] = False
            response_data['error_message'] = str(e)

        return JsonResponse(response_data)

    def get(self, request):
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


class MessagingAutomationView(LoginRequiredMixin, View):
    template_name = 'send_messages.html'

    def get_context_data(self, **kwargs):
        # Retrieve the count of total contacts, messages delivered, and failed
        total_contacts = MessangerPrimary.objects.count()
        messages_delivered = MessangerPrimary.objects.filter(status='delivered').count()
        failed = MessangerPrimary.objects.filter(status='failed').count()

        return {
            'total_contacts': total_contacts,
            'messages_delivered': messages_delivered,
            'failed': failed,
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


class StartWhatsAppAutomation(LoginRequiredMixin, View):

    def post(self, request):
        image = request.FILES.get("image")
        # now = datetime.datetime.now()
        # hour = now.hour
        # minute = now.minute + 2  # Send messages 2 minutes from now
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # Get all contacts with a status of "ready"
        contacts = PrimaryContact.objects.filter(status="ready")

        # Initialize counters
        total_contacts = contacts.count()
        messages_delivered = 0
        failed = 0

        link = 'https://web.whatsapp.com'
        driver.get(link)
        time.sleep(59)

        # Check if an image is provided in the request
        if image:
            # Generate a dynamic image path based on the image's name or some unique identifier
            image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', 'image.png')

            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
        else:
            image_path = None

        for contact in contacts:
            mobile_no = contact.phone
            message = contact.message
            link = f'https://web.whatsapp.com/send/?phone={mobile_no}'

            driver.get(link)
            time.sleep(25)

            # Check if an image is provided in the request
            if image_path:
                message = contact.message
                image_path = image_path

                try:

                    attach_btn = driver.find_element(By.CSS_SELECTOR, '._1OT67')
                    attach_btn.click()
                    time.sleep(1)
                    # Find and send image path to input
                    msg_input = driver.find_elements(By.CSS_SELECTOR, '._2UNQo input')[1]
                    msg_input.send_keys(image_path)
                    time.sleep(1)
                    # Start the action chain to write th
                    actions = ActionChains(driver)
                    for line in message.split('\n'):
                        actions.send_keys(line)
                        # SHIFT + ENTER to create next line
                        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                    time.sleep(3)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()
                    time.sleep(5)

                    # If successful, update the contact status to "delivered"

                    contact.status = "delivered"
                    contact.save()

                    # Increment the messages delivered counter
                    messages_delivered += 1

                except Exception as e:
                    # If the image sending fails, update the contact status to "Fields Processed"
                    contact.status = "failed"
                    contact.save()
                    print(f'Error sending image: {str(e)}')
                    # Increment the fields processed counter
                    failed += 1
            else:
                try:
                    input_box = driver.find_element(By.CSS_SELECTOR, '._3Uu1_')
                    time.sleep(1)

                    if input_box:
                        actions = ActionChains(driver)
                        for line in message.split('\n'):
                            actions.send_keys(line)
                            # SHIFT + ENTER to create next line
                            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                        actions.send_keys(Keys.ENTER)
                        actions.perform()
                        time.sleep(3)
                        contact.status = "delivered"
                        contact.save()

                        # Increment the messages delivered counter
                        messages_delivered += 1
                    else:
                        failed += 1


                except Exception as e:
                    # If the message sending fails, update the contact status to "Fields Processed"
                    contact.status = "failed"
                    contact.save()

                    # Increment the fields processed counter
                    failed += 1

        driver.quit()

        add_to_messanger = PrimaryContact.objects.filter(status='failed')

        for contact in add_to_messanger:
            title = contact.name
            message = contact.message
            website_url = contact.website
            message_status = contact.message_status
            print('contacts_to_add_in_messanger>', title)

            try:
                facebook_page_url = facebook_page_url_from_website(website_url)
                print('fburl>', facebook_page_url)

                if facebook_page_url:
                    create_contact = create_messenger_contact(title, facebook_page_url, message, message_status,
                                                              source='website')
                    if create_contact == 'success':
                        PrimaryContact.objects.filter(website=website_url).delete()

            except Exception as e:
                error = str(e)

        # Return a JSON response with the results
        response_data = {
            "success": True,
            "total_contacts": total_contacts,
            "messages_delivered": messages_delivered,
            "failed": failed,
            "error": error,
        }
        return JsonResponse(response_data)


class StartMessangerAutomation(LoginRequiredMixin, View):

    def post(self, request):
        image = request.FILES.get("image")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        contacts = MessangerPrimary.objects.filter(status="ready")

        # Initialize counters
        total_contacts = contacts.count()
        messages_delivered = 0
        failed = 0

        this_recipient = ''
        last_recipient = ''
        link = 'https://www.messenger.com/'
        driver.get(link)
        time.sleep(45)

        # Check if an image is provided in the request
        if image:
            # Generate a dynamic image path based on the image's name or some unique identifier
            image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', 'image.png')

            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
        else:
            image_path = None

        for contact in contacts:
            user = contact.messenger_link
            message = contact.message

            driver.get(user)
            time.sleep(15)

            # Check if an image is provided in the request
            if image_path:
                message = contact.message
                image_path = image_path

                try:
                    get_recipient = driver.current_url
                    match = re.search(r"https://www\.messenger\.com/t/\d+", get_recipient)

                    if match:
                        this_recipient = match.group(0)

                    if this_recipient != last_recipient:
                        print("this_recipient:", this_recipient)

                        file_input = driver.find_element(By.XPATH, "//input[@type='file']")

                        # msg_input = driver.find_elements(By.CSS_SELECTOR, '.div[aria-label="Attach a file"] input')[1]
                        file_input.send_keys(image_path)
                        time.sleep(2)
                        # Start the action chain to write th
                        actions = ActionChains(driver)
                        for line in message.split('\n'):
                            actions.send_keys(line)
                            # SHIFT + ENTER to create next line
                            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                        actions.send_keys(Keys.ENTER)
                        actions.perform()
                        time.sleep(5)
                        get_last_recipient = driver.current_url
                        match = re.search(r"https://www\.messenger\.com/t/\d+", get_last_recipient)

                        if match:
                            last_recipient = match.group(0)
                        print("last_recipient:", last_recipient)

                        contact.status = "delivered"
                        contact.save()
                        messages_delivered += 1

                    else:
                        contact.status = "failed"
                        contact.save()
                        failed += 1
                        print('Invalid User')

                except Exception as e:
                    # If the image sending fails, update the contact status to "Fields Processed"
                    contact.status = "failed"
                    contact.save()
                    print(f'Error sending image: {str(e)}')
                    # Increment the fields processed counter
                    failed += 1
            else:
                try:
                    get_recipient = driver.current_url
                    match = re.search(r"https://www\.messenger\.com/t/\d+", get_recipient)

                    if match:
                        this_recipient = match.group(0)

                    if this_recipient != last_recipient:
                        print("this_recipient:", this_recipient)

                        message_box = driver.find_element(By.XPATH, "//div[@aria-label='Message']")

                        # message_box.send_keys(message)
                        time.sleep(1)
                        # message_box.send_keys(Keys.RETURN)
                        if message_box:
                            actions = ActionChains(driver)
                            for line in message.split('\n'):
                                actions.send_keys(line)
                                # SHIFT + ENTER to create next line
                                actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                            actions.send_keys(Keys.ENTER)
                            actions.perform()
                            time.sleep(5)

                            get_last_recipient = driver.current_url
                            match = re.search(r"https://www\.messenger\.com/t/\d+", get_last_recipient)

                            if match:
                                last_recipient = match.group(0)
                                print("last_recipient:", last_recipient)

                                contact.status = "delivered"
                                contact.save()

                                messages_delivered += 1

                        else:
                            failed += 1

                    else:
                        contact.status = "failed"
                        contact.save()
                        failed += 1
                        print('Invalid User')


                except Exception as e:
                    # If the message sending fails, update the contact status to "Fields Processed"
                    contact.status = "failed"
                    contact.save()

                    failed += 1

        driver.quit()

        response_data = {
            "success": True,
            "total_contacts": total_contacts,
            "messages_delivered": messages_delivered,
            "failed": failed,
        }
        return JsonResponse(response_data)


class CityListView(LoginRequiredMixin, View):
    template_name = 'edit_cities.html'

    def get(self, request):
        cities = City.objects.all()
        return render(request, self.template_name, {'cities': cities})


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')

        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        # Check if the user is already authenticated, redirect to a dashboard or home page if needed
        if request.user.is_authenticated:
            return redirect('dashboard')  # Change 'dashboard' to your desired URL

        # Create an instance of the AuthenticationForm and populate it with POST data
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # Get the username and password from the form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(request, user)
                return redirect('dashboard')  # Change 'dashboard' to your desired URL after login

        # If the form is invalid or login failed, set an error message
        error_message = 'Invalid username or password. Please try again.'

        return render(request, 'login.html', {'form': form, 'error_message': error_message})
