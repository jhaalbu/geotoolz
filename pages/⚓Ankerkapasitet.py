import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

st.title('Overslagsberegning av ankerkapasitet')

st.write('Basert på NVE sikringshåndbokmodul: Modul S0.001: Forankring av skredsikringskonstruksjoner, og SVV håndbok V220 kap. 11.6.4')


bergegenskaper = {
    "Granitt": {
        "Tyngdetetthet (kN/m³)": "25 - 28",
        "Trykkfasthet (MPa)": "90 - 170",
        "Heftfasthet (MPa)": 2.0
    },
    "Gabbro": {
        "Tyngdetetthet (kN/m³)": "27 - 31",
        "Trykkfasthet (MPa)": "18 - 250",
        "Heftfasthet (MPa)": 2.5
    },
    "Gneis": {
        "Tyngdetetthet (kN/m³)": "25 - 28",
        "Trykkfasthet (MPa)": "90 - 130",
        "Heftfasthet (MPa)": 1.5
    },
    "Kvartsitt": {
        "Tyngdetetthet (kN/m³)": "21 - 25",
        "Trykkfasthet (MPa)": "150 - 170",
        "Heftfasthet (MPa)": 2.5
    },
    "Sandstein": {
        "Tyngdetetthet (kN/m³)": "20 - 26",
        "Trykkfasthet (MPa)": "100 - 140",
        "Heftfasthet (MPa)": 1.2
    },
    "Kalkstein": {
        "Tyngdetetthet (kN/m³)": "25 - 28",
        "Trykkfasthet (MPa)": "70 - 100",
        "Heftfasthet (MPa)": 2.0
    },
    "Leirskifer": {
        "Tyngdetetthet (kN/m³)": "20 - 27",
        "Trykkfasthet (MPa)": "25 - 60",
        "Heftfasthet (MPa)": 0.5
    },
    "Fyllitt": {
        "Tyngdetetthet (kN/m³)": "20 - 27",
        "Trykkfasthet (MPa)": "25 - 60",
        "Heftfasthet (MPa)": 0.75
    }
}


