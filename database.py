import sqlite3
from datetime import datetime

def luo_yhteys():
    """Luo yhteyden SQLite-tietokantaan. Jos tiedostoa ei ole, se luodaan."""
    return sqlite3.connect("uas-maa-asema.db")

def alusta_tietokanta():
    """Rakentaa tietokannan taulut suunnitellun ER-kaavion pohjalta."""
    conn = luo_yhteys()
    cursor = conn.cursor()

    # 1. LENTO-taulu (Päätaulu lennon perustiedoille)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pvm_aika TEXT,
            tehtava_tyyppi TEXT
        )
    ''')

    # 2. REITTIPISTE-taulu (Kartalle piirretyt pisteet, viittaa LENTO-tauluun)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reittipiste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lento_id INTEGER,
            lat REAL,
            lon REAL,
            jarjestysnumero INTEGER,
            FOREIGN KEY(lento_id) REFERENCES lento(id)
        )
    ''')

    # 3. HAVAINTO-taulu (Tekoälyn poikkeamahavainnot, viittaa LENTO-tauluun)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS havainto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lento_id INTEGER,
            lat REAL,
            lon REAL,
            luokka TEXT,
            luotettavuus REAL,
            FOREIGN KEY(lento_id) REFERENCES lento(id)
        )
    ''')

    conn.commit()
    conn.close()

def tallenna_reitti(tehtava_tyyppi, koordinaatit):
    """Ottaa vastaan reitin käyttöliittymästä ja tallentaa sen kantaan."""
    conn = luo_yhteys()
    cursor = conn.cursor()

    # Tallennetaan ensin uusi lento aikaleiman kera//Huomaa aikaleima vielä muodossa vuosi ekana
    pvm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO lento (pvm_aika, tehtava_tyyppi) VALUES (?, ?)", (pvm, tehtava_tyyppi))
    
    # Otetaan talteen juuri luodun lennon ID
    lento_id = cursor.lastrowid

    # Sidotaan jokainen koordinaatti äsken luotuun lentoon
    for index, piste in enumerate(koordinaatit):
        cursor.execute(
            "INSERT INTO reittipiste (lento_id, lat, lon, jarjestysnumero) VALUES (?, ?, ?, ?)",
            (lento_id, piste[0], piste[1], index + 1)
        )

    conn.commit()
    conn.close()
    
    # Palautetaan lennon ID, jotta  se jää käyttäjälle tietoon
    return lento_id

def hae_lennot():
    """Hakee ja palauttaa kaikki tallennetut lennot tietokannasta."""
    conn = luo_yhteys()
    cursor = conn.cursor()
    
    # Haetaan data lento-taulusta, uusin ensin (DESC)
    cursor.execute("SELECT id, pvm_aika, tehtava_tyyppi FROM lento ORDER BY id DESC")
    lennot = cursor.fetchall()
    
    conn.close()
    return lennot

def tallenna_havainto(lento_id, lat, lon, luokka, luotettavuus):
    """
    Tallentaa konenäön (ML) tekemän satelliittikuvahavainnon tietokantaan.
    Georeferoitu data (lat, lon) yhdistetään aktiiviseen lentoon.
    """
    conn = luo_yhteys()
    cursor = conn.cursor()
    
    # Syötetään tekoälyn havainnot havainto-tauluun
    cursor.execute(
        "INSERT INTO havainto (lento_id, lat, lon, luokka, luotettavuus) VALUES (?, ?, ?, ?, ?)",
        (lento_id, lat, lon, luokka, luotettavuus)
    )
    
    havainto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return havainto_id

# Testissä muistutusviesti kun en muista mihin jään
if __name__ == "__main__":
    alusta_tietokanta()
    print("tietokanta tehty")
IndentationError
