import streamlit as st
from geo import grunn, geofunk, geolag, geo_plot
import math
#TODO: Sjekke opp i reduksjonsfaktor
st.set_page_config(page_title='NVDB skreddata', page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title("Forenkla utrekning av bæreevne")
st.write("###  etter HBV220")

def calculate_phi(tan_phi_value):
    # Convert tan_phi to phi
    return math.degrees(math.atan(tan_phi_value))

def calculate_tan_phi(phi_value):
    # Convert phi to tan_phi
    return math.tan(math.radians(phi_value))
col1, col2 = st.columns([1, 3])

with col1:
# Radio button for input selection
    format_option = st.radio("Velg grader, eller forholdstall:", ('φ (grader)', 'tan φ'))

    # Input for φ (degrees)
    if format_option == 'φ (grader)':
        phi_value = st.number_input('φ (grader)', value=38)
        tan_phi_value = calculate_tan_phi(phi_value)
    # Input for tan(φ)
    elif format_option == 'tan φ':
        tan_phi_value = st.number_input('tan φ', value=0.0)
        phi_value = calculate_phi(tan_phi_value)

    # Display the current values
    col3, col4 = st.columns([1, 1])
    with col3:
        st.write(f"φ (grader): {round(phi_value,1)}")
    with col4:
        st.write(f"tan φ: {round(tan_phi_value,2)}")
    gamma = st.number_input("Gamma", value=18, min_value=0, max_value=30, step=1)
    gamma_m = st.number_input("Gamma_m", value=1.4, min_value=1.0, max_value=2.0, step=0.05)
    attraksjon = st.number_input("Attraksjon", value=2, min_value=0, max_value=1000, step=1)
    terrenghelling = st.number_input("Terrenghelling", value=0.0, min_value=0.0, max_value=2.0, step=0.01)
    #grunnvannstand = st.number_input("Grunnvannstand", value=0.0, min_value=0.0, max_value=10.0, step=0.1)
    #tan_phi = st.number_input("Tan phi", value=0.7)
    #attraksjon = st.number_input("Attraksjon", value=10)
    #grunnvannstand = st.number_input("Grunnvannstand", value=2)
    #gamma = st.number_input("Gamma", value=20)
    #Jordparametere

    #Avledede parametere
    tan_fi_d = round(tan_phi_value/gamma_m,2)

    #vertikalkrefter
    fv_fund = st.number_input("Sum vertikalkraft", value=360, min_value=0, step=1)
    #Horisontalkrefter
    fh = st.number_input("Sum horisontalkraft", value=120, min_value=0, step=1)

    #Dybde til underkant fundament
    z = st.number_input("Dybde til underkant fundament", value=0.5, min_value=0.0, step=0.1)
with col2:
    try:
        jordlag = grunn.JordLag('grus', 10000, gamma)
        jordlag.sett_styrke_parameter(tanphi=tan_fi_d, attraksjon=attraksjon)
        jordprofil = grunn.JordProfil([jordlag], z)





        b0, fig = geo_plot.finn_solebredde(z, fv_fund, fh, gamma_m, terrenghelling, jordprofil, plot=True)
        st.write(b0)
        st.pyplot(fig)

        fundament = grunn.Fundament(b0, z, fv_fund, fh, gamma_m, jordprofil)
        fundament.sett_delta_fv()
        fundament.sett_rb()
        fundament.nq_ngamma_faktor()
        plot = geo_plot.plot_samla(fundament, jordprofil, terrenghelling)
        st.pyplot(plot)

        nfaktplot = geo_plot.plot_nfakt(fundament.tan_fi_d, fundament.rb, fundament.nq, fundament.n_gamma)
        st.pyplot(nfaktplot)
    except ValueError:
        st.write("Feil i input, kan f.eks være for stort forhold mellom horisontal og vertikal kraft")