bolt = {
    "M20x2.5": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 20,
        "Stigning (mm)": 2.5,
        "Stigningsdiameter (mm)": 16.93,
        "Minimumsdiameter (mm)": 18.38,
        "Spenningsareal (As) (mm²)": 244.8
    },
    "M22x2.5": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 22,
        "Stigning (mm)": 2.5,
        "Stigningsdiameter (mm)": 18.93,
        "Minimumsdiameter (mm)": 20.38,
        "Spenningsareal (As) (mm²)": 303.4
    },
    "M24x3.0": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 24,
        "Stigning (mm)": 3.0,
        "Stigningsdiameter (mm)": 20.32,
        "Minimumsdiameter (mm)": 22.05,
        "Spenningsareal (As) (mm²)": 352.5
    },
    "M27x3.0": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 27,
        "Stigning (mm)": 3.0,
        "Stigningsdiameter (mm)": 23.32,
        "Minimumsdiameter (mm)": 25.05,
        "Spenningsareal (As) (mm²)": 459.4
    },
    "M30x3.5": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 30,
        "Stigning (mm)": 3.5,
        "Stigningsdiameter (mm)": 25.71,
        "Minimumsdiameter (mm)": 27.73,
        "Spenningsareal (As) (mm²)": 560.6
    },
    "M33x3.5": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 33,
        "Stigning (mm)": 3.5,
        "Stigningsdiameter (mm)": 28.71,
        "Minimumsdiameter (mm)": 30.73,
        "Spenningsareal (As) (mm²)": 693.6
    },
    "M36x4.0": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 36,
        "Stigning (mm)": 4.0,
        "Stigningsdiameter (mm)": 31.09,
        "Minimumsdiameter (mm)": 33.40,
        "Spenningsareal (As) (mm²)": 816.7
    },
    "M39X4.0": {
        "Type" : 'Kamstål',
        "Største diameter (mm)": 39,
        "Stigning (mm)": 4.0,
        "Stigningsdiameter (mm)": 34.09,
        "Minimumsdiameter (mm)": 36.40,
        "Spenningsareal (As) (mm²)": 975.8
    },
        "TITAN 30/11": {
        "Type" : "TITAN",
        "Inst. kapasitet N_i": 198,
        "R_d iht. EC2": 222,
        "N_d iht. EC3": 220,
        "Nom. ytre diameter d_y [mm]": 30,
        "Nom. indre diameter d_i [mm]": 13,
        "Effektiv tverrsnittsareal A [mm^2]": 415,
        "Karak. flytelast R_k [kN]": 255,
        "Gjennomsn. bruddlast P_b [kN]": 326,
        "Aksialstivhet EA [10^3 kN]": 83,
        "Bøyningsstivhet EI [kNm^2]": 4.6,
        "Kjernediameter d_core [mm]": 24.6,
        "Treghetsmoment I_s [cm^4]": 1.66,
        "Motstandsmoment W [cm^3]": 1.35,
        "Plastisk motstandsmoment W_pl [cm^3]": 2.11,
        "Maksimal prøvelast P_p,max [kN]": 244,
        "Vekt per meter M [kg/m]": 3.3,
        "Lengde skjøtehylse d_s [mm]": 38,
        "Lengde skjøtehylse L_s [mm]": 105
    },
    "TITAN 40/20": {
        "Type" : "TITAN",
        "Inst. kapasitet N_i": 347,
        "R_d iht. EC2": 374,
        "N_d iht. EC3": 385,
        "Nom. ytre diameter d_y [mm]": 40,
        "Nom. indre diameter d_i [mm]": 20,
        "Effektiv tverrsnittsareal A [mm^2]": 730,
        "Karak. flytelast R_k [kN]": 430,
        "Gjennomsn. bruddlast P_b [kN]": 523,
        "Aksialstivhet EA [10^3 kN]": 135,
        "Bøyningsstivhet EI [kNm^2]": 8.1,
        "Kjernediameter d_core [mm]": 36.1,
        "Treghetsmoment I_s [cm^4]": 7.55,
        "Motstandsmoment W [cm^3]": 4.18,
        "Plastisk motstandsmoment W_pl [cm^3]": 6.51,
        "Maksimal prøvelast P_p,max [kN]": 428,
        "Vekt per meter M [kg/m]": 6.1,
        "Lengde skjøtehylse d_s [mm]": 57,
        "Lengde skjøtehylse L_s [mm]": 140
    },
    "TITAN 40/16": {
        "Type" : "TITAN",
        "Inst. kapasitet N_i": 418,
        "R_d iht. EC2": 461,
        "N_d iht. EC3": 464,
        "Nom. ytre diameter d_y [mm]": 40,
        "Nom. indre diameter d_i [mm]": 16,
        "Effektiv tverrsnittsareal A [mm^2]": 900,
        "Karak. flytelast R_k [kN]": 530,
        "Gjennomsn. bruddlast P_b [kN]": 673,
        "Aksialstivhet EA [10^3 kN]": 167,
        "Bøyningsstivhet EI [kNm^2]": 9.4,
        "Kjernediameter d_core [mm]": 36.1,
        "Treghetsmoment I_s [cm^4]": 8.02,
        "Motstandsmoment W [cm^3]": 4.44,
        "Plastisk motstandsmoment W_pl [cm^3]": 6.51,
        "Maksimal prøvelast P_p,max [kN]": 461,
        "Vekt per meter M [kg/m]": 7.2,
        "Lengde skjøtehylse d_s [mm]": 57,
        "Lengde skjøtehylse L_s [mm]": 140
    },
    "TITAN 52/29": {
        "Type" : "TITAN",
        "Inst. kapasitet N_i": 512,
        "R_d iht. EC2": 552,
        "N_d iht. EC3": 569,
        "Nom. ytre diameter d_y [mm]": 52,
        "Nom. indre diameter d_i [mm]": 29,
        "Effektiv tverrsnittsareal A [mm^2]": 1250,
        "Karak. flytelast R_k [kN]": 630,
        "Gjennomsn. bruddlast P_b [kN]": 899,
        "Aksialstivhet EA [10^3 kN]": 231,
        "Bøyningsstivhet EI [kNm^2]": 12.2,
        "Kjernediameter d_core [mm]": 45.9,
        "Treghetsmoment I_s [cm^4]": 13.82,
        "Motstandsmoment W [cm^3]": 8.44,
        "Plastisk motstandsmoment W_pl [cm^3]": 19.1,
        "Maksimal prøvelast P_p,max [kN]": 710,
        "Vekt per meter M [kg/m]": 10.5,
        "Lengde skjøtehylse d_s [mm]": 70,
        "Lengde skjøtehylse L_s [mm]": 160
    },
    "TITAN 52/26": {
        "Type" : "TITAN",
        "Inst. kapasitet N_i": 593,
        "R_d iht. EC2": 617,
        "N_d iht. EC3": 659,
        "Nom. ytre diameter d_y [mm]": 52,
        "Nom. indre diameter d_i [mm]": 26,
        "Effektiv tverrsnittsareal A [mm^2]": 1460,
        "Karak. flytelast R_k [kN]": 865,
        "Gjennomsn. bruddlast P_b [kN]": 1056,
        "Aksialstivhet EA [10^3 kN]": 272,
        "Bøyningsstivhet EI [kNm^2]": 13.8,
        "Kjernediameter d_core [mm]": 45.9,
        "Treghetsmoment I_s [cm^4]": 19.54,
        "Motstandsmoment W [cm^3]": 8.52,
        "Plastisk motstandsmoment W_pl [cm^3]": 23.14,
        "Maksimal prøvelast P_p,max [kN]": 824,
        "Vekt per meter M [kg/m]": 11.7,
        "Lengde skjøtehylse d_s [mm]": 70,
        "Lengde skjøtehylse L_s [mm]": 180
    },
    "R32/15": {
        "Type" : "Pretec",
        "Diameter" : 32,
        "Lengde (mm)": "L=3000, L=1500",
        "Min. Flytelast (kN)": 280,
        "Min. Bruddlast (kN)": 340,
        "Min. Skjærlast (kN)": 168,
        "Vekt (kg/m)": 4.1,
        "Min. Forlengelse % Agt": ">=5",
        "Spenningareal (mm2)": "460*",
        "Min. Slagseighet -20°C (J)": 40,
        "E-modul (GPa)": 210
    },
    "R38/19": {
        "Type" : "Pretec",
        "Diameter" : 38,
        "Lengde (mm)": "L=3000",
        "Min. Flytelast (kN)": 400,
        "Min. Bruddlast (kN)": 500,
        "Min. Skjærlast (kN)": 240,
        "Vekt (kg/m)": 5.5,
        "Min. Forlengelse % Agt": ">=5",
        "Spenningareal (mm2)": "670*",
        "Min. Slagseighet -20°C (J)": 40,
        "E-modul (GPa)": 210
    },
    "R51/26": {
        "Type" : "Pretec",
        "Diameter" : 51,
        "Lengde (mm)": "L=3000",
        "Min. Flytelast (kN)": 730,
        "Min. Bruddlast (kN)": 930,
        "Min. Skjærlast (kN)": 438,
        "Vekt (kg/m)": 10.2,
        "Min. Forlengelse % Agt": ">=5",
        "Spenningareal (mm2)": "1290*",
        "Min. Slagseighet -20°C (J)": 40,
        "E-modul (GPa)": 210
    }
}


