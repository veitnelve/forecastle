import requests.packages.urllib3
from django.shortcuts import render, redirect
import requests as req
from geopy import geocoders
import json
from .models import City
from .forms import CityForm

requests.packages.urllib3.disable_warnings()
ya_token = 'cb1dd557-b24e-44e5-9de7-35d121beea5f'


def index(request):
    cities = City.objects.all()

    error = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            duplicate_city = City.objects.filter(name=new_city).count()

            if duplicate_city == 0:
                form.save()
            else:
                error = 'Этот город уже добавлен!'

        if error:
            message = error
            message_class = 'alert-danger'
        else:
            message = 'Город успешно добавлен!'
            message_class = 'alert-success'

    form = CityForm()

    weather_data = []

    for city in cities:
        def geo_pos(city: str):
            geolocator = geocoders.Nominatim(user_agent='forecastle')
            latitude = str(geolocator.geocode(city).latitude)
            longitude = str(geolocator.geocode(city).longitude)
            return latitude, longitude

        latitude, longitude = geo_pos(city)

        url_ya = f'https://api.weather.yandex.ru/v2/informers?lat={latitude}&lon={longitude}'
        ya_req = req.get(url_ya, headers={'X-Yandex-API-Key': ya_token}, verify=False)

        ya_json = json.loads(ya_req.text)

        weather = {
            'city': city,
            'temperature': ya_json['fact']['temp'],
            'description': ya_json['fact']['condition'],
            'icon': ya_json['fact']['icon'],
            'link': ya_json['info']['url']
        }

        weather_data.append(weather)

    context = {
        'weather_data' : weather_data,
        'form' : form,
        'message' : message,
        'message_class' : message_class
    }

    return render(request, 'weather/index.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()

    return redirect('home')
