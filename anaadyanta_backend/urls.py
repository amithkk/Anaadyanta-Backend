"""anaadyanta_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from aybackend import views


admin.site.site_header = 'Anaadyanta Framework Admin'

urlpatterns = [
    path(r'', RedirectView.as_view(url='/admin')),
    path(r'accounts/login/', RedirectView.as_view(url='/admin/login')),
    path('admin/', admin.site.urls),
    path('events/', views.eventlist_view),
    path('api/get_events/', views.get_events),
    path('api/do_register', views.do_registration),
    path('admin/export_xslx_registrations', views.export_xslx),
    path('admin/firebase_sync', views.do_firebase_sync),
    path('admin/event_sync', views.do_event_fb_sync),
]