heftfasthet_berg = {
    "Meget godt berg" : {
        "Heftfasthet" : 150,
        "Bruddvinkel" : 45
    },
    "To sprekkesett" : {
        "Heftfasthet" : 75,
        "Bruddvinkel" : 40
    },
    "Tre sprekkesett" : {
        "Heftfasthet" : 50,
        "Bruddvinkel" : 30
    }
}

reduksjonsfaktor_fa_dict = {
    'Midlertidig' : 0.9,
    'Permanent' : 0.6
}

#Variabler som ikkje blir endra
kt=0.9 #Eurokode 3, Del 5, NA. 7.2.3
gamma_m2 = 1.25 #Eurokode 3, Del5, NA 7.1
gamma_m0 = 1.05 #Eurokode 3, NA.5.1.1
gamma_heft = 1.25
gamma_acc = 1.1
heft_mørtel_stål = 2.4
# Display the selected rock's properties
stålegenskaper = {
    'bruddspenning' : 0.6,
    'flytspenning' : 0.5
}

def innstallert_kapasitet_kamstål(reduksjonsfaktor, flytspenning, bruddspenning, spenningsareal, diameter, kt, gamma_m2, gamma_m0):

    f_ttRd = round(kt * (spenningsareal) * (bruddspenning/gamma_m2),1)  #strekkapaistet gjengede del, bruddspenning
    f_tgRd = round((math.pi * (diameter/2)**2) * (flytspenning/gamma_m0),1)  # strekkakapsitet resten av bolt, flytspenning
    f_tRd = min(f_ttRd, f_tgRd)  # Minste av overliggande

    Ni = reduksjonsfaktor * f_tRd

    return Ni, f_tRd, f_ttRd, f_tgRd

