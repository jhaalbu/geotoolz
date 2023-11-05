"""Streamlit profilvisning

Script, laget som ein webapp med Streamlit.
Leser inn CSV filer, henta inn frå Høydedata.no
Formatet er forventa å vere: X, Y, Z, M
Dårlig testa på andre oppløsninger enn 1m

TODO: Definere bedre funksjoner i egen modul for
å kunne bruke videre i f.eks GIS programvare
"""


import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.image as image

#TODO: Vise kart
#TODO: La bruker tegne på kart

st.set_page_config(layout="wide")

#Laster inn Asplan Viak logo for vannmerke i plot, usikker på valg av logostørrelse..
# with open('logo (Phone).png', 'rb') as file:
#     img = image.imread(file)

#FIXME: Blei vel omstendlig funksjon, burde nok bli delt opp i meir handterbar størrelse
def fargeplot(df, rutenettx, rutenetty, farger='Snøskred', aspect=1, tiltak=False, tiltak_plassering=0, femtenlinje=False, linjeverdi=1/15, meterverdi=0, retning='Mot venstre', justering=0, legend=True):
    """Funksjonen setter opp pyplot og plotter medst.plot()
    
    TODO: Berre returne fig og ax fra matplotlib og ta ut st.pyplot() fra funksjonen
    """

    xy = df[['M', 'Z']].to_numpy()
    #xy = xy.reshape(-1, 1, 2)
    segments = np.array([xy[:-1], xy[1:]]).transpose(1,0,2) 
    #segments = np.hstack([xy[:-1], xy[1:]])
    femten = ein_paa_femten(df, meterverdi, linjeverdi, retning, justering)
    tiltak_punkt = vis_tiltak(df, tiltak_plassering)

    dZ = df['Z'].diff().values[1:]  # difference in Z for each segment
    dM = df['M'].diff().values[1:]  # difference in M for each segment
    slopes = abs(np.degrees(np.arctan(dZ / dM)))

    #TODO: Ta ut fargemapping frå funksjonen
    if farger == 'Snøskred':
        cmap = ListedColormap(['grey', 'green', 'yellow', 'orange', 'orangered', 'red', 'darkred'])
        norm = BoundaryNorm([0, 27, 30, 35, 40, 45, 50, 90], cmap.N)
        legend_elements = [
                Line2D([0], [0], marker='o', color='w', label='0 - 27\N{DEGREE SIGN}',
                        markerfacecolor='grey', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='27-30\N{DEGREE SIGN}',
                        markerfacecolor='green', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='30-35\N{DEGREE SIGN}',
                        markerfacecolor='yellow', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='35-40\N{DEGREE SIGN}',
                        markerfacecolor='orange', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='40-45\N{DEGREE SIGN}',
                        markerfacecolor='orangered', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='45-50\N{DEGREE SIGN}',
                        markerfacecolor='darkred', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='50-90\N{DEGREE SIGN}',
                        markerfacecolor='black', markersize=15),
        ]
    if farger == 'Jordskred':
        cmap = ListedColormap(['grey', 'palegreen', 'green', 'greenyellow', 'orange', 'orangered', 'darkred'])
        norm = BoundaryNorm([0, 3, 10, 15, 25, 45, 50, 90], cmap.N)
        legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='0 - 3\N{DEGREE SIGN}',
                markerfacecolor='grey', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='3-10\N{DEGREE SIGN}',
                markerfacecolor='palegreen', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='10-15\N{DEGREE SIGN}',
                markerfacecolor='green', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='15-25\N{DEGREE SIGN}',
                markerfacecolor='greenyellow', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='25-45\N{DEGREE SIGN}',
                markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='45-50\N{DEGREE SIGN}',
                markerfacecolor='orangered', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='50-90\N{DEGREE SIGN}',
                markerfacecolor='darkred', markersize=15),
        ]
    if farger == 'Stabilitet':
        cmap = ListedColormap(['blue','aquamarine' , 'lime', 'green','yellow', 'orange', 'orangered', 'red', 'black']) #8
        norm = BoundaryNorm([0, 2.9, 3.8, 5.7, 14, 26.6, 33.7, 45, 63.4, 90], cmap.N) 
        legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='< 1:20',
                markerfacecolor='blue', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:20 - 1:15',
                markerfacecolor='aquamarine', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:15 - 1:10',
                markerfacecolor='lime', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:10 - 1:4',
                markerfacecolor='green', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:4 - 1:2',
                markerfacecolor='yellow', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:2 - 1:1.5',
                markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:1.5 - 1:1',
                markerfacecolor='orangered', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='> 1:1',
                markerfacecolor='red', markersize=15)
        ]

    #TODO: Gå vekk fra fastsatt bredde på plot?
    fig, ax = plt.subplots(figsize=(15,10))
    
    coll = LineCollection(segments, cmap=cmap, norm=norm)
    coll.set_array(slopes) 
    #coll.set_array(df.Vinkel)
    coll.set_linewidth(3)
    #fig.figimage(img, 100, 50, alpha=0.25)
    ax.add_collection(coll)
    ax.autoscale_view()

    #Lar bruker justere inn avstand mellom rutenettet
    ax.set_yticks(np.arange(0,df['Z'].max(),rutenetty))
    ax.set_xticks(np.arange(0,df['M'].max(),rutenettx))
    ax.grid(linestyle = '--', linewidth = 0.5)

    #TODO: Ta inn brukerstyrt labeling?
    ax.set_ylabel('Høyde (moh.)')
    ax.set_xlabel(f'Lengde (m) | Høgdeforhold: {aspect}:1')
    ax.set_aspect(aspect, 'box')

    #Brukes til å styre presentasjon av plotting
    høgdeforskjell = df['Z'].max() - df['Z'].min()
    ax.set_ylim(df['Z'].min() - høgdeforskjell/10, df['Z'].max() + høgdeforskjell/10)

    if tiltak:
        ax.scatter(tiltak_punkt[0], tiltak_punkt[1], marker='x', s=200, color='black', linewidths=3, zorder=10)
    if femtenlinje:
        ax.plot(femten[0], femten[1], color='green', label='1:15')
    if legend:
        ax.legend(handles=legend_elements, title='Helling')
    st.pyplot(fig)
    return

