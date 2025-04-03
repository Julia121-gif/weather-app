import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
import json
import datetime
import os
import urllib.parse

# Установка размера окна для мобильного приложения
Window.size = (400, 650)

# API ключ OpenWeatherMap
API_KEY = "d818d1408119df9c8aee74992d7f4a78"
API_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&appid={}"

# Словарь для перевода описаний погоды
WEATHER_TRANSLATIONS = {
    'clear sky': 'Ясно',
    'few clouds': 'Малооблачно',
    'scattered clouds': 'Переменная облачность',
    'broken clouds': 'Облачно с прояснениями',
    'shower rain': 'Ливень',
    'rain': 'Дождь',
    'thunderstorm': 'Гроза',
    'snow': 'Снег',
    'mist': 'Туман',
    'overcast clouds': 'Пасмурно'
}

# Определение UI с помощью Kivy Language
KV = '''
<WeatherRoot>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.2, 1  # Темно-синий фон
        Rectangle:
            pos: self.pos
            size: self.size
    
    orientation: 'vertical'
    padding: 20
    spacing: 15
    
    Label:
        text: 'ПРОГНОЗ ПОГОДЫ'
        font_size: 28
        size_hint: 1, 0.1
        bold: True
        color: 1, 1, 1, 1
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, 0.1
        spacing: 10
        
        TextInput:
            id: city_input
            hint_text: 'Введите название города'
            multiline: False
            size_hint: 0.7, 1
            font_size: 18
            padding: [10, 10, 0, 0]
            background_color: 0.9, 0.9, 1, 0.8
            foreground_color: 0, 0, 0, 1
        
        Button:
            text: 'Поиск'
            size_hint: 0.3, 1
            font_size: 18
            bold: True
            background_normal: ''
            background_color: 0.8, 0.1, 0.1, 1  # Красный
            on_press: root.search_weather()
    
    Label:
        id: city_label
        text: ''
        font_size: 26
        size_hint: 1, 0.1
        color: 1, 1, 1, 1
    
    Label:
        id: date_label
        text: ''
        font_size: 16
        size_hint: 1, 0.05
        color: 0.7, 0.7, 1, 1  # Светло-голубой
    
    BoxLayout:
        id: weather_box
        orientation: 'vertical'
        size_hint: 1, 0.6
        padding: 10
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.12, 0.14, 0.33, 0.7  # Темно-синий с прозрачностью
            Rectangle:
                pos: self.pos
                size: self.size
                
        AsyncImage:
            id: weather_image
            source: ''
            size_hint: 1, 0.4
        
        Label:
            id: weather_description
            text: ''
            font_size: 22
            size_hint: 1, 0.1
            color: 1, 1, 1, 1
        
        Label:
            id: temp_label
            text: ''
            font_size: 48
            size_hint: 1, 0.2
            color: 1, 1, 1, 1
            bold: True
        
        GridLayout:
            cols: 2
            size_hint: 1, 0.3
            spacing: 10
            
            Label:
                id: humidity_box
                text: 'Влажность: ---'
                font_size: 16
                color: 1, 1, 1, 1
            
            Label:
                id: wind_box
                text: 'Ветер: --- м/с'
                font_size: 16
                color: 1, 1, 1, 1
                
            Label:
                id: pressure_box
                text: 'Давление: --- мм рт.ст.'
                font_size: 16
                color: 1, 1, 1, 1
                
            Label:
                id: feels_like_box
                text: 'Ощущается: ---°C'
                font_size: 16
                color: 1, 1, 1, 1
    
    Label:
        id: error_label
        text: ''
        color: 1, 0.3, 0.3, 1  # Красный
        size_hint: 1, 0.05
'''

