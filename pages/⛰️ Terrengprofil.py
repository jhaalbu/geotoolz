"""Streamlit profilvisning

Script, laga som ein webapp med Streamlit.
Leser inn CSV/TXT-filer frå Høydedata.no (med fleire "Source:"-seksjonar)
eller hentar terrengpunkt frå Kartverket sitt høgde-API.

Forventa format i filseksjonar:
Source: <navn>
X;Y;Z;M
...

Endringar samla i ÉI FIL:
- Robust filparser (les_hoydedata_fra_fil) som støttar fleire "Source:"-blokker.
- Fjerna csv_bearbeiding(), erstatta med parseren over.
- Fiksa helnings/vinkel-bergning (unngår wrap-around, NaN for første segment).
- Sikra berekning ved dM==0 og NaN/inf-handtering i fargeplot.
- Fiksa calculate_distance() og gjort det tolerant for både X/Y og x/y.
- Korrigert koordinattransformasjon (always_xy=True) for lon/lat → UTM (EPSG:25833).
- Små ryddefiksar, validering og kommentarar.

TODO: Vurdere splitting i eigne moduler ved behov.
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
from shapely.geometry import LineString, MultiPoint, Point
from pyproj import Transformer
import folium
from folium.plugins import Draw
import math
from streamlit_folium import st_folium
import ezdxf
from io import BytesIO, StringIO
import tempfile

st.set_page_config(layout="wide")

# ------------------------------
# Hjelpefunksjonar
# ------------------------------

def transformer(x, y):
    """Transformerer frå EPSG:5973 → EPSG:4326 (henta frå originalen).
    NB: Denne er ikkje brukt andre stader i skriptet no, men blir bevart.
    """
    tr = Transformer.from_crs(5973, 4326, always_xy=True)
    lon, lat = tr.transform(x, y)
    return lon, lat


def les_hoydedata_fra_fil(file_like) -> dict:
    """Leser Høydedata-profilfil med fleire 'Source:'-seksjonar og returnerer
    ein dict: {'dtm': df, 'dom': df, 'dtm_topobathy': df, ...}

    Godtek både bytes og tekst. Kolonner blir tvangskonvertert til numerisk X,Y,Z,M.
    Linjer utan tabell blir hoppa over.
    """
    raw = file_like.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='replace')

    lines = raw.splitlines()
    seksjonar = {}
    name = None
    buff = []

    def flush(_name, _buff):
        if not _name or not _buff:
            return
        # Finn tabellstart
        start_idx = None
        for i, ln in enumerate(_buff):
            if ln.strip().upper().startswith('X;Y;Z;M'):
                start_idx = i
                break
        if start_idx is None:
            return
        block = "\n".join(_buff[start_idx:])  # inkluder header
        df = pd.read_csv(StringIO(block), sep=';', engine='python')
        # Sikre riktige datatypar
        for c in ['X', 'Y', 'Z', 'M']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['X', 'Y', 'Z', 'M']).reset_index(drop=True)
        seksjonar[_name.lower()] = df

    for ln in lines:
        if ln.strip().lower().startswith('source:'):
            flush(name, buff)
            name = ln.split(':', 1)[1].strip()
            buff = []
        else:
            buff.append(ln)
    flush(name, buff)  # siste seksjon

    return seksjonar


def transform_coords(coords_lonlat):
    """Transformerer liste av (lon, lat) i EPSG:4326 til (x, y) i EPSG:25833.
    returnerer liste [(x, y), ...].
    """
    tr = Transformer.from_crs(4326, 25833, always_xy=True)
    return [tr.transform(lon, lat) for lon, lat in coords_lonlat]


def interpolate_points_shapely(coords_lonlat, distance_m=1):
    """Interpolate punkt kvar 'distance_m' meter langs polyline i lon/lat.
    Returnerer liste med UTM-punkt [(x, y), ...] i EPSG:25833.
    """
    utm_coords = transform_coords(coords_lonlat)
    line = LineString(utm_coords)
    st.write(f'Linjelengde: {round(line.length)} m')
    num_points = int(line.length / distance_m)

    points = []
    for i in range(num_points + 1):
        p = line.interpolate(distance_m * i)
        points.append([p.x, p.y])
    return points


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def calculate_distance(row, prev_row):
    """Euklidsk distanse mellom to rader. Tolerant for X/Y eller x/y."""
    if prev_row is None:
        return 0.0
    x1 = row.get('X', row.get('x'))
    y1 = row.get('Y', row.get('y'))
    x0 = prev_row.get('X', prev_row.get('x'))
    y0 = prev_row.get('Y', prev_row.get('y'))
    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


@st.cache_data
def hent_hogder(coords_lonlat, opplosning=1):
    """Hentar høgder frå Kartverket sitt API for polyline i lon/lat.
    Returnerer DataFrame med kolonnene X, Y, Z, M.
    """
    points = interpolate_points_shapely(coords_lonlat)
    df = pd.DataFrame()
    chunk_size = 50
    for chunk in chunk_list(points, chunk_size):
        r = requests.get(
            'https://ws.geonorge.no/hoydedata/v1/punkt',
            params={
                'koordsys': '25833',
                'punkter': chunk,
                'geojson': 'false'
            },
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        temp_df = pd.DataFrame(data['punkter'])
        df = pd.concat([df, temp_df], ignore_index=True)

    # Normaliser kolonnenamn til versalar og legg til M som løpande meterposisjon
    df.columns = [c.upper() for c in df.columns]
    df['M'] = df.index.astype(float)
    return df[['X', 'Y', 'Z', 'M']]


# ------------------------------
# Profilberekning og plotting
# ------------------------------

def terrengprofil(df, utjamning=False, opplosning=None):
    """Rekn ut helning og vinkel per segment. Returnerer ny DF.

    - df må innehalde kolonnene X, Y, Z, M
    - utjamning/oppløysing: enkel blokk-gjennomsnitt på numeriske kolonner
    """
    df = df.copy()

    if utjamning:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        # Gruppér per blokk og ta mean, resett indeks
        grouped = df[numeric_cols].groupby(np.arange(len(df)) // int(opplosning)).mean()
        df = grouped.reset_index(drop=True)

    Z = df['Z'].to_numpy()
    M = df['M'].to_numpy()

    dZ = np.diff(Z)
    dM = np.diff(M)

    # Unngå deling på 0
    with np.errstate(divide='ignore', invalid='ignore'):
        helning = np.divide(dZ, dM)
        vinkel = np.degrees(np.arctan(np.abs(helning)))

    # Første rad har ikkje segment
    df['Helning'] = np.r_[np.nan, helning]
    df['Vinkel'] = np.r_[np.nan, vinkel]

    return df


def vis_tiltak(df, meterverdi):
    """Finn nærmaste M-verdi og returner (M, Z) for plotting."""
    radnr = df['M'].sub(meterverdi).abs().idxmin()
    M = float(df.iloc[radnr]['M'])
    Z = float(df.iloc[radnr]['Z'])
    return M, Z


def ein_paa_femten(df, meterverdi, linjeverdi=1/15, retning='Mot venstre', justering=0):
    """Lager koordinatlister for linje med gitt stigning (t.d. 1:15)."""
    radnr = df['M'].sub(meterverdi).abs().idxmin()
    M0 = float(df.iloc[radnr]['M'])
    Z0 = float(df.iloc[radnr]['Z']) - justering
    M_max = float(df['M'].max())
    xs = [M0]
    ys = [Z0]
    if retning == 'Mot venstre':
        xs.append(0)
        ys.append(Z0 + M0 * (linjeverdi))
    else:  # Mot høgre
        xs.append(M_max)
        ys.append(Z0 + (M_max - M0) * (linjeverdi))
    return xs, ys


def fargeplot(df, rutenettx, rutenetty, farger='Snøskred', aspect=1, tiltak=False,
              tiltak_plassering=0, femtenlinje=False, linjeverdi=1/15,
              meterverdi=0, retning='Mot venstre', justering=0, legend=True):
    """Set opp matplotlib-plot og viser med st.pyplot()."""
    xy = df[['M', 'Z']].to_numpy()
    segments = np.array([xy[:-1], xy[1:]]).transpose(1, 0, 2)

    # Hent fargekartar og legend
    if farger == 'Snøskred':
        cmap = ListedColormap(['grey', 'green', 'yellow', 'orange', 'orangered', 'red', 'black'])
        norm = BoundaryNorm([0, 27, 30, 35, 40, 45, 50, 90], cmap.N)
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='0–27°', markerfacecolor='grey', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='27–30°', markerfacecolor='green', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='30–35°', markerfacecolor='yellow', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='35–40°', markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='40–45°', markerfacecolor='orangered', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='45–50°', markerfacecolor='red', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='50–90°', markerfacecolor='black', markersize=15),
        ]
    elif farger == 'Jordskred':
        cmap = ListedColormap(['grey', 'palegreen', 'green', 'greenyellow', 'orange', 'orangered', 'darkred'])
        norm = BoundaryNorm([0, 3, 10, 15, 25, 45, 50, 90], cmap.N)
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='0–3°', markerfacecolor='grey', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='3–10°', markerfacecolor='palegreen', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='10–15°', markerfacecolor='green', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='15–25°', markerfacecolor='greenyellow', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='25–45°', markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='45–50°', markerfacecolor='orangered', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='50–90°', markerfacecolor='darkred', markersize=15),
        ]
    else:  # Stabilitet
        cmap = ListedColormap(['blue', 'aquamarine', 'lime', 'green', 'yellow', 'orange', 'orangered', 'red', 'black'])
        norm = BoundaryNorm([0, 2.9, 3.8, 5.7, 14, 26.6, 33.7, 45, 63.4, 90], cmap.N)
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='< 1:20', markerfacecolor='blue', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:20–1:15', markerfacecolor='aquamarine', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:15–1:10', markerfacecolor='lime', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:10–1:4', markerfacecolor='green', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:4–1:2', markerfacecolor='yellow', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:2–1:1.5', markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='1:1.5–1:1', markerfacecolor='orangered', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='> 1:1', markerfacecolor='red', markersize=15),
        ]

    # Segmentfargar etter vinkel (berekna frå df['Vinkel'])
    vinkel = df['Vinkel'].to_numpy()
    # Erstatt NaN/inf
    vinkel = np.nan_to_num(vinkel, nan=0.0, posinf=90.0, neginf=90.0)

    fig, ax = plt.subplots(figsize=(15, 10))
    coll = LineCollection(segments, cmap=cmap, norm=norm)
    coll.set_array(vinkel[1:])  # 1: for å matche segmenta
    coll.set_linewidth(3)
    ax.add_collection(coll)
    ax.autoscale_view()

    # Rutenett
    ax.set_yticks(np.arange(0, df['Z'].max(), rutenetty))
    ax.set_xticks(np.arange(0, df['M'].max(), rutenettx))
    ax.grid(linestyle='--', linewidth=0.5)

    ax.set_ylabel('Høgde (moh)')
    ax.set_xlabel(f'Lengde (m) | Høgdeforhold: {aspect}:1')
    ax.set_aspect(aspect, 'box')

    # Margin oppe/nede
    hogdeforskjell = df['Z'].max() - df['Z'].min()
    ax.set_ylim(df['Z'].min() - hogdeforskjell/10, df['Z'].max() + hogdeforskjell/10)

    if tiltak:
        tM, tZ = vis_tiltak(df, tiltak_plassering)
        ax.scatter(tM, tZ, marker='x', s=200, color='black', linewidths=3, zorder=10)
    if femtenlinje:
        xs, ys = ein_paa_femten(df, meterverdi, linjeverdi, retning, justering)
        ax.plot(xs, ys, color='green', label='1:15')
    if legend:
        ax.legend(handles=legend_elements, title='Helling')

    st.pyplot(fig)


def alfabeta(df_heile, losne):
    """Skisserer alfa/beta etter enkel polynomtilpassing frå losne-indeks."""
    df = df_heile.iloc[losne:].reset_index(drop=True).copy()
    df['M'] = range(0, len(df))
    p = np.poly1d(np.polyfit(df['M'], df['Z'], 5))
    df['tilpass'] = p(df['M'])

    z_tilpass = df['tilpass'].to_numpy()
    z = df['Z'].to_numpy()
    m = df['M'].to_numpy()

    # Derivert via differanse
    dZ = np.diff(z_tilpass)
    dM = np.diff(m)
    with np.errstate(divide='ignore', invalid='ignore'):
        h_tilpass = np.divide(dZ, dM)
    deg_tilpass = np.degrees(h_tilpass)  # NB: dette er tan^-1(h) normalt, men beheld original logikk

    df['H_tilpass'] = np.r_[np.nan, h_tilpass]
    df['deg_tilpass'] = np.r_[np.nan, deg_tilpass]

    # Nær 10°
    value = -10
    mpos_10grad = int(np.nanargmin(np.abs(df['deg_tilpass'] - value)))
    zpos_10grad = df.loc[mpos_10grad, 'tilpass']

    pos_topp = (0, float(df['tilpass'].max()))
    pos_10grad = (mpos_10grad, float(zpos_10grad))

    zdelta = pos_10grad[1] - pos_topp[1]
    mdelta = pos_10grad[0] - pos_topp[0]

    beta = math.atan2(zdelta, mdelta)
    beta_deg = math.degrees(beta)
    alpha = -abs((0.96 * abs(beta_deg)) - 1.4)
    alpha_rad = math.radians(alpha)

    m_max = float(df['M'].max())
    temp_z = math.tan(alpha_rad) * m_max
    pos_max = (m_max, pos_topp[1] - -temp_z)

    # Kryss med tilpassa profil
    first_line = LineString(np.column_stack((df['M'], df['tilpass'])))
    second_line = LineString(np.column_stack(([pos_topp[0], pos_max[0]], [pos_topp[1], pos_max[1]])))
    intersection = first_line.intersection(second_line)

    if isinstance(intersection, (MultiPoint, Point)):
        koordliste = [(p.x, p.y) for p in (intersection.geoms if hasattr(intersection, 'geoms') else [intersection])]
        utlop = koordliste[-1]
    elif isinstance(intersection, LineString):
        xs, ys = intersection.xy
        utlop = (xs[-1], ys[-1])
    else:
        utlop = (m_max, pos_max[1])

    textstr = '\n'.join((
        rf'$\\alpha={abs(round(alpha,1))}$',
        rf'$\\beta={abs(round(beta_deg,1))}$',
    ))

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.plot(df['M'], df['Z'], label='Høgdeprofil')
    df10 = df.loc[(df['deg_tilpass'] <= -9.8) & (df['deg_tilpass'] >= -10.2)]
    if not df10.empty:
        ax.scatter(df10['M'], df10['Z'], label='~10° punkt', linewidth=1)
    ax.plot([pos_topp[0], pos_10grad[0]], [pos_topp[1], pos_10grad[1]], color='orange', label='Beta-linje')

    if isinstance(intersection, LineString):
        x_int, y_int = intersection.xy
        ax.plot(x_int, y_int, color='red', label='Alpha-linje')
    else:
        ax.plot([pos_topp[0], utlop[0]], [pos_topp[1], utlop[1]], color='red', label='Alpha-linje')

    ax.plot(df['M'], df['tilpass'], label='Regresjon (5. grad)')
    ax.legend()
    ax.grid()
    loc = ticker.MultipleLocator(base=100.0)
    ax.xaxis.set_major_locator(loc)
    ax.yaxis.set_major_locator(loc)
    ax.axis('equal')
    ax.annotate("10° punkt", xy=pos_10grad, xycoords='data',
                xytext=(-70, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"))
    ax.annotate("Utløpslengde " + str(int(utlop[1])) + ' m', xy=utlop, xycoords='data',
                xytext=(70, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    return fig


def create_dxf(df):
    """Lag enkel DXF av profil-linja i M–Z-plan og returner buffer for nedlasting."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmpfile:
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for index, row in df.iterrows():
            if index > 0:
                msp.add_line((df.iloc[index - 1]['M'], df.iloc[index - 1]['Z']), (row['M'], row['Z']))
        doc.saveas(tmpfile.name)
        tmpfile.seek(0)
        buffer = BytesIO(tmpfile.read())
    return buffer

