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

```

#Tietokantarakenteen hahmotelma:

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#f4f9ff",
    "primaryBorderColor": "#0055ff",
    "primaryTextColor": "#111111",
    "lineColor": "#0055ff",
    "secondaryColor": "#e6f0ff",
    "tertiaryColor": "#ffffff"
  }
}}%%

erDiagram
    LENTO {
        INTEGER id PK "Pääavain"
        TEXT pvm_aika "Lennon luontiaika"
        TEXT tehtava_tyyppi "Kategoria"
    }
    
    REITTIPISTE {
        INTEGER id PK "Pääavain"
        INTEGER lento_id FK "Viittaus Lento-tauluun"
        REAL lat "Leveysaste"
        REAL lon "Pituusaste"
        INTEGER jarjestysnumero "Pisteen järjestys"
    }

    %% UUSI KONENÄKÖKOKONAISUUS
    KONENAKO_ANALYYSI {
        INTEGER id PK "Pääavain"
        INTEGER lento_id FK "Viittaus Lento-tauluun"
        TEXT satelliitti_lahde "Esim. Sentinel-2"
        TEXT tekoaly_malli "Esim. GEE SWIR-algoritmi"
        TEXT pvm_aika "Analyysin suoritusaika"
    }
    
    HAVAINTO {
        INTEGER id PK "Pääavain"
        INTEGER analyysi_id FK "Viittaus Konenäkö-analyysiin"
        REAL lat "Leveysaste"
        REAL lon "Pituusaste"
        TEXT luokka "Kohteen luokka"
        REAL luotettavuus "0.0 - 1.0"
    }

    %% Relaatiot
    LENTO ||--o{ REITTIPISTE : "koostuu"
    LENTO ||--o{ KONENAKO_ANALYYSI : "käynnistää"
    KONENAKO_ANALYYSI ||--o{ HAVAINTO : "tuottaa"

```


