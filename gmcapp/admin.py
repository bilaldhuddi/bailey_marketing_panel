from django.contrib import admin

from django.contrib.admin import AdminSite

from gmcapp.models import MessageTemplate


class CustomAdminSite(AdminSite):
    site_header = 'Custom Admin Panel'  # Customize the admin panel header


admin_site = CustomAdminSite(name='admin')  # Create an instance of your custom admin site

# Register your models with the custom admin site

# Register more models as needed
