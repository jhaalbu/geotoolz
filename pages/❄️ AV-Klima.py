'''Enkel webapp for uthenting av klimaanalyser i samband med skredfarevurderinger
Bruker streamlit pakken for å lage webapp fra python script
Utvikla av 
'''

import streamlit as st
from pyproj import Transformer
from klimadata import klimadata
from klimadata import plot
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(page_title="AV-Klima", page_icon=":snowflake:")

st.title("AV-Klima")
st.write("Enkel webapp for klimaanalyser basert på grid klimadata.")

# Setter liste med parametere brukt i analyse, tenkt å kunne utvides
parameterliste = ["rr", "tm", "sd", "fsw", "sdfsw", "sdfsw3d"]

# For kartbruk må koordinater transformerer mellom lat/lon og UTM
transformer = Transformer.from_crs(4326, 5973)

# Setter opp kartobjekt, med midtpunkt og zoom nivå
m = folium.Map(location=[62.14497, 9.404296], zoom_start=5)
#Legger til norgeskart som bakgrunn
# folium.raster_layers.WmsTileLayer(
#     url="https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}",
#     name="Norgeskart",
#     fmt="image/png",
#     layers="topo4",
#     attr='<a href="http://www.kartverket.no/">Kartverket</a>',
#     transparent=True,
#     overlay=True,
#     control=True,
# ).add_to(m)

# Litt knotete måte å hente ut koordinater fra Streamlit, kanskje bedre i nye versjoner av streamlit? Ev. litt bedre måte i rein javascript?
m.add_child(folium.ClickForMarker(popup="Waypoint"))
output = st_folium(m, width=700, height=500)

x = 0
y = 0
st.write("Trykk i kartet, eller skriv inn koordinater for å velge klimapunkt.")
st.write("Dersom du velger koordinat uten data, f.eks ved kyst eller midt i fjord vil du få feilmelding.")
st.write(
    "Tjenesten finn automatisk nærmaste stadnavn dersom det er eit navn innafor 500m radius."
)

# Enkel måte å vente på klikk i kartet
try:
    kart_kord_lat = output["last_clicked"]["lat"]
    kart_kord_lng = output["last_clicked"]["lng"]
    x, y = transformer.transform(kart_kord_lat, kart_kord_lng)
    y = round(y, 2)
    x = round(x, 2)

except TypeError:
    y = "Trykk i kart, eller skriv inn koordinat"
    x = "Trykk i kart, eller skriv inn koordinat"


y = st.text_input("Nord (UTM 33)", y)
x = st.text_input("Øst (UTM 33)", x)

# Venter på klikk, og prøver å finne stedsnavn
try:
    navn = klimadata.stedsnavn(x, y)["navn"][0]["stedsnavn"][0][
        "skrivemåte"
    ]
except (IndexError, KeyError):
    navn = "Skriv inn navn"

lokalitet = st.text_input("Gi navn til lokalitet (brukes i tittel på plot)", navn)

# Hardkoda start og sluttdato, det er mulig å utvide dette til å la bruker velge, 
# men funksjoner for plotting er ikke utvikla for å håndtere dette
startdato = "1958-01-01"
sluttdato = "2023-10-31"

#Lar brukere velge plotversjoner
plottype = st.radio(
    "Velg plottype", ("Klimaoversikt", "Klimaoversikt med 3 døgn snø og returverdi")
)

#Lar bruker velge om de vil ha annotert normalplot
annotert = st.checkbox("Vis tall på søylediagram og temperaturkurve for månedsnormaler.")

#Lar bruker velge om de vil ha vindanalyse
vind = st.checkbox("Kjør vindanalyse")

#Enkel knapp for å vente med kjøre resten av scriptet før input er registert
knapp = st.button("Vis plott")