def skjærkapasitet_kamstål(flytspenning, spenningsareal, gamma_m0):
    return flytspenning * (spenningsareal/(gamma_m0 * math.sqrt(3)))

def bøyningskapasitet_kamstål(flytspenning, diameter):
    return flytspenning * ((diameter**2)/4.5)

def innstallert_kapasitet_selvborende_stag(reduksjonsfaktor, dimensjonerende_kapasitet):
    return reduksjonsfaktor * dimensjonerende_kapasitet
    
def forankringslengde_stål_mørtel(forankringskraft, heft_mørtel_stål, diameter_bolt, gamma_heft):
    return round(forankringskraft / ((heft_mørtel_stål*gamma_heft) * (diameter_bolt) * math.pi),1)

def forankringslengde_mørtel_berg(forankringskraft, heft_mørtel_berg, hulldiameter, gamma_heft):
    return round(forankringskraft / ((heft_mørtel_berg/gamma_heft) * hulldiameter * math.pi),1)

def forankringslengde_stabilitet_berg(forankringskraft, bruddvinkel, heftfasthet_bruddplan, gamma_m_berg):
    return round(math.sqrt((gamma_m_berg * forankringskraft)/(heftfasthet_bruddplan * math.pi * math.tan(math.radians(bruddvinkel)))),1)



st.write('**Inndata anker**')
col1, col2 = st.columns(2)
with col1:
    bolttype = st.selectbox("Velg stag/bolt", list(bolt.keys()))
    reduksjonsfaktor = st.selectbox(rf'Reduksjonsfaktor', ['Permanent', 'Midlertidig'], help='Eurokode 7, Del 1, Tabell NA.A.A19: "Ved prosjektering av ankere skal det tas hensyn til at ujevne grunnforhold og installasjonsmetode kan redusere motstanden. Typiske reduksjonfaktorer for ankerets kapasitet er fra 0,6 til 0,9. Fra Byggegropsveiledningen Kapittel 7.6.4 står det at det for ankere er vanlig å benytte 0,9 for midlertidige og 0,6 for permanente ankere.')
    reduksjonsfaktor_fa = reduksjonsfaktor_fa_dict[reduksjonsfaktor]
    #bergart = st.selectbox("Velg bergart", list(bergegenskaper.keys()))
    
    forankringskraft = st.number_input("Gi forankringskraft i kN")
    hulldiameter = st.number_input("Gi hulldiameter (mm)", 0, 300, 51)
    


