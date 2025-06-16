from django.shortcuts import render
from .models import Dailies
from datetime import date, timedelta

from .utils.load_config import load_config

# Create your views here.

def about_us(request):
    return render(request, 'weather_data/about.html')
def contact_us(request):
    return render(request, 'weather_data/contact.html')
def weather_top(request):
    station_name = request.GET.get('station', '')
    year = request.GET.get('year', '')

    config = load_config()
    # print('config', config)

    # 年一覧
    year_now = int(date.today().strftime('%Y'))
    years = range(1880, year_now)

    # 日付別気象一覧
    weather_data_list = []

    # 検索機能が低いのが気になる
    if station_name and year:
        start_date = date(int(year), 1, 1)
        end_date = date(int(year), 12, 31)

        # 気象情報取得
        weather_data = Dailies.objects.filter(
                date__range=(start_date, end_date)
                ).filter(station_name=station_name)
        
        if year == year_now:
            end_date = date.today() - timedelta(days=1)
        else:
            end_date = date(int(year), 12, 31)
        
        # 日付一覧
        current = start_date
        while current <= end_date:
            # 取得した気象情報のうち、日付で絞ったもの探す
            weather = next((d for d in weather_data if d.date == current), {
                'date': current,
                'station_name': None,
                'temperature_highest': None,
                'temperature_lowest': None,
            })

            weather_data_list.append(weather)

            current += timedelta(days=1)

    else:
        weather_data = None

    print('type of year', type(year))

    return render(request, 'weather_data/weather_top.html', {
        'weather_data_list': weather_data_list,
        'year': int(year),
        'years': years,
        'station_name': station_name,
        'weather_data': weather_data,
        'config': config
    })