# ------------------------------
# UI
# ------------------------------

st.header('Profilverktøy')
st.write('Hentar terrengdata frå Kartverket sitt API, eller CSV/TXT-filer frå profilverktøyet på Høydedata.no')

uploaded_file = None
ok_df = False

tilak = False  # (stavemåte i original: tiltak)
tiltak = False

tiltak_plassering = 0
meterverdi = 0
retning = "Mot høgre"
justering = 0
femtenlinje = False
linjeverdi = 1/15

profilinput = st.radio('Vel input', ('Kart', 'Filopplasting'))

# --- Filopplasting ---
if profilinput == 'Filopplasting':
    uploaded_file = st.file_uploader("Vel profilfil (.csv/.txt)", type=['csv', 'txt'])
    if uploaded_file is not None:
        seksjonar = les_hoydedata_fra_fil(uploaded_file)
        if not seksjonar:
            st.error("Klarte ikkje å lese seksjonar frå fila. Kontroller formatet.")
        else:
            # La brukaren velje seksjon
            valg = st.radio("Vel datasett", list(seksjonar.keys()))
            df = seksjonar[valg]
            ok_df = True

# --- Kart ---
elif profilinput == 'Kart':
    m = folium.Map(location=[62.14497, 9.404296], zoom_start=5)
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
            'polyline': {'shapeOptions': {'color': '#0000FF'}},
            'polygon': False,
            'rectangle': False,
            'circle': False,
            'circlemarker': False,
            'marker': False
        },
        position='topleft',
        filename='skredkart.geojson',
        export=True,
    )
    draw.add_to(m)

    output = st_folium(m, width=900, height=700)

    try:
        # Folium returnerer GeoJSON med koordinatar [lon, lat]
        coords_lonlat = output["all_drawings"][0]["geometry"]["coordinates"]
        # Kan vere nested med ekstra nivå: sikr at vi får ei flat liste
        if len(coords_lonlat) > 0 and isinstance(coords_lonlat[0][0], (list, tuple)):
            coords_lonlat = coords_lonlat[0]
        df = hent_hogder(coords_lonlat)
        ok_df = True
    except Exception:
        st.info('Teikn ei profillinje i kartet for å hente høgder.')

