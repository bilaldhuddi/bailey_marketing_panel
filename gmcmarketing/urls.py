"""
URL configuration for gmcmarketing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from gmcapp import views
from gmcapp.views import (
    AutoResearchView,
    SettingsView,
    WebScrapingView,
    DeleteRecordView,
    EditRecordView,
    ExportSelectedRecordsView,
    CreateMessengerContactView,
    StartWhatsAppAutomation, StartMessangerAutomation, DashboardView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('research/', AutoResearchView.as_view(), name='research'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('web_scraping/', WebScrapingView.as_view(), name='web_scraping'),
    path('web_scraping/delete-record/', DeleteRecordView.as_view(), name='delete-record'),
    path('web_scraping/edit-record/', EditRecordView.as_view(), name='edit-record'),
    path('web_scraping/export-selected-records/', ExportSelectedRecordsView.as_view(), name='export-selected-records'),
    path('create_messenger_contact/', CreateMessengerContactView.as_view(), name='create_messenger_contact'),
    path('messaging_automation/', views.MessagingAutomationView.as_view(), name='messaging_automation'),
    path('messaging_automation/start_whatsapp_automation/', StartWhatsAppAutomation.as_view(), name='start_whatsapp_automation'),
    path('messaging_automation/start_messanger_automation/', StartMessangerAutomation.as_view(),
         name='start_whatsapp_automation'),
    path('edit_cities/', views.CityListView.as_view(), name='edit_cities'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)