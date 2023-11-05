import streamlit as st

st.set_page_config(
    page_title="Geoverktøy",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Geoverktøy")

st.write("Denne webappen er ein samling av forksjellige geoverktøy. Sjå i venstre meny for å velge verktøy.")

st.image("PB160147.jpg")
st.write("Jordskred i Oldedalen etter ekstremværet Hilde den 16.11.2013. Foto: Jan Helge Aalbu")

with st.sidebar:
    st.write("Ved spørsmål om verktøy ta kontakt på jan.helge.aalbu@vegvesen.no")