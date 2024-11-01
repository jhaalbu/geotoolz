"""Streamlit profilvisning

Script, laget som ein webapp med Streamlit.
Leser inn CSV filer, henta inn frå Høydedata.no
Formatet er forventa å vere: X, Y, Z, M
Dårlig testa på andre oppløsninger enn 1m

TODO: Definere bedre funksjoner i egen modul for
å kunne bruke videre i f.eks GIS programvare
"""

import requests
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.ticker as ticker
import matplotlib.image as image
from shapely.geometry import LineString
from pyproj import CRS
from pyproj import Transformer
import folium
from folium.plugins import Draw
import math
from shapely.geometry import MultiPoint, Point, LineString
from streamlit_folium import st_folium
import ezdxf
from io import BytesIO
import tempfile

#TODO: Vise kart
#TODO: La bruker tegne på kart

st.set_page_config(layout="wide")


def transformer(x, y):
    transformer = Transformer.from_crs(5973, 4326)
    trans_x, trans_y =  transformer.transform(x, y)
    return trans_x, trans_y

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
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        df[numeric_cols] = df[numeric_cols].groupby(np.arange(len(df))//opplosning).mean()
        #df = df.groupby(np.arange(len(df))//opplosning).mean()
    
    #Rekner ut hellinger, litt uelegant utanfor pandas, men funker..
    z = df['Z'].tolist()
    m = df['M'].tolist()
    h = []
    
    for i in range(len(z)):
        h.append((z[i] - z[i -1])/(m[i] - m[i - 1])) 

    df['Helning'] = h
    df['Vinkel'] = abs(np.degrees(np.arctan(df['Helning'])))

    return df

def profildf():
    return

def alfabeta(df_heile, losne):
    df = df_heile.iloc[losne:]
    df = df.reset_index(drop=True)
    df['M'] = range(0, len(df))
    p = np.poly1d(np.polyfit(df['M'], df['Z'], 5))
    df['tilpass'] = p(df['M'])
    z_tilpass = df['tilpass'].tolist()
    z = df['Z'].tolist()
    m = df['M'].tolist()
    h_tilpass = []
    for i in range(len(m)):
        h_tilpass.append((z_tilpass[i] - z_tilpass[i -1])/(m[i] - m[i - 1]))  
#Rekner ut hellinger, litt uelegant utanfor pandas, men funker..
    df['H_tilpass'] = h_tilpass
    df['deg_tilpass'] = np.degrees(df['H_tilpass'])
    df10 = df.loc[(df['deg_tilpass'] <= -9.8) & (df['deg_tilpass'] >= -10.2)]
    #Finner enkelpunktet på 10 grader
    value = -10 #Verdien som skal finnest
    mpos_10grad = abs(df['deg_tilpass'] - value).idxmin() #X-akse verdien, altså meterverdi langs skredbane
    #mpos_10grad = 1044
    zpos_10grad = df.loc[mpos_10grad, 'tilpass'] #Y-akse verdien, altså Z verdi (høgde) for 10 graders punkt
    maxzpos = df['Z'].max() #Finner største Z verdi, høgast i skredbane
    pos_topp = (0, df['tilpass'].max()) #Finner posisjonen til toppen av skredbane
    pos_10grad = (mpos_10grad, zpos_10grad) #Finner posisjonen til 10 graderspunkt
    m1 = pos_topp[0] 
    z1 = pos_topp[1]

    m2 = pos_10grad[0]
    z2 = pos_10grad[1]

    z = z2 - z1
    m = m2 - m1

    #Finner betavinkel
    beta = math.atan(z/m)
    beta_deg = math.degrees(beta)
    #Rekner ut alphavinkel
    alpha = -abs((0.96 * abs(beta_deg)) -1.4)
    alpha_rad = math.radians(alpha)
    print(f'alpha {alpha} beta {beta_deg}')
    #alpha_1sd = (0.96 * beta_deg) - 

    m_max = df['M'].max()
    temp_z = math.tan(alpha_rad) * m_max
    pos_max = (m_max, z1 - -temp_z)

    #Bruker Shapelybibliotek for å finne 
    first_line = LineString(np.column_stack((df['M'], df['tilpass'])))
    second_line = LineString(np.column_stack(([pos_topp[0], pos_max[0]], [pos_topp[1], pos_max[1]])))
    intersection = first_line.intersection(second_line)
    print(intersection)

    koordliste = [(p.x, p.y) for p in intersection.geoms]

    #koordliste = [(p.x, p.y) for p in intersection]
    print(koordliste)
    utlop = koordliste[-1]

    textstr = '\n'.join((
        r'$\alpha=%.f$' % (abs(round(alpha,1)), ),
        r'$\beta=%.f$' % (abs(round(beta_deg,1)), ),))

    fig, ax = plt.subplots(figsize=(15,10))
    ax.plot(df['M'], df['Z']) #Høgdeprofilet
    ax.scatter(df10['M'], df10['Z'], color='r', linewidth=1, label='Punkt med 10 grader helling') # 10 graders punkter
    ax.plot([pos_topp[0], pos_10grad[0]], [pos_topp[1], pos_10grad[1]], color='orange') #Beta 
    #ax.plot([pos_topp[0], pos_max[0]], [pos_topp[1], pos_max[1]])
    if isinstance(intersection, MultiPoint) or isinstance(intersection, Point):
        for p in koordliste:
            ax.plot([pos_topp[0], p[0]], [pos_topp[1], p[1]], color='red')
    elif isinstance(intersection, LineString):
        ax.plot(*intersection.xy, color='red')
    else:
        print(f"Unhandled geometry type: {type(intersection)}")
    ax.plot(df['M'], df['tilpass']) #Plotter regresjonslinje ax2 + bx + c
    ax.legend()
    ax.grid()
    loc = ticker.MultipleLocator(base=100.0)
    ax.xaxis.set_major_locator(loc)
    ax.yaxis.set_major_locator(loc)
    ax.axis('equal')
    ax.annotate("10 graders punkt", xy=(m2, z2),  xycoords='data',
                xytext=(-70, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3,rad=-0.2"))
    ax.annotate("Utløpslengde "+str(int(utlop[1]))+'m', xy=utlop,  xycoords='data',
                xytext=(70, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3,rad=-0.2"))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)


    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    return fig
    
def csv_bearbeiding(fil):
    '''Fikser fil med høydatada.no som levere både DTM og DOM'''
    try:
        df = pd.read_csv(uploaded_file, sep=';', skiprows=1)
        #df = df.loc[: df[(df['X'] == 'Source: DOM1')].index[0] - 1, :]
        df = df.astype('float64')
    except:
        st.write('Prøv å laste ned fil med berre terreng, og ikkje overlfate eller bathymetri')
    return df

def transform_coords(coords):
    transformer = Transformer.from_crs(4326, 25833)
    return [transformer.transform(lon, lat) for lat, lon in coords]

def interpolate_points_shapely(coords, distance_m=1):
    
    utm_coords = transform_coords(coords)
    #print(utm_coords)
    #st.write(coords)
    #print(utm_coords)
    line = LineString(utm_coords)
    st.write(f'Linjelengde: {round(line.length)}')
    num_points = int(line.length / distance_m)

    points = []
    for i in range(num_points + 1):
        point = line.interpolate(distance_m * i)
        points.append([point.x, point.y])  # Append the x and y coordinates as a list

    return points

def chunk_list(lst, chunk_size):
    """Yield successive chunks from lst of size chunk_size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def calculate_distance(row, prev_row):
    if prev_row is None:
        return 0
    return math.sqrt((row['x'] - prev_row['y']) ** 2 + (row['y'] - prev_row['y']) ** 2)

def create_dxf(df):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmpfile:
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        for index, row in df.iterrows():
            if index > 0:
                msp.add_line((df.iloc[index - 1]['M'], df.iloc[index - 1]['Z']), (row['M'], row['Z']))

        # Save DXF to the temporary file
        doc.saveas(tmpfile.name)

        # Read the file content into a BytesIO object
        tmpfile.seek(0)
        buffer = BytesIO(tmpfile.read())

    return buffer


@st.cache_data
def hent_hogder(koordiater, opplosning=1):
        points = interpolate_points_shapely(koordiater)
        df = pd.DataFrame()
        chunk_size = 50
        for chunk in chunk_list(points, chunk_size):
            r = requests.get(f'https://ws.geonorge.no/hoydedata/v1/punkt?koordsys=25833&punkter={chunk}&geojson=false')
            data = r.json()

            temp_df = pd.DataFrame(data['punkter'])
            df = pd.concat([df, temp_df], ignore_index=True)
        return df

st.header('Profilverktøy')
st.write('Henter terrengdata fra kartverket sitt API, eller csv filer fra profilverktøyet på Høydedata.no')
st.write('Ved bruk av kartverket sitt API blir best tilgjengelige ')

uploaded_file = None
ok_df = False
tiltak = False
tiltak_plassering = 0
meterverdi = 0
retning = "Mot høgre"
justering = 0
femtenlinje = False
linjeverdi = 1/15

profilinput = st.radio('Velg input', ('Kart', 'Filopplasting'))
#FIXME: Eskalerte etter kvart, legge inn i ein main() funksjon?

if profilinput == 'Filopplasting':
    uploaded_file = st.file_uploader("Choose a file")

elif profilinput == 'Kart':
    m = folium.Map(location=[62.14497, 9.404296], zoom_start=5)
    #Legger til norgeskart som bakgrunn
    folium.raster_layers.WmsTileLayer(
        url="https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}",
        name="Norgeskart",
        fmt="image/png",
        layers="topo4",
        attr='<a href="http://www.kartverket.no/">Kartverket</a>',
        transparent=True,
        overlay=True,
        control=True,
    ).add_to(m)
    draw = Draw(
    draw_options={
        'polyline': {'shapeOptions': {
                'color': '#0000FF',  # Change this to your desired color
            }
        },
        'polygon': False,
        'rectangle': False,
        'circle': False,
        'circlemarker': False,
        'marker': False
    }, position='topleft', filename='skredkart.geojson', export=True,
    )
    draw.add_to(m)

    # Litt knotete måte å hente ut koordinater fra Streamlit, kanskje bedre i nye versjoner av streamlit? Ev. litt bedre måte i rein javascript?

    output = st_folium(m, width=900, height=700)


    try:
        koordiater = output["all_drawings"][0]["geometry"]["coordinates"]
        df = hent_hogder(koordiater)




    # Add a new column for distances
        df['M'] = df.index
        df.columns = [col.upper() for col in df.columns]

        # Print or process the DataFrame
        #st.write(df)

        ok_df = True
        #r = requests.get('https://ws.geonorge.no/hoydedata/v1/punkt?koordsys=4258&punkter=[[11,60],[12,61]]&geojson=false')
        #data = r.json()
        #st.write(data)
        # try:
        #     pos1 = output["all_drawings"][0]["geometry"]["coordinates"]
        #     pos2 = output["all_drawings"][1]["geometry"]["coordinates"]
        #     st.write(pos1[0])
        #     st.write(output["all_drawings"][0]["geometry"]["coordinates"])
        #     st.write(output["all_drawings"][1]["geometry"]["coordinates"])
        # except:
        #     st.write('Velg profillinje')
    except TypeError:
        st.error('Du må tegne ei profillinje')

else:
    st.write('Velg input')

if uploaded_file is not None or ok_df is True:

    if uploaded_file:
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
    
    if farge == 'Snøskred':
        losne = st.number_input("Gi plassering for løsneområde", value=0, min_value=0, step=10)
        if st.button('Vis alfabeta'):
            fig = alfabeta(df, losne)
            st.pyplot(fig)



    if st.button('Lag dxf fil'):
        dxf_file = create_dxf(df)
        st.download_button(
            label="Last ned dxf fil",
            data=dxf_file,
            file_name="profil.dxf",
            mime="application/dxf"
        )
