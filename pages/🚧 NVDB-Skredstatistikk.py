import streamlit as st
import pandas as pd
import nvdbapiv3
import altair as alt
from shapely import wkt
import folium
from folium.plugins import Draw
import streamlit_folium
from streamlit_folium import st_folium
from io import BytesIO
from datetime import datetime
from nvdbskred.kartfunksjoner import kart, create_point_map
from nvdbskred.plotfunksjoner import plot, skred_type_counts, skred_type_by_month, style_function
import requests

st.set_page_config(page_title='NVDB skreddata', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

def feilmelding():
    st.write('Feil oppstått, mest truleg feil vegreferanse. Prøv igjen med ny vegreferanse.')



@st.cache_data
def databehandling(filter):
    skred = nvdbapiv3.nvdbFagdata(445)
    skred.filter(filter)
    #st.write(f'Antall skredregisteringar på strekninga: {skred.statistikk()["antall"]} stk')
    #st.write(f'Total lengde registert for registerte skredhendingar: {int(skred.statistikk()["lengde"])} meter')
    df = pd.DataFrame.from_records(skred.to_records())
    df_utvalg = df[['Skred dato', 'Type skred', 'Volum av skredmasser på veg', 
                    'Stedsangivelse', 'Løsneområde', 'Værforhold på vegen', 'Blokkert veglengde', 
                    'geometri', 'vref']].copy() 
    df_utvalg.columns = df_utvalg.columns.str.replace(' ', '_')
    df_utvalg['Skred_dato'] = pd.to_datetime(df_utvalg['Skred_dato'], errors='coerce')
    return df_utvalg

def filter_df(df, losneomrade, fradato, tildato):
    filtered_df = df[(df['Skred_dato'] >= fradato) & 
                 (df['Skred_dato'] <= tildato) & 
                 (df['Løsneområde'].isin(losneomrade))]
    return filtered_df

def last_ned_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def nedlasting(df):
    return st.download_button(
                "Last ned skredpunkt",
                df.to_csv().encode("utf-8"),
                "skredpunkt.csv",
                "text/csv",
                key="download-csv",
            )


st.title('NVDB skreddata')
st.write('Henter data fra NVDB api v3, ved nedhenting av fylker og heile landet tek det ein del tid å hente data')
col_tid_fra, col_tid_til = st.columns(2)
with col_tid_fra:
    fradato = st.date_input('Fra dato', value=pd.to_datetime('2000-01-01'), min_value=pd.to_datetime('1900-01-01'), max_value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))
    fradato = str(fradato)
