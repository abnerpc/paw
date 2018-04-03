from django.contrib import admin
from django.urls import path, include

from pawapp.api import CallEventResource

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v0/call_events/', include(CallEventResource.urls())),

    path('django-rq/', include('django_rq.urls')),
]