else:
    st.write('Vel input')

# ------------------------------
# Når vi har eit DF: vis verktøy
# ------------------------------
if ok_df:
    # Sidepanel
    farge = st.sidebar.radio("Kva fargar skal visast?", ('Snøskred', 'Jordskred', 'Stabilitet'))
    aspect = st.sidebar.slider('Endre vertikalskala', 1, 5, 1)

    ticky_space = round(max(df['Z'].max() / 10, 1), -1)
    if ticky_space == 0:
        ticky_space = 5
    tickx_space = round(max(df['M'].max() / 10, 1), -1)
    if tickx_space == 0:
        tickx_space = 1

    hogdeforskjell = df['Z'].max() - df['Z'].min()
    rutenetty = st.sidebar.slider('Avstand rutenett y', 5, 100, int(ticky_space), 5)
    rutenettx = st.sidebar.slider('Avstand rutenett x', 10, 100, int(tickx_space), 10)

    if farge == 'Stabilitet':
        femtenlinje = st.sidebar.checkbox("Vis linje for potensielt løsneområde")
        if femtenlinje:
            meterverdi = st.sidebar.number_input("Plassering av linje (M)", 0.0, float(df['M'].max()), 0.0)
            justering = st.sidebar.number_input("Justering (senk startpunkt, m)", 0.0, value=0.0)
            linjeverdi = st.sidebar.number_input("Helling (forholdstal)", 0.0, 1.0, 1/15, 0.01)
            st.sidebar.write(f'Forholdstal – 1/{round(1/linjeverdi) if linjeverdi>0 else "∞"}')
            vinkel_line = round(abs(np.degrees(np.arctan(linjeverdi)))) if linjeverdi>0 else 0
            st.sidebar.write(f'Vinkel – {vinkel_line}°')
            retning = st.sidebar.radio('Retning for linje', ("Mot høgre", "Mot venstre"))

    tiltak = st.sidebar.checkbox("Vis tiltak")
    if tiltak:
        tiltak_plassering = st.sidebar.number_input("Plassering for tiltak (M)", 0.0, float(df['M'].max()), 0.0)

    check = st.sidebar.checkbox("Jamn ut profil")
    tegnforklaring = st.sidebar.checkbox("Vis teiknforklaring", True)
    if check:
        utjamn = st.sidebar.slider('Oppløysing (blokkstorleik)', 1, 100, 10)
        df_plot = terrengprofil(df, True, utjamn)
    else:
        df_plot = terrengprofil(df)

    # Plot
    fargeplot(
        df_plot, rutenettx, rutenetty, farge, aspect, tiltak, tiltak_plassering,
        femtenlinje, linjeverdi, meterverdi, retning, justering, tegnforklaring
    )

    # Alfa-beta
    if farge == 'Snøskred':
        losne = st.number_input("Plassering for løsneområde (indeks frå 0)", value=0, min_value=0, step=10)
        if st.button('Vis alfa–beta'):
            fig = alfabeta(df, int(losne))
            st.pyplot(fig)

    # DXF
    if st.button('Lag DXF-fil'):
        dxf_file = create_dxf(df)
        st.download_button(
            label="Last ned DXF",
            data=dxf_file,
            file_name="profil.dxf",
            mime="application/dxf"
        )
