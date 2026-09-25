# Mirror – Smart Wall Dashboard

Böngészőből megnyitható, Raspberry Pi / mini szerver / Docker hoston futtatható fal-dashboard.

Jelenlegi funkciók:
- heti Google Calendar nézet iCal URL-ből
- Trello listák és kártyák
- Open-Meteo időjárás
- automatikus ruhajavaslat
- 5 percenkénti automatikus frissítés
- reszponzív, sötét dashboard UI
- Docker Compose futtatás

## Gyors indítás

```bash
git clone https://github.com/Nicqx/mirror.git
cd mirror
cp .env.template .env
nano .env
docker compose up -d --build
```

Ezután alapbeállítással:

```text
http://<szerver-ip>:8088
```

A külső port a `.env` fájlban a `MIRROR_PORT` értékével módosítható, így ugyanazon a gépen más webes szolgáltatások mellett is futhat.

## Konfiguráció és tokenek

A repó **nem tartalmaz valódi configot vagy tokent**.

A verziókezelt minta:

```text
.env.template
```

Ebből készíts helyi configot:

```bash
cp .env.template .env
```

Majd szerkeszd a `.env` fájlt. A `.env` szerepel a `.gitignore`-ban, ezért normál esetben nem kerül GitHubra.

Példa:

```env
MIRROR_PORT=8088

WEATHER_LAT=47.4979
WEATHER_LON=19.0402
WEATHER_TZ=Europe/Budapest

GOOGLE_CALENDAR_ICAL_URL=

TRELLO_KEY=
TRELLO_TOKEN=
TRELLO_BOARD_ID=
```

> Fontos: valódi Google Calendar secret URL-t, Trello tokent vagy más titkot ne írj a `.env.template` fájlba és ne commitolj GitHubra.

## Google Calendar

Az első verzió OAuth helyett a Google Calendar **Secret address in iCal format** címét használja.

Google Calendarban:

1. Nyisd meg a naptár beállításait.
2. Keresd meg az **Integrate calendar** részt.
3. Másold ki a **Secret address in iCal format** URL-t.
4. Tedd a helyi `.env` fájlba:

```env
GOOGLE_CALENDAR_ICAL_URL=https://...
```

Az URL-t csak a backend használja; a frontend nem kapja meg.

## Trello

A helyi `.env` fájlban add meg:

```env
TRELLO_KEY=
TRELLO_TOKEN=
TRELLO_BOARD_ID=
```

Ha ezek nincsenek beállítva, a dashboard demó Trello tartalmat mutat.

## Időjárás

Az időjárás az Open-Meteo API-t használja, amihez ehhez a használathoz nem kell külön API-kulcs.

Állítsd be a megjelenítendő hely koordinátáit és időzónáját:

```env
WEATHER_LAT=47.4979
WEATHER_LON=19.0402
WEATHER_TZ=Europe/Budapest
```

## Docker kezelés

Indítás / friss build:

```bash
docker compose up -d --build
```

Leállítás:

```bash
docker compose down
```

Log:

```bash
docker compose logs -f
```

Frissítés GitHubról:

```bash
git pull
docker compose up -d --build
```

## Fájlstruktúra

```text
mirror/
├── app/
│   ├── main.py
│   └── static/
│       └── index.html
├── .dockerignore
├── .env.template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Tervezett következő lépések

- több Google Calendar támogatása
- eseményszínek és egész napos események jobb kezelése
- Trello kártyák részletesebb megjelenítése
- napszakfüggő layout
- ingress / reverse proxy támogatás
- Raspberry Pi kiosk mód
- monitor automatikus ON/OFF
- fizikai gomb vagy jelenlétérzékelő
