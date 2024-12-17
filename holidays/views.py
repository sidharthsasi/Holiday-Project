from django.shortcuts import render
import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from datetime import datetime
from .serializers import HolidaySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import *
# Create your views here.





class HolidayListView(generics.ListAPIView):
    def get(self, request):
        # Extract query parameters
        country = request.GET.get('country')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Validate required parameters
        if not country or not year:
            return Response({"error": "Country and year parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"holidays_{country}_{year}"
        if month:
            cache_key += f"_{month}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Fetch data from the Calendarific API
        api_key = settings.CALENDARIFIC_API_KEY  
        url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()

                print("Raw response data:", response_data)  
             
                holidays = response_data.get('response', [])

                if isinstance(holidays, list):
                    if month:
                        holidays = [holiday for holiday in holidays if holiday['date']['iso'][5:7] == month]

                   
                    serialized_data = [
                        {
                            "name": holiday['name'],
                            "date": holiday['date']['iso'],
                            "description": holiday.get('description', 'No description available')
                        }
                        for holiday in holidays
                    ]

                    cache.set(cache_key, serialized_data, timeout=86400)

                    return Response(serialized_data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid format for 'holidays' field"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({"error": "Failed to fetch holidays from Calendarific API"}, status=response.status_code)

        except requests.RequestException as e:
            return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class SearchHolidayView(APIView):
    """
    Search holidays by name for a given country and year.
    """
    def get(self, request):
        country = request.GET.get('country')
        year = request.GET.get('year')
        search_query = request.GET.get('name', '').lower()

        if not country or not year or not search_query:
            return Response({"error": "Country, year, and name parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"holidays_{country}_{year}"

        holidays = cache.get(cache_key)

  
        if not holidays:
            api_key = settings.CALENDARIFIC_API_KEY
            url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}"

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    holidays = response.json().get('response', {}).get('holidays', [])

                    #
                    cache.set(cache_key, holidays, timeout=86400)
                else:
                    return Response({"error": "Failed to fetch holidays from Calendarific API"}, status=response.status_code)
            except requests.RequestException as e:
                return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

     
        filtered_holidays = [
            {
                "name": holiday['name'],
                "date": holiday['date']['iso'],
                "description": holiday['description']
            }
            for holiday in holidays if search_query in holiday['name'].lower()
        ]

        return Response(filtered_holidays, status=status.HTTP_200_OK)
    


class FilterHolidaysView(APIView):
    def get(self, request):
        country = request.GET.get('country')
        year = request.GET.get('year')
        month = request.GET.get('month')

       
        if not country or not year:
            return JsonResponse({'error': 'Country and year are required'}, status=400)

        cache_key = f"holidays_{country}_{year}"
        holidays = cache.get(cache_key)

        if not holidays:
           
            api_key = settings.CALENDARIFIC_API_KEY
            url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}"
            response = requests.get(url)

            if response.status_code == 200:
                holidays = response.json().get('response', {}).get('holidays', [])
                cache.set(cache_key, holidays, 86400)  # Cache for 24 hours
            else:
                return JsonResponse({'error': 'Failed to fetch holidays'}, status=500)

      
        if month:
            holidays = [
                holiday for holiday in holidays
                if holiday['date']['datetime']['month'] == int(month)
            ]

        # Format data for the response
        formatted_holidays = [
            {
                'name': holiday['name'],
                'date': holiday['date']['iso'],
                'description': holiday.get('description', 'No description available')
            }
            for holiday in holidays
        ]

        return JsonResponse(formatted_holidays, safe=False)




class HolidayDetailsView(APIView):
    def get(self, request):
        country = request.GET.get('country')
        year = request.GET.get('year')
        name = request.GET.get('name')
        date = request.GET.get('date')

        
        if not country or not year or not name or not date:
            return JsonResponse({'error': 'Country, year, name, and date are required'}, status=400)

     
        cache_key = f"holidays_{country}_{year}"
        holidays = cache.get(cache_key)

        if not holidays:
           
            api_key = settings.CALENDARIFIC_API_KEY
            url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}"
            response = requests.get(url)

            if response.status_code == 200:
                holidays = response.json().get('response', {}).get('holidays', [])
                cache.set(cache_key, holidays, 86400)  # Cache for 24 hours
            else:
                return JsonResponse({'error': 'Failed to fetch holidays'}, status=500)

        holiday_detail = next(
            (holiday for holiday in holidays if holiday['name'] == name and holiday['date']['iso'] == date),
            None
        )

        if not holiday_detail:
            return JsonResponse({'error': 'Holiday not found'}, status=404)

        # Format the holiday details
        formatted_details = {
            'name': holiday_detail['name'],
            'date': holiday_detail['date']['iso'],
            'description': holiday_detail.get('description', 'No description available'),
            'type': ', '.join(holiday_detail.get('type', [])),
            'locations': holiday_detail.get('locations', 'N/A'),
            'country': holiday_detail['country']['name'],
        }

        return JsonResponse(formatted_details)





def search_holidays(request):

    CALENDARIFIC_API_KEY = 'Gg6fo4LvZG1gR0Uo8rhsxhc91VLsl7t9'
    
   
    search_query = request.GET.get('search', '').lower()
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year', datetime.now().year)
    country_code = 'US'  

    
    response = requests.get(
        f"https://calendarific.com/api/v2/holidays",
        params={
            'api_key': CALENDARIFIC_API_KEY,
            'country': country_code,
            'year': selected_year
        }
    )

    holidays = response.json().get('response', {}).get('holidays', [])

    if search_query:
        holidays = [h for h in holidays if search_query in h['name'].lower()]
    
    if selected_month:
        holidays = [h for h in holidays if h['date']['datetime']['month'] == int(selected_month)]

    context = {
        'holidays': holidays,
        'months': [(str(i).zfill(2), datetime(2023, i, 1).strftime('%B')) for i in range(1, 13)],
        'years': [str(y) for y in range(2020, 2031)],
    }
    return render(request, 'holiday_list.html', context)