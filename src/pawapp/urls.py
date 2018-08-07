from django.urls import path, re_path, include

from pawapp.api import CallEventResource, BillResource


urlpatterns = [
    path('v0/call_events/', include(CallEventResource.urls())),
    re_path('v0/bills/(?P<phone_number>\d+)/$', BillResource.as_detail()),
    re_path('v0/bills/(?P<phone_number>\d+)/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})/$', BillResource.as_detail()),
]