if knapp:
    y = int(float(y.strip()))
    x = int(float(x.strip()))
    try:
        df = klimadata.klima_dataframe(x, y, startdato, sluttdato, parameterliste)
    except KeyError:
        st.write("OBS! Ingen data funnet for koordinat. Dersom du har valgt eit punkt nær kyst eller fjord kan dette være grunnen.")
        st.write("Sjekk dekning av data på xgeo.no eller senorge.no")
        st.stop()

    st.write(f'Modellhøgden frå punktet er {klimadata.hent_hogde(x, y)} moh. Denne kan avvike fra faktisk terrenghøgde.')
    st.write("Generering av plot tek litt tid, spesielt med returverdianalyse. Trykk på pil oppe i høgre hjørne av plot for å utvide.")

    if plottype == "Klimaoversikt":
        st.pyplot(plot.klimaoversikt(df, lokalitet, annotert, klimadata.hent_hogde(x, y)))
        st.download_button(
            "Last ned klimadata",
            df.to_csv().encode("utf-8"),
            "klimadata.csv",
            "text/csv",
            key="download-csv",
        )

        plt.savefig(f'Klimaoversikt_{lokalitet}.pdf')
        with open(f"Klimaoversikt_{lokalitet}.pdf", "rb") as file:
            btn=st.download_button(
            label="Last ned PDF plot",
            data=file,
            file_name=f"Klimaoversikt_{lokalitet}.pdf",
            mime="application/octet-stream"
        )

    if plottype == "Klimaoversikt med 3 døgn snø og returverdi":
        st.pyplot(plot.klima_sno_oversikt(df, lokalitet, annotert, klimadata.hent_hogde(x, y)))
        st.download_button(
            "Last ned klimadata",
            df.to_csv().encode("utf-8"),
            "klimadata.csv",
            "text/csv",
            key="download-csv",
        )
        plt.savefig(f'Klimaoversikt_{lokalitet}.pdf')
        with open(f"Klimaoversikt_{lokalitet}.pdf", "rb") as file:
            btn=st.download_button(
            label="Last ned PDF plot",
            data=file,
            file_name=f"Klimaoversikt_{lokalitet}.pdf",
            mime="application/octet-stream"
        )
        st.write("Vær obs på bruk av returverdier basert på griddata. Verdiene i plottet bør vurderes som første grove vurdering av returverdi.")
        st.write("For meir nøyaktige vurderinger av returverdier anbefales NVE rapport 2014/22.")

    if vind:
        st.subheader("Vind")
        st.write("Vindrosa viser kva retning vinden kjem frå. Dei forskjellige fargeplot syner vindstyrke, regn og snø. Sjå dokumentasjon på link nederst for utvida forklaring.")
        vind_para = [
            "windDirection10m24h06",
            "windSpeed10m24h06",
            "rr",
            "tm",
            "fsw",
            "rrl",
        ]
        vindslutt = "2023-03-01"
        vindstart = "2018-03-01"
        vind_df = klimadata.klima_dataframe(x, y, vindstart, vindslutt, vind_para)
        st.pyplot(plot.vind(vind_df))
        st.download_button(
            "Last ned vinddata",
            vind_df.to_csv().encode("utf-8"),
            "vinddata.csv",
            "text/csv",
            key="download-csv-vind",
        )
        plt.savefig(f'Klimaoversikt_{lokalitet}.pdf')
        with open(f"Klimaoversikt_{lokalitet}.pdf", "rb") as file:
            btn=st.download_button(
            label="Last ned PDF plot",
            data=file,
            file_name=f"Vindanalyse_for_{lokalitet}.pdf",
            mime="application/octet-stream"
        )

# st.write(
#     "Scriptet henter ned data frå NVE sitt Grid Time Series API, som er visualisert på xgeo.no"
# )
# st.write("Parametere som er brukt er: ")

#hardcoda inn kva parameter som er brukt
# parametere = {
#     "rr": "Døgnnedbør v2.0 - mm",
#     "tm": "Døgntemperatur v2.0	 - Celcius",
#     "sd": "Snødybde v2.0.1 - cm",
#     "fsw": "Nysnø siste døgn	 - mm",
#     "sdfsw3d": "Nysnødybde 3 døgn - cm",
#     "rrl": "Regn - mm",
#     "windDirection10m24h06": "Vindretning 10m døgn",
#     "windSpeed10m24h06": "Vindhastighet 10m døgn -  m/s",
# }
# st.json(parametere)
link = "[Skildring av tjenesten](https://klima-docs.readthedocs.io/)"
st.write(
    "Sjå link under for forklaring på dei forskjellige plot og dokumentasjon av web appen."
)
st.markdown(link, unsafe_allow_html=True)
st.write("Utvikla av Asplan Viak, v/Jan Helge Aalbu")

