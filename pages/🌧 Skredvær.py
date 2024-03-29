from matplotlib import pyplot as plt
import streamlit as st
from pyproj import CRS
from pyproj import Transformer
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime
import requests
import matplotlib.dates as mdates

def nve_api(lat, lon, startdato, sluttdato, para):
    """Henter data frå NVE api GridTimeSeries
    Args:
        lat (str): øst-vest koordinat (i UTM33)
        output er verdien i ei liste, men verdi per dag, typ ne
        lon (str): nord-sør koordinat (i UTM33)
        startdato (str): startdato for dataserien som hentes ned
        sluttdato (str): sluttdato for dataserien som hentes ned
        para (str): kva parameter som skal hentes ned f.eks rr for nedbør
        
    Returns:
        verdier (liste) : returnerer i liste med klimaverdier
        
    """
    print(f'inne i nve api funksjon lat{lat} lon {lon}')
    api = 'http://h-web02.nve.no:8080/api/'
    url = api + '/GridTimeSeries/' + str(lat) + '/' + str(lon) + '/' + str(startdato) + '/' + str(sluttdato) + '/' + para + '.json'
    r = requests.get(url)

    verdier = r.json()
    return verdier

def klima_dataframe3h(lat, lon, startdato, sluttdato, parametere):
    lon = int(float(lon.strip()))
    lat = int(float(lat.strip()))
    print(f'lat{lat} lon {lon}')
    parameterdict = {}
    for parameter in parametere:
        print(f'inne i loop lat{lat} lon {lon}')
        api_svar = nve_api(lat, lon, startdato, sluttdato, parameter)
        print(api_svar)
        parameterdict[parameter] = api_svar['Data']
        altitude = api_svar['Altitude']
     
    df = pd.DataFrame(parameterdict)
    df = df.set_index(pd.date_range(
        datetime.datetime(int(startdato[0:4]), int(startdato[5:7]), int(startdato[8:10])),
        datetime.datetime(int(sluttdato[0:4]), int(sluttdato[5:7]), int(sluttdato[8:10])), freq='3h')
    )
    df[df > 1000] = 0
    return df, altitude

st.header('AV-Skredvær')
parameterliste_3h = ['rr3h', 'tm3h', 'windDirection10m3h', 'windSpeed10m3h']
transformer = Transformer.from_crs(4326, 5973)
m = folium.Map(location=[62.14497, 9.404296], zoom_start=5)
folium.raster_layers.WmsTileLayer(
    url='https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}',
    name='Norgeskart',
    fmt='image/png',
    layers='topo4',
    attr=u'<a href="http://www.kartverket.no/">Kartverket</a>',
    transparent=True,
    overlay=True,
    control=True,
    
).add_to(m)
m.add_child(folium.ClickForMarker(popup="Waypoint"))
#from folium.plugins import Draw
#Draw().add_to(m)
output = st_folium(m, width = 700, height=500)
utm_lat = 0
utm_lon = 0
st.write('Trykk i kartet, eller skriv inn koordinater for å velge klimapunkt.')


try:
    kart_kord_lat = output['last_clicked']['lat']
    kart_kord_lng = output['last_clicked']['lng']
    utm_ost, utm_nord = transformer.transform(kart_kord_lat, kart_kord_lng)
    utm_nord = round(utm_nord,2)
    utm_ost = round(utm_ost,2)

except TypeError:
    utm_nord  = 'Trykk i kart, eller skriv inn koordinat'
    utm_ost = 'Trykk i kart, eller skriv inn koordinat'


lat = st.text_input("NORD(UTM 33)", utm_nord)
lon = st.text_input("ØST  (UTM 33)", utm_ost)



start_3h_dato = st.date_input("Gi startdato (data fra 2010-01-01", datetime.date(2019, 7, 28))
antall_dager = st.text_input("Gi antall dager (fungerer best med intill 7 dager)", '5')

#start3h_dato = datetime.datetime(int(start_3h_dato[0:4]), int(start_3h_dato[5:7]), int(start_3h_dato[8:10]))

sluttdato_berekna = start_3h_dato + datetime.timedelta(days=int(antall_dager))

startdato_str = str(start_3h_dato)[0:10]
sluttdato_str = str(sluttdato_berekna)[0:10]
print(start_3h_dato)
print(sluttdato_str)
print(utm_nord, utm_ost)

knapp = st.button('Vis plott')

if knapp:
    df, altitude = klima_dataframe3h(lon, lat, startdato_str, sluttdato_str, parameterliste_3h)
    df['rr3h_cumsum'] = df['rr3h'].cumsum()
    max_cum_precip_idx = df['rr3h_cumsum'].idxmax()
    max_cum_precip_value = round(df['rr3h_cumsum'].max())

    #st.dataframe(df)
    fig = plt.figure(figsize=(15,8)) 
    ax1 = fig.add_subplot(111)
    ax1.set_title('Værdata - 3timer nedbør og temperatur')
    ax1.bar(df.index,  df['rr3h'], width=0.100, label='3t Nedbør')
    ax1.set_xlabel('Tidspunkt')
    ax1.set_ylabel('Nedbør (mm)')
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))   
    ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=90, ha='right')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M')) 

    ax2 = ax1.twinx()
    ax2.plot(df.index, df['tm3h'], 'r', label='Temperatur ')
    ax2.set_ylabel('Temperatur (\u00B0C)')

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.05))
    ax3.plot(df.index, df['rr3h_cumsum'], 'g', label='Kumulert nedbør')
    ax3.set_ylabel('Kumulert nedbør (mm)')
    ax3.annotate(f'Max kumulert nedbør: {max_cum_precip_value} mm', 
             xy=(max_cum_precip_idx, max_cum_precip_value),
             xytext=(max_cum_precip_idx, max_cum_precip_value + 0.1), # slight offset
             arrowprops=dict(facecolor='black', shrink=0.05),
             horizontalalignment='right')

    ax1.legend(loc='upper left')
    ax2.legend(loc='lower left')
    ax3.legend(loc='upper right')
    st.pyplot(fig)