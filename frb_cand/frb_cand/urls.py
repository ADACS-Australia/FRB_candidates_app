"""frb_cand URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from cand_app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('frbevent_create/', views.frbevent_create),
    path('frbevent_table/',  views.frbevent_table),
    path('frbevent_details/<int:id>/', views.frbevent_details),
    path('radio_measurement_create/', views.radio_measurement_create),
    path('observation_create/', views.observation_create),
    path('slack_get_rating/', views.slack_get_rating),
    path('trigger_pipeline/<int:id>/', views.trigger_pipeline),
]

# allow media files to be linked and viewed directly
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
