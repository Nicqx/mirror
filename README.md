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


## Kubernetes / k3s telepítés

A production cél a meglévő egy-node-os k3s környezet. A repo tartalmaz:

- `k8s/mirror.yaml` — ConfigMap + Deployment + Service
- `k8s/config.env.template` — környezetfüggő config mintája
- `k8s/secret.env.template` — titkok mintája
- `scripts/update.sh` — build → k3s image import → apply → rollout
- `update.sh` — vékony wrapper

A Mirror Kubernetesben natívan a `/mirror` base pathot használja. A publikus route-ot a külön `Nicqx/ingress` repo kezeli Traefikkel.

### 1. Helyi Kubernetes config és titkok előkészítése

```bash
cp k8s/config.env.template k8s/config.env
cp k8s/secret.env.template k8s/secret.env

nano k8s/config.env
nano k8s/secret.env
```

A `k8s/config.env` tartalmazza a nem titkos, környezetfüggő értékeket:

```env
BASE_PATH=/mirror
WEATHER_LAT=47.4979
WEATHER_LON=19.0402
WEATHER_TZ=Europe/Budapest
```

A `k8s/secret.env` tartalmazza a titkokat:

```env
GOOGLE_CALENDAR_ICAL_URL=
TRELLO_KEY=
TRELLO_TOKEN=
TRELLO_BOARD_ID=
```

Mindkét helyi fájl gitignore-olt. Az update script a configból `mirror-config` ConfigMapet, a titkokból `mirror-secrets` Kubernetes Secretet hoz létre/frissít.

### 2. Dry-run

Pi 5:

```bash
KUBECTL='sudo k3s kubectl' sh update.sh --target pi5 --dry-run
```

NUC:

```bash
sh update.sh --target nuc --dry-run
```

### 3. Telepítés / frissítés

Pi 5:

```bash
KUBECTL='sudo k3s kubectl' sh update.sh --target pi5
```

NUC:

```bash
sh update.sh --target nuc
```

A script:

1. ellenőrzi, hogy a kube-context a kért egy-node-os clusterre mutat;
2. `git pull --ff-only`-t futtat;
3. Git commit + architektúra alapján egyedi image taget készít;
4. Docker image-et buildel;
5. az image-et a k3s containerd-be importálja;
6. létrehozza/frissíti a `mirror-secrets` Secretet;
7. alkalmazza a ConfigMap + Deployment + Service manifestet;
8. megvárja a rollout végét.

A Service neve:

```text
mirror-service:8080
```

A pod readiness/liveness endpointjai:

```text
/healthz
/livez
```

### 4. Publikus /mirror útvonal

A publikus HTTPS útvonalat a közös ingress repo kezeli:

```text
https://pmqxyz.hopto.org/mirror/
```

A Mirror maga kezeli a `/mirror` prefixet, ezért nincs szükség külön strip-prefix middleware-re.


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
- Raspberry Pi kiosk mód
- monitor automatikus ON/OFF
- fizikai gomb vagy jelenlétérzékelő
