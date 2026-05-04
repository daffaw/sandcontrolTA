import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Gravel Pack Design Tool", layout="centered")

st.title("Gravel Pack Design Tool")

# =========================
# INPUT
# =========================

st.sidebar.header("Input Data")

Ro = st.sidebar.number_input("Ro (ohm-m)", value=0.9)
Rw = st.sidebar.number_input("Rw (ohm-m)", value=0.1)
phi = st.sidebar.number_input("Porosity (%)", value=28.0)

d40 = st.sidebar.number_input("d40 (in)", value=0.0069, step=0.0001, format="%.6f")
d90 = st.sidebar.number_input("d90 (in)", value=0.00475, step=0.0001, format="%.6f")

Grlog = st.sidebar.number_input("GR log", value=30.0)
Grmax = st.sidebar.number_input("GR max", value=120.0)
Grmin = st.sidebar.number_input("GR min", value=20.0)

pb = st.sidebar.number_input("Bulk Density (gr/cc)", value=1.9)
dt = st.sidebar.number_input("Δt (us/ft)", value=115.0)
K = st.sidebar.number_input("Permeability (md)", value=1000.0)

interval = st.sidebar.number_input("Interval (ft)", value=54.0)
shot_density = st.sidebar.number_input("Shot Density (SPF)", value=12)

A_input = st.sidebar.number_input("A (ft³)", value=10.0)
B_input = st.sidebar.number_input("B (bbl/stb)", value=0.007)
mu = st.sidebar.number_input("Viscosity (cp)", value=0.1)

run = st.sidebar.button("Run Calculation")

# =========================
# FUNCTIONS
# =========================

def calc_F(Ro, Rw):
    return Ro / Rw

def calc_Vclay(Grlog, Grmin, Grmax):
    return (Grlog - Grmin) / (Grmax - Grmin)

def calc_U(Vclay):
    return 0.125 * Vclay + 0.27

def calc_C(d40, d90):
    return d40 / d90

def calc_A():
    return 0.5

def calc_B():
    return 1/3

def calc_N(interval, shot_density):
    return interval * shot_density

def calc_G(A, pb, dt):
    return 1.34e11 * (A * pb / dt**2)

def calc_Qc(K, N, G, A_input, B_input, mu):
    return 0.025e-6 * (K * N * G * A_input) / (B_input * mu)

def calc_m(Ro, Rw, phi):
    return - (math.log10(Ro/Rw) / math.log10(phi/100))

def calc_So(d40, d90):
    return (d40 / d90)**0.5


def calc_gravel(d40, d90):
    d50 = (d40 + d90)/2
    gmin = 5 * d50
    gmax = 6 * d50
    gmid = (gmin + gmax)/2
    return d50, gmin, gmax, gmid


def sieve_map(gravel):
    if 0.066 >= gravel >= 0.0331:
        return "12–20", 0.024
    elif 0.0331 > gravel >= 0.0165:
        return "20–40", 0.012
    elif 0.0165 > gravel >= 0.0098:
        return "40–60", 0.010
    elif 0.0098 > gravel >= 0.0059:
        return "60–100", 0.006
    else:
        return "Out of range", None

# =========================
# CLASSIFICATION
# =========================

def classify_m(m):
    if m <= 1.3:
        return "Unconsolidated Rocks"
    elif m <= 1.5:
        return "Very Slightly Cemented"
    elif m <= 1.7:
        return "Slightly Cemented"
    elif m <= 1.9:
        return "Moderately Cemented"
    elif m <= 2.2:
        return "Highly Cemented"
    else:
        return "Out of Range"

def classify_dt(dt):
    if dt < 95:
        return "Compact Formation"
    elif 95 <= dt <= 105:
        return "Uncertain"
    else:
        return "Unconsolidated Formation"

def classify_So(So):
    if So < 2.5:
        return "Well Sorted"
    elif So < 4.5:
        return "Poorly Sorted"
    else:
        return "Very Poorly Sorted"

# =========================
# PROCESS
# =========================

if run:

    F = calc_F(Ro, Rw)
    Vclay = calc_Vclay(Grlog, Grmin, Grmax)
    U = calc_U(Vclay)
    C = calc_C(d40, d90)
    A = calc_A()
    B = calc_B()
    N = calc_N(interval, shot_density)
    G = calc_G(A, pb, dt)
    Qc = calc_Qc(K, N, G, A_input, B_input, mu)
    m = calc_m(Ro, Rw, phi)
    So = calc_So(d40, d90)

    d50, gmin, gmax, gmid = calc_gravel(d40, d90)
    sieve, slot = sieve_map(gmid)

    # 🔥 CLASSIFICATION
    m_class = classify_m(m)
    dt_class = classify_dt(dt)
    So_class = classify_So(So)

    # =========================
    # TABLE OUTPUT
    # =========================

    data = {
        "Parameter": ["F", "Vclay", "C", "m", "So", "N", "G", "Qc"],
        "Result": [
            f"{F:.3f}",
            f"{Vclay:.3f}",
            f"{C:.3f} ",
            f"{m:.3f}",
            f"{So:.3f}",
            f"{N:.0f} shots",
            f"{G:,.2f} psi",
            f"{Qc:,.2f} stb/day"
        ]
    }

    st.dataframe(pd.DataFrame(data), use_container_width=True)

    # =========================
    # INTERPRETATION
    # =========================

    st.subheader("Formation Evaluation")

    st.success(f"""
    Cementation (m): {m_class}  

    Formation Condition (Δt): {dt_class}  

    Sorting Quality (So): {So_class}
    """)

    # =========================
    # DESIGN
    # =========================

    st.subheader("Gravel Pack Design")

    st.write(f"""
d50: {d50:.5f} in  

Gravel Range:
- {gmin:.5f} – {gmax:.5f} in
""")

    st.subheader("Screen Selection")

    st.success(f"""
Sieve Size: {sieve}  
Slot Size: {slot} in
""")