import os
import datetime as dt
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from icalendar import Calendar

app = FastAPI(title='Smart Wall Dashboard')
app.mount('/static', StaticFiles(directory='app/static'), name='static')

WEATHER_LAT = float(os.getenv('WEATHER_LAT', '47.4979'))
WEATHER_LON = float(os.getenv('WEATHER_LON', '19.0402'))
WEATHER_TZ = os.getenv('WEATHER_TZ', 'Europe/Budapest')
GOOGLE_CALENDAR_ICAL_URL = os.getenv('GOOGLE_CALENDAR_ICAL_URL', '')
TRELLO_KEY = os.getenv('TRELLO_KEY', '')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN', '')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID', '')

@app.get('/')
async def index():
    return FileResponse('app/static/index.html')

@app.get('/api/weather')
async def weather() -> dict[str, Any]:
    params = {
        'latitude': WEATHER_LAT,
        'longitude': WEATHER_LON,
        'timezone': WEATHER_TZ,
        'current': 'temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m',
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code',
        'forecast_days': 7,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
        r.raise_for_status()
        data = r.json()

    c = data['current']
    d = data['daily']
    temp = c['temperature_2m']
    feels = c['apparent_temperature']
    rain = d['precipitation_probability_max'][0]
    wind = c['wind_speed_10m']

    clothes = []
    if feels <= 5:
        clothes += ['meleg kabát', 'pulóver', 'hosszúnadrág']
    elif feels <= 12:
        clothes += ['könnyű kabát', 'pulóver', 'hosszúnadrág']
    elif feels <= 18:
        clothes += ['pulóver vagy vékony dzseki', 'hosszúnadrág']
    else:
        clothes += ['póló', 'könnyű nadrág']
    if rain >= 40:
        clothes.append('esernyő')
    if wind >= 35:
        clothes.append('szélálló felső')

    return {
        'current': {'temperature': temp, 'feels_like': feels, 'wind': wind, 'precipitation': c['precipitation']},
        'today': {'min': d['temperature_2m_min'][0], 'max': d['temperature_2m_max'][0], 'rain_probability': rain},
        'clothing': clothes,
        'week': [
            {'date': d['time'][i], 'min': d['temperature_2m_min'][i], 'max': d['temperature_2m_max'][i], 'rain_probability': d['precipitation_probability_max'][i]}
            for i in range(min(7, len(d['time'])))
        ]
    }

@app.get('/api/calendar')
async def calendar() -> list[dict[str, Any]]:
    if not GOOGLE_CALENDAR_ICAL_URL:
        today = dt.datetime.now().date()
        return [
            {'title': 'Google Calendar nincs még beállítva', 'start': f'{today.isoformat()}T09:00:00', 'end': f'{today.isoformat()}T09:30:00'},
            {'title': 'Add meg a secret iCal URL-t az .env fájlban', 'start': f'{today.isoformat()}T17:00:00', 'end': f'{today.isoformat()}T17:30:00'},
        ]

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        r = await client.get(GOOGLE_CALENDAR_ICAL_URL)
        r.raise_for_status()
        cal = Calendar.from_ical(r.content)

    now = dt.datetime.now(dt.timezone.utc)
    end_window = now + dt.timedelta(days=7)
    out = []
    for component in cal.walk('VEVENT'):
        start = component.decoded('dtstart')
        end = component.decoded('dtend') if component.get('dtend') else start
        if isinstance(start, dt.date) and not isinstance(start, dt.datetime):
            start = dt.datetime.combine(start, dt.time.min, tzinfo=dt.timezone.utc)
        elif start.tzinfo is None:
            start = start.replace(tzinfo=dt.timezone.utc)
        if isinstance(end, dt.date) and not isinstance(end, dt.datetime):
            end = dt.datetime.combine(end, dt.time.min, tzinfo=dt.timezone.utc)
        elif end.tzinfo is None:
            end = end.replace(tzinfo=dt.timezone.utc)
        if now - dt.timedelta(days=1) <= start <= end_window:
            out.append({'title': str(component.get('summary', 'Névtelen esemény')), 'start': start.isoformat(), 'end': end.isoformat()})
    out.sort(key=lambda x: x['start'])
    return out[:30]

@app.get('/api/trello')
async def trello() -> list[dict[str, Any]]:
    if not (TRELLO_KEY and TRELLO_TOKEN and TRELLO_BOARD_ID):
        return [
            {'name': 'TEENDŐ', 'cards': ['Trello még nincs beállítva', 'Add meg a kulcsot/token/board ID-t']},
            {'name': 'FOLYAMATBAN', 'cards': ['Dashboard első verzió']},
            {'name': 'KÉSZ', 'cards': ['Webes alap']},
        ]

    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN, 'cards': 'open', 'card_fields': 'name'}
    url = f'https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists'
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        lists = r.json()
    return [{'name': x['name'], 'cards': [c['name'] for c in x.get('cards', [])]} for x in lists]