class WeatherRoot(BoxLayout):
    def __init__(self, **kwargs):
        super(WeatherRoot, self).__init__(**kwargs)
        Clock.schedule_once(self._post_init)
    
    def _post_init(self, dt):
        self.city_input = self.ids.city_input
        self.city_label = self.ids.city_label
        self.date_label = self.ids.date_label
        self.weather_image = self.ids.weather_image
        self.weather_description = self.ids.weather_description
        self.temp_label = self.ids.temp_label
        self.humidity_box = self.ids.humidity_box
        self.wind_box = self.ids.wind_box
        self.pressure_box = self.ids.pressure_box
        self.feels_like_box = self.ids.feels_like_box
        self.error_label = self.ids.error_label
        
        # Установка текущей даты в русском формате
        now = datetime.datetime.now()
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        self.date_label.text = f"{now.day} {months[now.month-1]} {now.year}"
    
    def search_weather(self):
        city = self.city_input.text.strip()
        if not city:
            self.error_label.text = "Пожалуйста, введите название города"
            return
        
        self.error_label.text = "Загрузка..."
        
        # Кодирование города для URL (для поддержки русских городов)
        encoded_city = urllib.parse.quote(city)
        url = API_URL.format(encoded_city, API_KEY)
        
        UrlRequest(url, on_success=self.weather_success, on_failure=self.weather_error, on_error=self.weather_error)
    
    def weather_success(self, request, result):
        self.error_label.text = ""
        data = result
        
        # Обновляем информацию о погоде
        # Используем русские названия стран, если возможно
        country_code = data['sys']['country']
        country_name = self.get_country_name(country_code)
        
        self.city_label.text = f"{data['name']}, {country_name}"
        
        # Используем русское описание погоды из API (lang=ru)
        weather_description = data['weather'][0]['description']
        self.weather_description.text = weather_description.capitalize()
        
        # Иконка погоды
        icon_code = data['weather'][0]['icon']
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
        self.weather_image.source = icon_url
        
        # Температура
        temperature = int(round(data['main']['temp']))
        self.temp_label.text = f"{temperature}°C"
        
        # Влажность
        humidity = data['main']['humidity']
        self.humidity_box.text = f"Влажность: {humidity}%"
        
        # Ветер
        wind_speed = data['wind']['speed']
        self.wind_box.text = f"Ветер: {wind_speed} м/с"
        
        # Давление (конвертируем из гПа в мм рт.ст.)
        pressure = int(round(data['main']['pressure'] * 0.750062))
        self.pressure_box.text = f"Давление: {pressure} мм рт.ст."
        
        # Ощущаемая температура
        feels_like = int(round(data['main']['feels_like']))
        self.feels_like_box.text = f"Ощущается: {feels_like}°C"
    
    def weather_error(self, request, error):
        self.error_label.text = "Ошибка при получении данных о погоде. Проверьте название города."
    
    def get_country_name(self, country_code):
        # Словарь кодов стран и их русских названий
        country_dict = {
            'RU': 'Россия',
            'US': 'США',
            'GB': 'Великобритания',
            'DE': 'Германия',
            'FR': 'Франция',
            'IT': 'Италия',
            'ES': 'Испания',
            'CN': 'Китай',
            'JP': 'Япония',
            'UA': 'Украина',
            'BY': 'Беларусь',
            'KZ': 'Казахстан',
            'GE': 'Грузия',
            'AM': 'Армения',
            'AZ': 'Азербайджан',
            'LV': 'Латвия',
            'LT': 'Литва',
            'EE': 'Эстония',
            'MD': 'Молдова',
            'KG': 'Киргизия',
            'TJ': 'Таджикистан',
            'TM': 'Туркменистан',
            'UZ': 'Узбекистан',
            'CA': 'Канада',
            'AU': 'Австралия',
            'NZ': 'Новая Зеландия',
            'BR': 'Бразилия',
            'AR': 'Аргентина',
            'CL': 'Чили',
            'CO': 'Колумбия',
            'PE': 'Перу',
            'MX': 'Мексика',
            'EG': 'Египет',
            'ZA': 'ЮАР',
            'SA': 'Саудовская Аравия',
            'AE': 'ОАЭ',
            'IN': 'Индия',
            'PK': 'Пакистан',
            'TR': 'Турция',
            'IL': 'Израиль',
            'IR': 'Иран',
            'TH': 'Таиланд',
            'SG': 'Сингапур',
            'PL': 'Польша',
            'CZ': 'Чехия',
            'SK': 'Словакия',
            'HU': 'Венгрия',
            'RO': 'Румыния',
            'BG': 'Болгария',
            'RS': 'Сербия',
            'HR': 'Хорватия',
            'SI': 'Словения',
            'GR': 'Греция',
            'BE': 'Бельгия',
            'NL': 'Нидерланды',
            'PT': 'Португалия',
            'SE': 'Швеция',
            'NO': 'Норвегия',
            'FI': 'Финляндия',
            'DK': 'Дания',
            'CH': 'Швейцария',
            'AT': 'Австрия',
            'IE': 'Ирландия',
            'IS': 'Исландия',
            'LU': 'Люксембург',
            'MC': 'Монако',
            'AD': 'Андорра',
            'LI': 'Лихтенштейн',
            'MT': 'Мальта',
            'CY': 'Кипр'
        }
        return country_dict.get(country_code, country_code)


class WeatherApp(App):
    def build(self):
        # Устанавливаем русскую локаль для правильного отображения кириллицы
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
            except:
                pass  # Если не удалось установить русскую локаль, используем текущую
        
        # Загружаем KV язык
        Builder.load_string(KV)
        return WeatherRoot()


if __name__ == '__main__':
    WeatherApp().run()