import streamlit as st
import math

snøhøgde = st.number_input("3 døgns snøhøgde i cm", min_value=0, max_value=10000, value=150, step=1)
terrengivnkel = st.number_input("Terrengvinkel i grader", min_value=0, max_value=90, value=35, step=1)


def bruddhøgde(snøhøgde, terrengvinkel):
    vinkeljustering = 0.291 / (math.sin(math.radians(terrengvinkel)) - (0.202 * math.cos(math.radians(terrengvinkel))))
    return vinkeljustering * snøhøgde

st.write("Bruddhøgde: ", round(bruddhøgde(snøhøgde, terrengivnkel), 2), "cm")

st.write('Metode referert i NVE sin skredfareveileder: https://veileder-skredfareutredning-bratt-terreng.nve.no/hvordan-utfore-en-skredfareutredning/fase-2-utfore-oppdrag/prosedyre-snoskred/steg-2-vurdering-av-losneomrader-og-losnesannsynlighet/')
st.write('Referanse: Salm, B., Gubler, H. U., & Burkard, A. (1990). Berechnung von Fliesslawinen: eine Anleitung für Praktiker mit Beispielen. Eidgenössisches Institut für Schnee-und Lawinenforschung, Weissfluhjoch/Davos.')
