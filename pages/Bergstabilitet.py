
import math
import streamlit as st

st.set_page_config(page_title="Bergstabilitet – Partialfaktor (EC7)", page_icon="⛰️", layout="wide")

def deg(x): return x*180.0/math.pi

st.title("⛰️ Bergstabilitet – Partialfaktormetoden (Eurokode 7)")
st.caption("Likevektsberegning for blokk på planar svakhet ved bruk av **karakteristiske** og **dimensjonerende** verdier. "
           "Appen følger prinsippene i teksten din: Ekv. (5.2.4—9) for φ, (5.2.4—21..28) for ulike boltmodeller. "
           "Forholdet ΣRₙ/ΣFₙ navngis **ikke** som sikkerhetsfaktor.")

tab_pf, tab_fs = st.tabs(["Partialfaktor (EC7)", "Klassisk FS (referanse)"])

# ----------------------------
# Helper functions
# ----------------------------
def components_from_weight(G, beta):
    """Return driving and normal components of weight along/normal to plane"""
    b = math.radians(beta)
    Gs = G * math.sin(b)
    Gn = G * math.cos(b)
    return Gs, Gn

def bolt_components(T, alpha, beta):
    """Return stabilising components of bolt relative to plane using definitions Ts = T cos(α+β), Tn = T sin(α+β)"""
    a = math.radians(alpha)
    b = math.radians(beta)
    Ts = T * math.cos(a + b)
    Tn = T * math.sin(a + b)
    return Ts, Tn

def tanphi_design(phi_deg, gamma_phi):
    # tan(phi_d) = tan(phi_k)/gamma_phi  -> phi_d = atan(tan(phi_k)/gamma_phi)
    return math.tan(math.radians(phi_deg))/gamma_phi

def apply_preset_table_525():
    """Preset that reproduces Table 5.2.5 in the user's text"""
    st.session_state["H"] = 20.0
    st.session_state["beta"] = 65.0
    st.session_state["theta"] = 80.0
    st.session_state["gamma_b"] = 27.0
    st.session_state["use_geom_weight"] = True
    st.session_state["A"] = 22.0

    st.session_state["phi_k"] = 35.0
    st.session_state["phi_r_k"] = 30.0
    st.session_state["c_k"] = 30.0

    # Water
    st.session_state["U_c"] = 1103.0
    st.session_state["gamma_w"] = 1.0

    # Seismic excluded in the example
    st.session_state["include_seismic"] = False
    st.session_state["agR"] = 0.2  # as stated, but excluded
    st.session_state["Sf"] = 1.0
    st.session_state["gamma_ag"] = 1.25
    st.session_state["g"] = 9.81
    st.session_state["extra_gamma_F"] = 1.0

    # Bolts: 12 × 20 mm, capacity 157 kN each, α=10°, use γ_s = 1.25 per the table
    st.session_state["alpha"] = 10.0
    st.session_state["T_cap_per_bolt"] = 157.0
    st.session_state["n_bolts"] = 12
    st.session_state["T_pretension"] = 0.0
    st.session_state["gamma_s"] = 1.25

    # Partial factors
    st.session_state["gamma_phi"] = 1.25
    st.session_state["gamma_c"] = 1.25
    st.session_state["gamma_G"] = 1.0
    st.session_state["gamma_G_fav"] = 1.0