def vis_tiltak(df, meterverdi):
    """Henter ut M og Z verdi for plotting basert på M verdi"""
    radnr = df['M'].sub(meterverdi).abs().idxmin()
    M = float(df.iloc[radnr]['M'])
    Z = float(df.iloc[radnr]['Z'])
    return M, Z


def ein_paa_femten(df, meterverdi, linjeverdi=1/15, retning='Mot venstre', justering=0):
    """Lager lister (x verier, og y verdier) for 1:15 linje
    
    Tar utganspunkt i eit startpunkt, meterverdi, og retning
    Justering brukes for å senke startpunkt for linje under terreng
    """
    radnr = df['M'].sub(meterverdi).abs().idxmin()
    M = float(df.iloc[radnr]['M'])
    Z = float(df.iloc[radnr]['Z']) - justering
    M_max = float(df['M'].max())
    liste_x = []
    liste_y = []
    liste_x.append(M)
    liste_y.append(Z)
    if retning == 'Mot venstre':
        liste_x.append(0)
        liste_y.append(Z + M*(linjeverdi))
    if retning == 'Mot høgre':
        liste_x.append(M_max)
        liste_y.append(Z + (M_max-M)*(linjeverdi))
    
    return liste_x, liste_y
 
def terrengprofil(df, utjamning=False, opplosning=None):
    """Tar inn ein dataframe og regner ut hellinger og vinkler

    Dataframe må ha formatet, X, Y, Z, M
    Utjamning kan settes til True, men da må også oppløsning gis
    Denne 
    """
    if utjamning == True:
        df = df.groupby(np.arange(len(df))//opplosning).mean()
    
    #Rekner ut hellinger, litt uelegant utanfor pandas, men funker..
    z = df['Z'].tolist()
    m = df['M'].tolist()
    h = []
    
    for i in range(len(z)):
        h.append((z[i] - z[i -1])/(m[i] - m[i - 1])) 

    df['Helning'] = h
    df['Vinkel'] = abs(np.degrees(np.arctan(df['Helning'])))

    return df

def csv_bearbeiding(fil):
    '''Fikser fil med høydatada.no som levere både DTM og DOM'''
    df = pd.read_csv(uploaded_file, sep=';', skiprows=1)
    df = df.loc[: df[(df['X'] == 'Source: DOM1')].index[0] - 1, :]
    df = df.astype('float64')
    return df

st.header('Profilverktøy')
st.write('Leser csv filer fra profilverktøyet på Høydedata.no')

#FIXME: Eskalerte etter kvart, legge inn i ein main() funksjon?
uploaded_file = st.file_uploader("Choose a file")
tiltak = False
tiltak_plassering = 0
meterverdi = 0
retning = "Mot høgre"
justering = 0
femtenlinje = False
linjeverdi = 1/15

if uploaded_file is not None:

    df = csv_bearbeiding(uploaded_file)
    
    farge = st.sidebar.radio(
     "Kva fargar skal vises?",
     ('Snøskred', 'Jordskred', 'Stabilitet'))

    aspect = st.sidebar.slider('Endre vertikalskala', 1, 5, 1)

    ticky_space = round(df['Z'].max()/10, -1)
    if ticky_space == 0:
        ticky_space = 5
    tickx_space = round(df['M'].max()/10, -1)
    if tickx_space == 0:
        tickx_space = 1
    
    høgdeforskjell = df['Z'].max() - df['Z'].min()
    rutenetty = st.sidebar.slider('Avstand rutenett y', 5, 100, int(ticky_space), 5)
    rutenettx = st.sidebar.slider('Avstand rutenett x', 10, 100, int(tickx_space), 10)
    
    if farge == 'Stabilitet':
        femtenlinje = st.sidebar.checkbox("Vis linje for potensielt løsneområde")
        if femtenlinje:
            meterverdi = st.sidebar.number_input("Gi plassering av linje", 0)
            
            if meterverdi > float(df['M'].max()):
                meterverdi == df['M'].max() - 100
                
            justering = st.sidebar.number_input("Gi justering for line (0.25 x H)", 0)
            #linjeverdi = st.sidebar.slider("Gi helling for linje", 1/20, 1/1, 1/15, 0.01)
            linjeverdi = st.sidebar.number_input("Gi helling for linje",0.0, 1.0, 1/15, 0.01)
            st.sidebar.write(f'Forholdtall - 1/{round(1/linjeverdi)}')
            st.sidebar.write(f'Vinkel - {round(abs(np.degrees(np.arctan(linjeverdi))))}\N{DEGREE SIGN}')

            retning = st.sidebar.radio('Kva retning skal linje plottes?', ("Mot høgre", "Mot venstre"))

    tiltak = st.sidebar.checkbox("Vis tiltak")  
    if tiltak:
        tiltak_plassering = st.sidebar.number_input("Gi plassering for tiltak", 0)
        
    check = st.sidebar.checkbox("Jamn ut profil")
    tegnforklaring = st.sidebar.checkbox("Vis tegnforklaring", True)
    if check:
        utjamn = st.sidebar.slider('Kva oppløysing ynskjer du?', 1, 100, 10)
        df_plot = terrengprofil(df, True, utjamn)
    else:
        df_plot = terrengprofil(df)

        
    fargeplot(df_plot, rutenettx, rutenetty, farge, aspect, tiltak, tiltak_plassering, femtenlinje, linjeverdi, meterverdi, retning, justering, tegnforklaring)


