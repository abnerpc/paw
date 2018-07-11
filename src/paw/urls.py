from django.contrib import admin
from django.urls import path, re_path, include

from pawapp.api import CallEventResource, BillResource

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),

    path('api/v0/call_events/', include(CallEventResource.urls())),
    re_path('^api/v0/bills/(?P<phone_number>\d+)/$', BillResource.as_detail()),
    re_path('^api/v0/bills/(?P<phone_number>\d+)/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})/$', BillResource.as_detail()),
]
