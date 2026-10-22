# UAS AI Ground Control Station 

Tämä projekti on modulaarinen maa-asemaohjelmiston demo.  Järjestelmä yhdistää droonin reaaliaikaisen telemetrian ja tekoälypohjaisen konenäön (IMINT) yhtenäiseksi tilannekuvaksi.

## Arkkitehtuuri ja moduulit

Rakennettu aikaisemman Rottendam seurannan opettaman arkkitehtuurinn päälle pienillä muokkauksilla 
Projekti on jaettu selkeisiin moduuleihin, jotta raskas kuva-analyysi ei jäädytä kriittistä paikkatietodataa kun analysointiin kuluu liikaa aikaa. 

Järjestelmä koostuu seuraavista osista:

* **app.py (Käyttöliittymä)**: Streamlitillä ja Foliumilla toteutettu visuaalinen kojelauta. Vastaa lentoreittien suunnittelusta, kartan piirtämisestä ja datan esittämisestä käyttäjälle.
* **telemetry.py (Tietoliikenne)**: Vastaa datan vastaanotosta. Lukee Pymavlink-kirjaston avulla droonin tai SITL-simulaattorin lähettämää raakadataa (kuten GPS-koordinaatit ja akun tila).
* **vision.py (Konenäkö)**: Käsittelee kamerasyötteen. Simuloi raskaiden tekoälymallien (esim. LandCover.ai) toimintaa analysoimalla maastoa ja palauttamalla havainnot käyttöliittymälle.
* **database.py (Tietokanta)**: Paikallinen SQLite-tietokanta, johon tallennetaan suunnitellut reittipisteet, lentolokit sekä tekoälyn tekemät havainnot tarkkoine koordinaatteineen myöhempää raportointia varten.

## Teknologiat joita käytetään
* Kieli: Python
* Käyttöliittymä: Streamlit, streamlit-folium
* Paikkatieto ja analyysi: Folium, Pandas
* Drooni-integraatio: Pymavlink, SITL

```mermaid
graph LR
    %% -- TELEMETRIAN TIETOVIRTA (PAIKALLINEN) --
    subgraph Paikallinen_Telemetria [Maa-asema: Reittidata]
        A[Telemetry / AIS Source] -->|UDP / WebSocket| B[Ingestion & Parser]
        B -->|Clean JSON / Dataframe| C[Spatial Engine / Haversine]
    end

    %% -- GOOGLE EARTH ENGINE (PILVILASKENTA) --
    subgraph Pilvilaskenta [Pilvi: Google Earth Engine API]
        F[Sentinel-2 Kuva-arkisto] -->|SWIR-kaista B12| G[GEE Cloud Processing]
        G -.->|Massiivinen rinnakkaislaskenta Googlen palvelimilla| G
        G -->|Suodatuksen tulos: Kevyt JSON-vastaus| H[Koordinaattien purkaminen]
    end

    %% -- KÄYTTÖLIITTYMÄ JA TIETOKANTA (PAIKALLINEN) --
    subgraph Paikallinen_Ydin [Maa-asema: Tallennus ja UI]
        H -->|Lämpöpoikkeamien Lat/Lon| E[(SQLite Database)]
        C -->|Reittikoordinaatit| D[Folium Map / Streamlit UI]
        B -->|Lentohistoria| E
        E -.->|Datan haku käyttöliittymään| D
    end

    %% Tyylittely selkeyttämään pilven ja paikallisen eroa
    classDef cloud fill:#e6f7ff,stroke:#0099ff,stroke-width:2px;
    classDef local fill:#f9f9f9,stroke:#333,stroke-width:1px;
    class F,G,H cloud;
    class A,B,C,D,E local;

`
TAULU 1: LENTO (Ylätaso)
| id (Pääavain) | pvm_aika            | tehtava_tyyppi (Kategoria 1) |
|---------------|---------------------|------------------------------|
| 1             | 2026-10-22 14:00:00 | Reittisuunnitelma            |
| 2             | 2026-10-22 15:30:00 | Kartoituslento               |

TAULU 2: REITTIPISTE (Sidottu Lentoon)
| id | lento_id (Viittaus) | lat     | lon     | jarjestysnumero |
|----|---------------------|---------|---------|-----------------|
| 1  | 1                   | 62.2415 | 25.7209 | 1               |
| 2  | 1                   | 62.2450 | 25.7300 | 2               |

TAULU 3: HAVAINTO (Sidottu Lentoon)
| id | lento_id (Viittaus) | lat     | lon     | luokka (Kategoria 2)       | luotettavuus |
|----|---------------------|---------|---------|----------------------------|--------------|
| 1  | 1                   | 62.2420 | 25.7220 | Lämpöpoikkeama (Sentinel-2)| 0.90         |
