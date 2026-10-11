import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import database

# Varmistetaan, että tietokannan taulut luodaan käynnistyksessä, jos niitä ei ole
database.alusta_tietokanta()

# --- ASETUKSET ---
st.set_page_config(page_title="UAS Maa-asema", layout="wide")
st.title(" Tilannekuva (MUISTA MUOKATA SIVU NÄTIKSI")

def luo_kartta():
    """Luo Folium-kartan ja lisää siihen Esri-satelliittikuvat sekä piirtotyökalut."""
    m = folium.Map(location=[62.2415, 25.7209], zoom_start=13, tiles=None)
    
    esri_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    folium.TileLayer(
        tiles=esri_url, 
        attr='Tiles &copy; Esri', 
        name='Esri Satelliitti', 
        control=False
    ).add_to(m)
    
    piirtotyokalut = Draw(
        export=False, position='topleft',
        draw_options={
            'polyline': True, 
            'polygon': True, 
            'marker': True, 
            'circle': False, 
            'circlemarker': False, 
            'rectangle': False
        }
    )
    piirtotyokalut.add_to(m)
    return m

def pura_koordinaatit(geojson_data):
    """Parsii GeoJSON-datasta ulos puhtaat koordinaatit listaksi."""
    koordinaatit = []
    
    if not geojson_data or 'features' not in geojson_data:
        return koordinaatit
    
    for feature in geojson_data['features']:
        geom_type = feature['geometry']['type']
        coords = feature['geometry']['coordinates']
        
        # GeoJSON: [lon, lat] -> Käännetään muotoon [lat, lon]
        if geom_type == 'Point':
            koordinaatit.append((coords[1], coords[0]))
        elif geom_type == 'LineString':
            for c in coords:
                koordinaatit.append((c[1], c[0]))
                
    return koordinaatit

# --- KÄYTTÖLIITTYMÄN RAKENNE ---
vasen_sarake, oikea_sarake = st.columns([3, 1])

with vasen_sarake:
    kartta_olio = luo_kartta()
    kartan_tiedot = st_folium(kartta_olio, width="100%", height=700)

with oikea_sarake:
    st.subheader("Reittisuunnittelu")
    
    if kartan_tiedot and kartan_tiedot.get("all_drawings"):
        piirrokset = kartan_tiedot["all_drawings"]
        reittipisteet = pura_koordinaatit(piirrokset)
        
        if reittipisteet:
            st.success("Reittidata vastaanotettu!")
            st.write("Erotellut reittipisteet (Lat, Lon):")
            for i, piste in enumerate(reittipisteet):
                st.write(f"**Piste {i+1}:** {piste[0]:.5f}, {piste[1]:.5f}")
            
            # --- TALLENNUS TIETOKANTAAN ---
            if st.button("Tallenna reitti tietokantaan"):
                # Kutsutaan database.py:n tallennusfunktiota
                lento_id = database.tallenna_reitti("Reittisuunnitelma", reittipisteet)
                st.success(f"Reitti tallennettu! Lennokille luotiin ID: {lento_id}")
        else:
            st.info("Piirrä reitti tai aseta reittipisteitä kartan työkaluilla.")
    else:
        st.info("Piirrä reitti tai aseta reittipisteitä kartan vasemman yläkulman työkaluilla.")
    st.divider()
    st.subheader("Tallennetut lennot")
    
    tallennetut = database.hae_lennot()
    
    if tallennetut:
        import pandas as pd
        df = pd.DataFrame(tallennetut, columns=["ID", "Aikaleima", "Tehtävätyyppi"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Ei vielä tallennettuja lentoja. Piirrä ja tallenna ensimmäinen reittisi!")
