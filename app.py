import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
# --- määrityksiä ulkoasulle---# Määritetään Streamlit-sivun leveys ja koko ruutu, jotta kartta mahtuu hyvin.
st.set_page_config(page_title="UAS Maa-asema", layout="wide")
st.title("Tilannekuva (GCS)")
def luo_kartta():
    """Luo Folium-kartan, hakee Esri-satelliittikuvat ja lisää piirtotyökalun."""
    
    # Voit muokata aloitussijaintia muuttamalla 'location' arvoja [Leveysaste, Pituusaste]
    # 'zoom_start' määrittää kuinka lähelle kartta on zoomattu alussa (1-20).
    m = folium.Map(location=[62.2415, 25.7209], zoom_start=13, tiles=None)
    
    # Esri World Imagery URL satelliittikuville
    esri_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    folium.TileLayer(
        tiles=esri_url, 
        attr='Tiles &copy; Esri', 
        name='Esri Satelliitti', 
        control=False
    ).add_to(m)
# Lisätään piirtotyökalut karttaan (vain viivat, alueet ja reittipisteet sallittu)
    piirtotyokalut = Draw(
        export=False, position='topleft',
        draw_options={
            'polyline': True, 
            'polygon': True, 
            'marker': True, 
            'circle': False, 
            'circlemarker': False, 
            'rectangle': False,
'rectangle': False
        }
    )
    piirtotyokalut.add_to(m)
    return m

def pura_koordinaatit(geojson_data):
    """Parsii GeoJSON-datasta ulos puhtaat koordinaatit listaksi."""
    koordinaatit = []
    
    # Jos dataa ei ole olemassa, palautetaan tyhjä lista
    if not geojson_data or 'features' not in geojson_data:
        return koordinaatit
    
    # Käydään läpi kaikki käyttäjän piirtämät muodot
    for feature in geojson_data['features']:
        geom_type = feature['geometry']['type']
        coords = feature['geometry']['coordinates']
        
        # GeoJSON antaa koordinaatit muodossa [lon, lat], käännämme ne [lat, lon]
        if geom_type == 'Point':
            koordinaatit.append((coords[1], coords[0]))
        elif geom_type == 'LineString':
            for c in coords:
                koordinaatit.append((c[1], c[0]))
                
    return koordinaatit

# --- KÄYTTÖLIITTYMÄN RAKENNE ---
# Jaetaan näyttö kahteen sarakkeeseen: vasen sarake kartalle (suurempi), oikea datalle.
vasen_sarake, oikea_sarake = st.columns([3, 1])

with vasen_sarake:
    kartta_olio = luo_kartta()
    # st_folium piirtää kartan ja palauttaa datan, jos käyttäjä piirtää siihen
    kartan_tiedot = st_folium(kartta_olio, width="100%", height=700)

with oikea_sarake:
    st.subheader("Reittisuunnittelu")
    
    # Jos kartan tiedoista löytyy piirroksia, käsitellään ne
    if kartan_tiedot and kartan_tiedot.get("all_drawings"):
        st.success("Reittidata vastaanotettu!")
        piirrokset = kartan_tiedot["all_drawings"]
        
        # Pura koordinaatit datasta
        reittipisteet = pura_koordinaatit(piirrokset)
        
        st.write("Erotellut reittipisteet (Lat, Lon):")
        for i, piste in enumerate(reittipisteet):
            # Tulostetaan kukin piste viiden desimaalin tarkkuudella
            st.write(f"**Piste {i+1}:** {piste[0]:.5f}, {piste[1]:.5f}")
    else:
        st.info("Piirrä reitti tai aseta reittipisteitä kartan vasemman yläkulman työkaluilla.")