# ----------------------------
# TAB 1: Partial factor method
# ----------------------------
with tab_pf:
    st.header("Input – karakteristiske verdier og partialfaktorer")


    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Geometri/vekt")
        H = st.number_input("Høyde H (m)", min_value=0.0, value=20.0, step=0.5, key="H")
        beta = st.number_input("Svakhetsplanets fallvinkel β (° over horisontal)", min_value=0.0, max_value=89.9, value=65.0, step=0.5, key="beta")
        theta = st.number_input("Skjæringsflatens fallvinkel θ (° over horisontal)", min_value=0.0, max_value=89.9, value=80.0, step=0.5, key="theta")
        gamma_b = st.number_input("Tyngdetetthet berg ρ_b (kN/m³)", min_value=0.0, value=27.0, step=0.5, format="%.3f", key="gamma_b")
        use_geom_weight = st.checkbox("Beregn G fra H, β, θ (eq. 5.2.4—5)", value=True, key="use_geom_weight")
        if use_geom_weight and H>0 and math.tan(math.radians(beta))>0 and math.tan(math.radians(theta))>0:
            G_c = gamma_b * (H**2)/2.0 * (1.0/math.tan(math.radians(beta)) - 1.0/math.tan(math.radians(theta)))
            G_c = max(0.0, G_c)
        else:
            G_c = st.number_input("Blokkens karakteristiske vekt G (kN per m skjæring)", min_value=0.0, value=660.0, step=10.0, format="%.3f", key="G_c_manual")
        A = st.number_input("Areal av svakhetsplan A (m² per m skjæring)", min_value=0.0, value=22.0, step=0.5, key="A")

    with c2:
        st.subheader("Skjærstyrke")
        phi_k = st.number_input("Friksjonsvinkel φ (grader)", min_value=0.0, max_value=60.0, value=35.0, step=0.5, key="phi_k")
        phi_r_k = st.number_input("Residual friksjonsvinkel φᵣ (grader)", min_value=0.0, max_value=60.0, value=30.0, step=0.5, key="phi_r_k")
        c_k = st.number_input("Kohesjon c (kPa = kN/m²)", min_value=0.0, value=30.0, step=1.0, key="c_k")
        st.write("— NB: Sett c=0 om du ikke ønsker kohesjon.")

        st.subheader("Sprekkevann")
        with st.expander("💧 Vanntrykkskalkulator", expanded=False):
            model = st.selectbox("Modell", ["Triangulær (A)", "Hydrostatisk (B)", "Tensjonssprekk (C)"])
            rho_w = st.number_input("Vannets tyngdetetthet ρ_w (kN/m³)", min_value=0.0, value=10.0, step=0.1, key="rho_w")
            fill = st.slider("Oppfyllingsgrad i sprekken (0–1)", min_value=0.0, max_value=1.0, value=1.0, step=0.05, key="fill_ratio")
            H_eff = H * fill
            beta_rad = math.radians(beta) if beta>0 else 1e-6
            if model == "Triangulær (A)":
                U_calc = rho_w * (H_eff**2) / (4.0 * math.sin(beta_rad))
                st.caption("Formel: U = ρ_w · H_eff² / (4 · sinβ). Samsvarer med eq. (5.2.4—11) utan partialfaktor.")
            elif model == "Hydrostatisk (B)":
                U_calc = rho_w * (H_eff**2) / (2.0 * math.sin(beta_rad))
                st.caption("Formel: U = ρ_w · H_eff² / (2 · sinβ) (teoretisk verst).")
            else:  # Tension crack (C)
                h_tc = st.number_input("Vassdjup i tensjonssprekk h_tc (m)", min_value=0.0, value=0.0, step=0.5, key="h_tc")
                U_calc = rho_w * (h_tc * H_eff + 0.5 * H_eff**2) / (math.sin(beta_rad))
                st.caption("Formel: U = ρ_w · (h_tc · H_eff + 0.5 · H_eff²) / sinβ.")

            st.write(f"**U (karakteristisk)** = {U_calc:,.1f} kN")
            # Allow applying to the main U_c field
            if st.button("Bruk denne verdien i beregningen"):
                st.session_state["U_c"] = float(U_calc)
                try:
                    st.rerun()
                except Exception:
                    st.experimental_rerun()

        U_c = st.number_input("Karakteristisk vannkraft U (kN, normalt **ut** av planet)", min_value=0.0, value=1103.00, step=10.0, format="%.3f", key="U_c")
        gamma_w = st.number_input("Partialfaktor for vann/egenvekt γ_γ", min_value=0.1, value=1.0, step=0.05, format="%.2f", key="gamma_w")

    with c3:
        st.subheader("Seismikk")
        include_seismic = st.checkbox("Ta med seismisk påvirkning", value=True, key="include_seismic")
        agR = st.number_input("Grunnakselerasjon a_gR (m/s²)", min_value=0.0, value=0.2, step=0.05, key="agR")
        Sf = st.number_input("Forsterkningsfaktor S_f (—)", min_value=0.0, value=1.0, step=0.1, key="Sf")
        gamma_ag = st.number_input("Partialfaktor for a_g (γₐ)", min_value=1.0, value=1.25, step=0.05, key="gamma_ag")
        g = st.number_input("Tyngdens akselerasjon g (m/s²)", min_value=1.0, value=9.81, step=0.01, key="g")
        extra_gamma_F = st.number_input("Ekstra lastfaktor γ_f på seismiske **krefter** (valgfri)", min_value=1.0, value=1.0, step=0.05, key="extra_gamma_F")

        st.subheader("Bolt(er)")
        alpha = st.number_input("Boltvinkel α (° fra horisontal)", min_value=0.0, max_value=180.0, value=10.0, step=0.5, key="alpha")
        T_cap_per_bolt = st.number_input("Karakteristisk kapasitet pr bolt (kN)", min_value=0.0, value=157.0, step=1.0, key="T_cap_per_bolt")
        n_bolts = st.number_input("Antall bolter (pr. meter)", min_value=0, value=12, step=1, key="n_bolts")
        T_pretension = st.number_input("Forspenningskraft pr bolt (kN) [sett 0 for passiv]", min_value=0.0, value=0.0, step=5.0, key="T_pretension")
        gamma_s = st.number_input("Materialfaktor for bolt γ_s", min_value=1.0, value=1.25, step=0.05, key="gamma_s")

    # Partial factors for strength
    st.subheader("Partialfaktorer for material/last")
    colpf1, colpf2, colpf3 = st.columns(3)
    with colpf1:
        gamma_phi = st.number_input("γ_φ (friksjon)", min_value=1.0, value=1.25, step=0.05, key="gamma_phi")
        gamma_c = st.number_input("γ_c (kohesjon)", min_value=1.0, value=1.25, step=0.05, key="gamma_c")
    with colpf2:
        gamma_G = st.number_input("γ_G for vekt (unfavourable) – brukes på **drivende** komponent G_s", min_value=1.0, value=1.0, step=0.05, key="gamma_G")
        gamma_G_fav = st.number_input("γ_G,fav for vekt (favourable) – brukes på **stabiliserende** komponent G_n", min_value=0.5, value=1.0, step=0.05, key="gamma_G_fav")
    with colpf3:
        st.caption("Standardvalg følger tabellene i NA i EN 1997/1998 etter vanlig praksis; justér etter behov/klasse.")

    # ---- Derived characteristic components ----
    Gs_c, Gn_c = components_from_weight(G_c, beta)

    # Seismiske krefter
    if include_seismic:
        ag_d = gamma_ag * agR
        Fa_c = 0.5 * (ag_d / g) * Sf * G_c  # "design" iht. 5.2.4-13
        Fs_c = Fa_c * math.cos(math.radians(beta))
        Fn_c = Fa_c * math.sin(math.radians(beta))
    else:
        ag_d = 0.0
        Fa_c = 0.0
        Fs_c = 0.0
        Fn_c = 0.0

    # ---- Apply partial factors to get design values ----
    # Actions (driving): F_d = F_c * γ_f   | Permanent favourable: divide or set 1.0. We use γ_G and γ_G_fav sliders.
    Gs_d = Gs_c * gamma_G
    Gn_d = Gn_c * (1.0/gamma_G_fav) if gamma_G_fav != 0 else 0.0  # favourable -> often divided; slider default 1.0 (no change)
    # Water
    U_d = U_c * gamma_w
    # Seismics: allow extra gamma on force if desired
    Fs_d = Fs_c * extra_gamma_F
    Fn_d = Fn_c * extra_gamma_F

    # Strength: φ_d via tan relation; c_d = c_k / γ_c
    tan_phi_d = tanphi_design(phi_k, gamma_phi)
    tan_phir_d = tanphi_design(phi_r_k, gamma_phi)
    c_d = c_k / gamma_c

    # Bolter: total characteristic capacity / pretension
    T_cap_c = T_cap_per_bolt * n_bolts
    T_cap_d = T_cap_c / gamma_s if gamma_s>0 else 0.0
    T_pret_tot_c = T_pretension * n_bolts
    T_pret_tot_d = T_pret_tot_c / gamma_s if gamma_s>0 else 0.0

    # Bolt components for two cases:
    Ts_cap_d, Tn_cap_d = bolt_components(T_cap_d, alpha, beta)           # full kapasitet
    Ts_pret_d, Tn_pret_d = bolt_components(T_pret_tot_d, alpha, beta)    # kun forspenning

    # ------------- MODELS -------------
    # Conventional ACTIVE (5.2.4—21,22)
    Rd_active_conv = c_d*A + (Gn_d - U_d - Fn_d + Tn_cap_d)*tan_phi_d
    Fd_active_conv = Gs_d + Fs_d - Ts_cap_d

    # NEW ACTIVE (Li & Høien) - mot kollaps (5.2.4—25,26)
    Rd_active_new = c_d*A + (Gn_d - U_d - Fn_d + Tn_cap_d)*tan_phi_d + Ts_cap_d
    Fd_active_new = Gs_d + Fs_d

    # PASSIVE – mot skjærbrudd (5.2.4—27)
    Rd_passive_shear = c_d*A + (Gn_d - U_d - Fn_d)*tan_phi_d
    Fd_passive_shear = Gs_d + Fs_d

    # PASSIVE – mot kollaps (residual, full bolt capacity) (5.2.4—28)
    Rd_passive_collapse = (Gn_d - U_d - Fn_d + Tn_cap_d)*tan_phir_d + Ts_cap_d
    Fd_passive_collapse = Gs_d + Fs_d

    # ACTIVE – *kun forspenning* (mot skjærbrudd) – bruker pretensjon i staden for full kapasitet
    Rd_active_shear_pret = c_d*A + (Gn_d - U_d - Fn_d + Tn_pret_d)*tan_phi_d + Ts_pret_d
    Fd_active_shear_pret = Gs_d + Fs_d

    # Report table
    st.header("Resultat – dimensjonerende verdier")
    # Build a small table
    rows = [
        ("Aktiv bolt – konvensjonell", Rd_active_conv, Fd_active_conv),
        ("Aktiv bolt – ny (mot kollaps, full kapasitet)", Rd_active_new, Fd_active_new),
        ("Passiv bolt – mot skjærbrudd", Rd_passive_shear, Fd_passive_shear),
        ("Passiv bolt – mot kollaps (residual φᵣ)", Rd_passive_collapse, Fd_passive_collapse),
        ("Aktiv – *kun forspenning* (mot skjærbrudd)", Rd_active_shear_pret, Fd_active_shear_pret),
    ]

    import pandas as pd
    data = []
    for name, Rd, Fd in rows:
        ratio = (Rd/Fd) if Fd>0 else float("inf")
        ok = "✅ OK" if Rd > Fd else "❌ Ikke OK"
        data.append({
            "Modell": name,
            "ΣR_d [kN]": round(Rd,2),
            "ΣF_d [kN]": round(Fd,2),
            "ΣR_d/ΣF_d": (float("inf") if ratio==float("inf") else round(ratio,3)),
            "Vurdering": ok
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    with st.expander("Detaljerte komponenter (dimensjonerende)"):
        st.write(f"G (kar.) = **{G_c:,.1f} kN**  →  G_s,d = {Gs_d:,.1f} kN,  G_n,d = {Gn_d:,.1f} kN")
        st.write(f"Seismikk: a_g,d = {ag_d:.3f} m/s² → F_a = {Fa_c:,.1f} kN;  F_s,d = {Fs_d:,.1f} kN,  F_n,d = {Fn_d:,.1f} kN")
        st.write(f"Vann: U_d = {U_d:,.1f} kN (ut av planet)")
        st.write(f"φ_d = {deg(math.atan(tan_phi_d)):.2f}°,  tanφ_d = {tan_phi_d:.3f}  |  φᵣ_d = {deg(math.atan(tan_phir_d)):.2f}°, tanφᵣ_d = {tan_phir_d:.3f}")
        st.write(f"c_d = {c_d:.2f} kPa,  A = {A:.2f} m²  → c_d·A = {c_d*A:.1f} kN")
        st.write(f"Bolter (kapasitet): T_d = {T_cap_d:.1f} kN → T_s = {Ts_cap_d:.1f} kN, T_n = {Tn_cap_d:.1f} kN")
        if T_pret_tot_d>0:
            st.write(f"Bolter (forspenning): T_pre,d = {T_pret_tot_d:.1f} kN → T_s = {Ts_pret_d:.1f} kN, T_n = {Tn_pret_d:.1f} kN")

# ----------------------------
# TAB 2: Classic FS = R/D (for referanse)
# ----------------------------
with tab_fs:
    st.header("Klassisk sikkerhetsfaktor FS (kun referanse)")
    st.caption("Dette fanearket følger en enkel R/D-modell. Brukes kun som kontroll – **ikke** bland begrepene.")
    col1, col2 = st.columns(2)
    with col1:
        W = st.number_input("W (kN) – vekt av blokk", min_value=0.0, value=1500.0, step=10.0, format="%.2f", key="Wfs")
        beta_fs = st.number_input("β (°)", min_value=0.0, max_value=89.9, value=65.0, step=0.5, key="betafs")
        phi_fs = st.number_input("φ (°)", min_value=0.0, max_value=60.0, value=35.0, step=0.5, key="phifs")
        c_fs = st.number_input("c (kPa)", min_value=0.0, value=30.0, step=1.0, key="cfs")
        A_fs = st.number_input("A (m²)", min_value=0.0, value=22.0, step=0.5, key="Afs")
    with col2:
        U_fs = st.number_input("U (kN) – normal ut av planet", min_value=0.0, value=0.0, step=10.0, key="Ufs")
        T_fs = st.number_input("T (kN) – boltkraft (full)", min_value=0.0, value=0.0, step=10.0, key="Tfs")
        alpha_fs = st.number_input("α (° fra horisontal)", min_value=0.0, max_value=180.0, value=10.0, step=0.5, key="alphafs")
        kh = st.number_input("k_h – horisontal seismisk koeff.", min_value=0.0, value=0.0, step=0.01, key="khfs")

    b = math.radians(beta_fs); a = math.radians(alpha_fs); ph = math.radians(phi_fs)
    DW = W*math.sin(b); NW = W*math.cos(b)
    Fa = kh*W
    DF = Fa*math.cos(b); NF = -Fa*math.sin(b)
    Ts = T_fs*math.cos(a+b); Tn = T_fs*math.sin(a+b)
    Ntot = NW + NF + Tn - U_fs
    R = max(0.0, Ntot*math.tan(ph) + c_fs*A_fs) + max(0.0, Ts)
    D = max(0.0, DW + DF - min(0.0, Ts))
    FS = (R/D) if D>0 else float("inf")
    st.metric("FS", f"{FS:,.3f}")
    st.write(f"R = {R:,.1f} kN, D = {D:,.1f} kN")