with col2:
    if bolt[bolttype]['Type']  == 'Kamstål':
        st.latex(rf'N_d = {round(bolt[bolttype]["Spenningsareal (As) (mm²)"])} mm²', help='Spenningsareal i gjengde del av bolt')
        st.latex(rf'A_g = {round((math.pi * ((bolt[bolttype]["Største diameter (mm)"]/2)**2)))} {{mm}}^2', help="Stangankerets brutto areal")
        #st.latex(rf'f_y = {stålegenskaper["flytspenning"]} MPa', help='Stålets flytspenning i MPa')
        #st.latex(rf'\gamma_{{M0,stål}} = {gamma_m0}', help='Partialfaktor for martialfasthet, Eurokode 3-5, NA.5.1.1')
        st.latex(rf'f_a = {reduksjonsfaktor_fa}', help='Reduksjonsfaktor avhengig om midlertidig eller permanent sikring, Hb V220 pkt.10.6.4.2')
    elif bolt[bolttype]['Type'] == 'TITAN':
        st.latex(rf'N_d = {round(bolt[bolttype]["N_d iht. EC3"])} kN', help='Fra produktdatablad: Dimensjonerende kapasitet etter EN 1993-1-1:2005; EN 1993-5:2007')
        st.latex(rf'f_a = {reduksjonsfaktor_fa}', help='Reduksjonsfaktor avhengig om midlertidig eller permanent sikring, Hb V220 pkt.10.6.4.2')

st.write('**Inndata grunn**')
col_1d, col_2d = st.columns(2)
with col_1d:
    undergrunn = st.selectbox('Velg berg eller løsmasse', ['Berg', 'Løsmasse'])
    if undergrunn == 'Berg':
        bergart = st.selectbox("Velg bergart", list(bergegenskaper.keys()))
        heftfasthetstype = st.selectbox("Velg bergkvalitet", list(heftfasthet_berg.keys()))
        gamma_m_berg = st.number_input("Gi partialfaktor for berg", 1.0, 3.0, 2.0, 0.1)

with col_2d:
    if undergrunn == 'Berg':
        st.latex(rf'\tau_{{k.mørtel.berg}} = {bergegenskaper[bergart]["Heftfasthet (MPa)"]} MPa')
        st.latex(rf'\psi = {heftfasthet_berg[heftfasthetstype]["Bruddvinkel"]} ^\circ')
        st.latex(rf'\tau_k = {heftfasthet_berg[heftfasthetstype]["Heftfasthet"]} kPa')
        st.latex(rf'\gamma_{{M.berg}} = {gamma_m_berg}')


