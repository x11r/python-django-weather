from django.shortcuts import render
from .models import Dailies
from datetime import date

# Create your views here.

def about_us(request):
    return render(request, 'weather_data/about.html')
def contact_us(request):
    return render(request, 'weather_data/contact.html')
def weather_top(request):
    # weather_item = Dailies.objects.
    station_name = request.GET.get('station', '')
    year_start = request.GET.get('start', '')
    year_end = request.GET.get('end', '')

    weather_data = Dailies.objects.all()[:100]

    # 年一覧
    year_now = int(date.today().strftime('%Y'))
    years = range(1880, year_now)

    # 検索機能が低いのが気になる
    if station_name and year_start and year_end:
        start_date = date(int(year_start), 1, 1)
        end_date = date(int(year_end), 12, 31)

        weather_data = Dailies.objects.filter(
                date__range=(start_date, end_date)
                ).filter(station_name=station_name)
    else:
        weather_data = None

    return render(request, 'weather_data/weather_top.html', {
        'weather_data': weather_data,
        'year_start': int(year_start),
        'year_end': int(year_end),
        'years': years,
        'station_name': station_name
    })
