import nvdbapiv3
import streamlit as st
import requests
from io import BytesIO
import json
from shapely import wkt
import pandas as pd


@st.cache_data
def hent_data(filter):

    skred = nvdbapiv3.nvdbFagdata(445)
    skred.filter(filter)
    #st.write(f'Antall skredregisteringar på strekninga: {skred.statistikk()["antall"]} stk')
    #st.write(f'Total lengde registert for registerte skredhendingar: {int(skred.statistikk()["lengde"])} meter')
    df = pd.DataFrame.from_records(skred.to_records())
    df = df[['Skred dato', 'Type skred', 'Volum av skredmasser på veg', 
                    'Stedsangivelse', 'Løsneområde', 'Værforhold på vegen', 'Blokkert veglengde', 
                    'geometri', 'vref']].copy() 
    df.columns = df.columns.str.replace(' ', '_')
    df['Skred_dato'] = pd.to_datetime(df['Skred_dato'], errors='coerce')

    return df

def filter_df(df, losneomrade, fradato, tildato):
    #fradato = pd.to_datetime(fradato)
    #tildato = pd.to_datetime(tildato)

    df = df[(df['Skred_dato'] >= fradato) & 
                 (df['Skred_dato'] <= tildato) & 
                 ((df['Løsneområde'].isin(losneomrade)) | (df['Løsneområde'].isnull()))]

    return df

def last_ned_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache_data
def kontraktsfunksjon():
    r = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/omrader/kontraktsomrader')
    data = r.json()
    return data

def nedlasting(df):
    return st.download_button(
                "Last ned skredpunkt",
                df.to_csv().encode("utf-8"),
                "skredpunkt.csv",
                "text/csv",
                key="download-csv",
            )

@st.cache_data
def vegref(nord, ost, maks_avstand=50, srid=4326):
    r = requests.get(f"https://nvdbapiles-v3.atlas.vegvesen.no/posisjon?lat={nord}&lon={ost}&maks_avstand={maks_avstand}&maks_antall=1&srid={srid}")
    data = r.json()
    print(json.dumps(data[0], indent=4))
    vegreferanse = {
        'kortform' : data[0]['vegsystemreferanse']['kortform'],
        'vegkategori' : data[0]['vegsystemreferanse']['vegsystem']['vegkategori'],
        'fase' : data[0]['vegsystemreferanse']['vegsystem']['fase'],
        'nummer' : data[0]['vegsystemreferanse']['vegsystem']['nummer'],
        'strekning' : data[0]['vegsystemreferanse']['strekning']['strekning'],
        'delstrekning' : data[0]['vegsystemreferanse']['strekning']['delstrekning'],
        'meter' : data[0]['vegsystemreferanse']['strekning']['meter']
    }
    return vegreferanse