with col_tid_til:
    tildato = st.date_input('Til dato', value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')), min_value=pd.to_datetime('1900-01-01'), max_value=pd.to_datetime(datetime.today().strftime('%Y-%m-%d')))
    tildato = str(tildato)
losneomrade = st.multiselect(
    'Velg løsneområder',
    ['Fjell/dalside', 'Vegskjæring', 'Ur', 'Inne i tunnel', 'Tunnelmunning (historisk)'],
    ['Fjell/dalside', 'Vegskjæring'])

karttype = None
col_uttak, col_kart = st.columns(2)
with col_uttak:
    utvalg = st.radio('Velg utaksmåte', ['Veg', 'Vegreferanse', 'Landsdekkande', 'Fylke', 'Kontraktsområde'])
with col_kart:
    vis_kart = st.checkbox('Vis kart')
    if vis_kart:
        karttype = st.radio('Vis kart med linjer eller punkter', ['Linjer', 'Punkter'])
        st.write('OBS! Punkter gir senterpunkt av linjene')
st.divider()


if utvalg == 'Fylke':
    st.write('OBS! Kan ta lang tid å hente data')
    fylke = st.selectbox(
    'Velg fylke',
    ('Agder', 'Innlandet', 'Møre og Romsdal', 'Nordland',  'Oslo', 'Rogaland', 'Troms og Finnmark', 'Trøndelag',  'Vestfold og Telemark', 'Vestland', 'Viken'))
    #vegtype = st.multiselect(
    #'Velg vegtype',
    #['Ev', 'Rv', 'Fv'],
    #['Ev', 'Rv', 'Fv'])

    vegreferanse = st.text_input('Videre filtrering på vegreferanse, f.eks Fv, Ev, Rv, eller spesifikk veg som Rv13, eller delstrekning som Rv5 S8D1', '')
    fylker = {
    "Agder": "42",
    "Innlandet": "34",
    "Møre og Romsdal": "15",
    "Nordland": "18",
    "Oslo": "03",
    "Rogaland": "11",
    "Troms og Finnmark": "54",
    "Trøndelag": "50",
    "Vestfold": "38",
    "Vestland": "46",
    "Viken": "30"
    }

    if st.button('Hent skreddata'):
        try:
            if vegreferanse == '':
                filter = {'fylke': fylker[fylke]}
            else:   
                filter = {'fylke': fylker[fylke], 'vegsystemreferanse': vegreferanse}
            df_data = databehandling(filter)
            df = filter_df(df_data, losneomrade, fradato, tildato)

            st.altair_chart(plot(df), use_container_width=True)
            st.altair_chart(skred_type_counts(df), use_container_width=True)
            st.altair_chart(skred_type_by_month(df), use_container_width=True)
            if karttype == 'Punkter':
                streamlit_folium.folium_static(create_point_map(df))
            if karttype == 'Linjer':
                kart(df)
        except ValueError:
            st.write('Feil oppstått, mest truleg feil vegreferanse. Prøv igjen med ny vegreferanse.')
        except KeyError:
            st.write('Ingen skredpunkt funnet på strekninga, eller ingen gyldig strekning.')

if utvalg == 'Landsdekkande':
    st.write('OBS! Tar lang tid å hente data')

    if st.button('Hent skreddata'):
        try:
            filter = {}
            df_data = databehandling(filter)
            df_utvalg = filter_df(df_data, losneomrade, fradato, tildato)
            st.download_button(
                "Last ned skredpunkt",
                df_utvalg.to_csv().encode("utf-8"),
                "skredpunkt.csv",
                "text/csv",
                key="download-csv",
            )
            st.altair_chart(plot(df_utvalg), use_container_width=True)
            st.altair_chart(skred_type_counts(df_utvalg), use_container_width=True)
            st.altair_chart(skred_type_by_month(df_utvalg), use_container_width=True)
            if karttype == 'Punkter':
                streamlit_folium.folium_static(create_point_map(df_utvalg))
            if karttype == 'Linjer':
                kart(df_utvalg)
        except ValueError:
            st.write('Feil med API kall, prøv igjen senere')

if utvalg == 'Veg':
 
    st.write('Eksempel: Rv5, Fv53, Ev39')
    st.write('Det går og an å gi inn Rv, Ev, eller Fv for alle skred på vegklassene.')
    vegreferanse = st.text_input('Vegreferanse', 'Rv5')

    if st.button('Hent skreddata'):
        try:
            filter = {'vegsystemreferanse' : vegreferanse}
            df_data = databehandling(filter)
            df_utvalg = filter_df(df_data, losneomrade, fradato, tildato)
            st.download_button(
                "Last ned skredpunkt",
                df_utvalg.to_csv().encode("utf-8"),
                "skredpunkt.csv",
                "text/csv",
                key="download-csv",
            )
            st.altair_chart(plot(df_utvalg), use_container_width=True)
            st.altair_chart(skred_type_counts(df_utvalg), use_container_width=True)
            st.altair_chart(skred_type_by_month(df_utvalg), use_container_width=True)

            if karttype == 'Punkter':
                streamlit_folium.folium_static(create_point_map(df_utvalg))
            if karttype == 'Linjer':
                kart(df_utvalg)
        except ValueError:
            feilmelding()


if utvalg == 'Vegreferanse':
    st.write('Her går det an å gi inn vegreferanse for å hente ut skredpunkt for delstrekning, og meterverdi.')
    vegnummer = st.text_input('Vegnummer', 'Rv5')
    col1, col2 = st.columns(2)
    with col1:
        delstrekning_fra = st.number_input('Delstrekning fra (S1D1 = 1)', 1)
        delstrekning_til = st.number_input('Delstrekning til (S8D1 = 8)', 8)
    with col2:
        meterverdi_fra = st.number_input('Meterverdi fra', value=0)
        meterverdi_til = st.number_input('Meterverdi til', value=20000, min_value=0)
    vegreferanse = f'{vegnummer}S{delstrekning_fra}-{delstrekning_til}'

    

    if st.button('Hent skreddata'):
        try:
            filter = {'vegsystemreferanse' : vegreferanse}
            df_data = databehandling(filter)
            df_utvalg = filter_df(df_data, losneomrade, fradato, tildato)
            
            
            # Extract segment as int
            df_utvalg['segment'] = df_utvalg['vref'].str.extract(r'S(\d+)D\d+').astype(int)
            df_utvalg[['start_distance', 'end_distance']] = df_utvalg['vref'].str.extract(r'm(\d+)-(\d+)')

            # Convert the extracted distances to int
            df_utvalg['start_distance'] = df_utvalg['start_distance'].astype(int)
            df_utvalg['end_distance'] = df_utvalg['end_distance'].astype(int)

            #Filtrerer ut for å få delstrekning basert på meterverdier
            condition1 = (df_utvalg['segment'] == delstrekning_fra) & (df_utvalg['start_distance'] >= meterverdi_fra)
            condition2 = (df_utvalg['segment'] > delstrekning_fra) & (df_utvalg['segment'] < delstrekning_til)
            condition3 = (df_utvalg['segment'] == delstrekning_til) & (df_utvalg['end_distance'] <= meterverdi_til)

            filtered_df = df_utvalg[condition1 | condition2 | condition3]
            #st.write(filtered_df)

            nedlasting(filtered_df)

            st.altair_chart(plot(filtered_df), use_container_width=True)
            st.altair_chart(skred_type_counts(filtered_df), use_container_width=True)
            st.altair_chart(skred_type_by_month(filtered_df), use_container_width=True)

            if karttype == 'Punkter':
                streamlit_folium.folium_static(create_point_map(filtered_df))
            if karttype == 'Linjer':
                kart(filtered_df)
        except ValueError:
            feilmelding()
        except KeyError:
            st.write('Ingen skredpunkt funnet på strekninga, eller ingen gyldig strekning.')
    
if utvalg == 'Kontraktsområde':
    st.write('Ikkje implementert enda')

st.write('For spørsmål eller tilbakemelding kontakt: jan.helge.aalbu@vegvesen.no')
