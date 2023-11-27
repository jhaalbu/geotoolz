import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

st.title("Utrekning av brotkanthøgde for flakskred")

st.write('Basert på metode fra Sveits, ved Salm et al (1990)')
st.write('Sjå også NVE sin skredfareveileder angåande brotkanthøgde')
st.markdown("[NVE Veileder](https://veileder-skredfareutredning-bratt-terreng.nve.no/hvordan-utfore-en-skredfareutredning/fase-2-utfore-oppdrag/prosedyre-snoskred/steg-2-vurdering-av-losneomrader-og-losnesannsynlighet/)")

snøhøgde = st.number_input("3 døgns snøhøgde i cm (for det aktuelle gjenntaksintervall)", min_value=0, max_value=10000, value=150, step=1)
terrengivnkel = st.number_input("Terrengvinkel i grader", min_value=0, max_value=90, value=35, step=1)

@np.vectorize
def bruddhøgde(snøhøgde, terrengvinkel):
    vinkeljustering = 0.291 / (math.sin(math.radians(terrengvinkel)) - (0.202 * math.cos(math.radians(terrengvinkel))))
    return vinkeljustering * snøhøgde


st.write("Bruddhøgde: ", np.round(bruddhøgde(snøhøgde, terrengivnkel), 2), "cm")

st.divider()

bruddhøgdeliste = []
vinkelliste = []
for i in range(28, 60):
    brudd_høgde_temp = bruddhøgde(snøhøgde, i)
    bruddhøgdeliste.append(brudd_høgde_temp)
    vinkelliste.append(i)

plt.plot(vinkelliste, bruddhøgdeliste)
#plt.gca().invert_xaxis() 
#plt.gca().invert_yaxis() 
plt.ylabel('Flaktykkelse (cm)')
plt.xlabel('Terrengvinkel (grader)')

# Display the plot in Streamlit
st.pyplot(plt)


st.write('Referanse: Salm, B., Gubler, H. U., & Burkard, A. (1990). Berechnung von Fliesslawinen: eine Anleitung für Praktiker mit Beispielen. Eidgenössisches Institut für Schnee-und Lawinenforschung, Weissfluhjoch/Davos.')
st.markdown("[Salm et al (1990)](https://www.slf.ch/fileadmin/lawineninfo/lawinenhandbuch/1990_Salm_et_al_Berechnung_von_Fliesslawinen.pdf)")