from django.urls import path
from .views import *

urlpatterns = [
    path('', search_holidays, name='search-holidays'),
    path('api/holidays/', HolidayListView.as_view(), name='holiday-list'),
    path('api/search-holidays/', SearchHolidayView.as_view(), name='search-holiday'),
    path('api/filter-holidays/', FilterHolidaysView.as_view(), name='filter-holidays'),
    path('api/holiday-details/', HolidayDetailsView.as_view(), name='holiday-details'),
]