st.header('Utrekninger')
st.subheader('Indre kapasitet')
if bolt[bolttype]['Type']  == 'Kamstål':
    Ni, f_tRd, f_ttRd, f_tgRd = innstallert_kapasitet_kamstål(reduksjonsfaktor_fa, stålegenskaper["flytspenning"], stålegenskaper["bruddspenning"],  bolt[bolttype]["Spenningsareal (As) (mm²)"], bolt[bolttype]["Største diameter (mm)"], kt, gamma_m2, gamma_m0)
    Pp = Ni * gamma_acc
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.write('Strekkapasitet etter EC3-5 pkt. 7.2.3')
        st.write('Kapaistet for gjengde del av anker:')
        st.latex(rf'F_{{tt,Rd}} = k_t \cdot A_s \cdot \frac{{f_{{ua}}}}{{\gamma_{{M2,stål}}}}  = {f_ttRd} kN')
        st.write('Kapasitet for øvrig del av anker')
        st.latex(rf'F_{{tg,Rd}} = A_g \cdot \frac{{f_y}}{{\gamma_{{M0,stål}}}} = {f_tgRd} kN')
        st.write('Indre installerte kapaistet er minste verdi av kapsiteter over')
        st.latex(rf'F_{{t,Rd}} = \min(F_{{tt,Rd}}, F_{{tg,Rd}}) = {f_tRd} kN')
 
    with col_b2:
        st.latex(rf'k_t = {kt}', help='Korreksjon for kjerv-virking av gjengene. Eurokode 3, del 5 NA.7.2.3')
        st.latex(rf'A_s = {round(bolt[bolttype]["Spenningsareal (As) (mm²)"])} mm²', help='Spenningsareal i gjengde del av bolt')
        st.latex(rf'f_{{ua}} = {stålegenskaper["bruddspenning"]} MPa', help='Stålets bruddspenning i MPa')
        st.latex(rf'\gamma_{{M2,stål}} = {gamma_m2}', help='Partialfaktor for materialfasthet, Eurokode 3-5, pkt. 7.1(4) / NA.7.1')
        st.latex(rf'A_g = {round((math.pi * ((bolt[bolttype]["Største diameter (mm)"]/2)**2)))} {{mm}}^2', help="Stangankerets brutto areal")
        st.latex(rf'f_y = {stålegenskaper["flytspenning"]} MPa', help='Stålets flytspenning i MPa')
        st.latex(rf'\gamma_{{M0,stål}} = {gamma_m0}', help='Partialfaktor for martialfasthet, Eurokode 3-5, NA.5.1.1')
        st.latex(rf'f_a = {reduksjonsfaktor_fa}', help='Reduksjonsfaktor avhengig om midlertidig eller permanent sikring, Hb V220 pkt.10.6.4.2')

    st.write("**Indre kapasitet er:**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write('Installert strekkapasitet')
        st.latex(rf'N_{{i.strekk.d}} = f_a \cdot F_{{t,Rd}} =  {round(Ni,1)} kN')
        st.write('Sjekk av strekkapsitet')
        st.latex(rf'E_{{ULS.d}} = {forankringskraft} kN')
        
        if Ni > forankringskraft:
            st.write(f'**:green[OK! Installert kapasitet er større eller lik dimensjonerende ankerlast.]**')
        else:
            st.write(f'**:red[OBS! Installert kapasitet er mindre enn dimensjonerende ankerlast. Velg større dimensjon]**')

        st.latex(rf'P_P = \gamma_{{a.acc}} \cdot E_{{ULS.d}} = {round(forankringskraft * 1.1,1)}')

        if Ni > forankringskraft*1.1:
            st.write(f'**:green[OK! Installert kapasitet er større eller lik prøvelast.]**')
        else:
            st.write(f'**:red[OBS! Installert kapasitet er mindre enn prøvelast. Velg større dimensjon.]**')
    with col_c2:
        st.latex(rf'\gamma_{{a.acc}} = 1.1', help="Partialfaktor for godkjennings-prøving [EC 7-1 pkt. 8.6.2]")



elif bolt[bolttype]['Type'] == 'TITAN':
    st.write('For selborende stag brukes flytelast og bruddlast gitt i produktdatablad')
    Ni = innstallert_kapasitet_selvborende_stag(reduksjonsfaktor_fa, bolt[bolttype]["N_d iht. EC3"])
    Pp = Ni * gamma_acc
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.write('Installert strekkapasitet')
        st.latex(rf'N_{{i.strekk.d}} = f_a \cdot F_{{t,Rd}} =  {round(Ni,1)} kN')
    with col_e2:
        st.latex(rf'N_d = {round(bolt[bolttype]["N_d iht. EC3"])} kN', help='Fra produktdatablad: Dimensjonerende kapasitet etter EN 1993-1-1:2005; EN 1993-5:2007')
        st.latex(rf'f_a = {reduksjonsfaktor_fa}', help='Reduksjonsfaktor avhengig om midlertidig eller permanent sikring, Hb V220 pkt.10.6.4.2')


elif bolt[bolttype]['Type'] == 'Pretec':
    st.write('For selborende stag brukes flytelast og bruddlast gitt i produktdatablad')
    Ni = innstallert_kapasitet_selvborende_stag(reduksjonsfaktor_fa, bolt[bolttype]["Min. Flytelast (kN)"])
    Pp = Ni * gamma_acc
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.write('Installert strekkapasitet')
        st.latex(rf'N_{{i.strekk.d}} = f_a \cdot F_{{t,Rd}} =  {round(Ni,1)} kN')
    with col_e2:
        st.latex(rf'N_d = {round(bolt[bolttype]["Min. Flytelast (kN)"])} kN', help='Fra produktdatablad')
        st.latex(rf'f_a = {reduksjonsfaktor_fa}', help='Reduksjonsfaktor avhengig om midlertidig eller permanent sikring, Hb V220 pkt.10.6.4.2')

st.subheader('Beregning av ytre kapasiteter i bruddgrense')

col_f1, col_f2 = st.columns(2)
if bolt[bolttype]['Type'] == 'Kamstål':
    boltediameter = bolt[bolttype]["Største diameter (mm)"]
elif bolt[bolttype]['Type'] == 'TITAN':
    boltediameter = bolt[bolttype]["Nom. ytre diameter d_y [mm]"]
elif bolt[bolttype]['Type'] == 'Pretec':
    boltediameter = bolt[bolttype]["Diameter"]
lengde_stål_mørtel = forankringslengde_stål_mørtel(Pp, heft_mørtel_stål, boltediameter, gamma_heft)
lengde_mørtel_berg = forankringslengde_mørtel_berg(Pp, bergegenskaper[bergart]["Heftfasthet (MPa)"], hulldiameter, gamma_heft)
lengde_berg = forankringslengde_stabilitet_berg(Pp, heftfasthet_berg[heftfasthetstype]['Bruddvinkel'], heftfasthet_berg[heftfasthetstype]['Heftfasthet'], gamma_m_berg)
    

with col_f1:
    st.write('Lengde for nødvendig forankringslengde for brudd mellom stål og mørtel:')
    st.latex(fr'L_{{tb.stål.mørtel}} = \frac{{P_p}}{{\tau_{{d;stål-mørtel}} \cdot d_s \cdot \pi}} = {lengde_stål_mørtel} m')
    st.write('Lengde for nødvendig forankringslengde for brudd mellom mørtel og berg:')
    st.latex(rf'L_{{tb.mørtel.berg}} = \frac{{P_p}}{{\tau_{{d;mørtel-berg}} \cdot d_{{borhull}} \cdot \pi}} = {lengde_mørtel_berg} m')
    st.write('Lengde for nødvendig forankringslengde for brudd i berg:')
    st.latex(rf"\lambda = \sqrt{{\frac{{\gamma_M \cdot P_p}}{{\tau_k \cdot \pi \cdot \tan \varphi}}}} = {lengde_berg} m")

if lengde_stål_mørtel >= lengde_mørtel_berg and lengde_stål_mørtel >= lengde_berg:
    st.write(f"**Dimensjonerende kriterie er heft mellom stål og mørtel. Nødvendig lengde blir {lengde_stål_mørtel} m**")
elif lengde_mørtel_berg >= lengde_stål_mørtel and lengde_mørtel_berg >= lengde_berg:
    st.write(f"**Dimensjonerende kriterie er heft mellom mørtel og berg. Nødvendig lengde blir {lengde_mørtel_berg} m**")
else:
    st.write(f"**Dimensjonerende kriterie er utrekking av berg. Nødvendig lengde blir {lengde_berg} m**")


# reduksjonsfaktor_fa = 0.9

# indre_dimensjonerende_kapasitet = reduksjonsfaktor_fa * (bolt[bolttype]["Flytlast"]/(1.2 * materialfaktor_for_stålstag))

# st.write(f"Indre kapasistet: {indre_dimensjonerende_kapasitet} kN")

# #Brudd mellom stag og mørtel
# dimensjonerende_heft = 2.4 * 1.25


# st.write(f'Naudsynt lengde for brudd mellom stag og mørtel: {lengde_stag_mørtel} m')

# #Brudd mellom mørtel og berg

# lengde_stag_berg = forankringskraft / ((bergegenskaper[bergart]['Heftfasthet (MPa)']/1.25) * hulldiameter * math.pi)

# st.write(f'Naudsynt lengde for brudd mellom mørtel og berg: {lengde_stag_berg} m')

# #Stabilitet i berg mot uttreking

# lengde_berg_utrekk = math.sqrt((gamma_m_berg * forankringskraft)/(heftfasthet_berg[heftfasthetstype]['Heftfasthet'] * math.pi * math.tan(math.radians(heftfasthet_berg[heftfasthetstype]['Bruddvinkel']))))
# st.write(f'Naudsynt lengde for brudd i berg: {lengde_berg_utrekk} m')