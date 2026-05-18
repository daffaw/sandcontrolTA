import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if "history" not in st.session_state:
    st.session_state.history = []

if "run_triggered" not in st.session_state:
    st.session_state.run_triggered = False

from modules import economics
from modules import payout
from modules import formation
from modules import psd as psd_calc


st.title("Sand Control Selection Tool")

# =========================
# RULE-BASED ENGINE
# =========================

def is_sanding_risk(uc, fines, production_target, critical_rate):
    """
    Sanding risk screening based on PSD quality and critical rate.
    Risk is triggered if one of these conditions occurs:
    1. UC is lower than 3
    2. Fines is higher than 5%
    3. Production target is higher than critical rate Qz
    """

    if pd.isna(uc) or pd.isna(fines) or pd.isna(critical_rate):
        return False

    if uc < 3:
        return True

    if fines > 5:
        return True

    if production_target > critical_rate:
        return True

    return False

def evaluate_clay(swelling):
    if swelling == "YES":
        return "Effected by clay swelling, review Drilling Fluid Selection & GP Water Pack Not Recommended"
    else:
        return "No Effected by Clay"


def evaluate_psd(uc, fines):
    
    if uc < 3 and fines <= 2:
        return "SAS Wire Wrapped"
    
    elif 3 <= uc <= 5 and fines <= 5:
        return "SAS Premium Mesh"
    
    elif uc > 5 and 5 < fines < 10:
        return "Gravel Pack"
    
    elif uc > 5 and fines > 10:
        return "Frac Pack / Chemical Sand Control"
    else:
        return "Gravel Pack"

def evaluate_completion(rate, inclination):
    if rate < 7000 and inclination < 65:
        return "SAS Wire Wrapped / Premium Mesh"
    else:
        return "Gravel Pack / Expandable Sand Screen (ESS)"


def evaluate_chemical(rate, clay, fines, completion, hole, cement, length_perfo, temp):
    if (
        rate > 6000 and
        clay < 4 and
        fines < 15 and
        completion == "NEW" and
        hole == "Cased Hole" and
        cement.lower() == "yes" and
        length_perfo < 40 and
        temp < 350
    ):
        return "Resin Sand Consolidation"
    else:
        return "Polymer Sand Consolidation"


def remark_psd(psd_result):
    if psd_result in ["SAS Premium Mesh", "SAS Wire Wrapped"]:
        return "Not Recommended for High Inclination and High Rate"
    else:
        return "Positive Skin, High Cost & Complex Operation"


def remark_completion(comp_result):
    if comp_result == "SAS Premium Mesh":
        return "Not Recommended for High Inclination and High Rate"
    else:
        return "Positive Skin, High Cost & Complex Operation"


def remark_chemical(chem_result):
    if chem_result == "Resin Sand Consolidation":
        return "Good for High Rate"
    else:
        return "Preferable under 6000 bfpd"


# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Well Data",
    "Sand Formation",
    "PSD",
    "Completion & Operational",
    "Reservoir Properties",
    "Economics",
    "Results"
])

# =========================
# WELL DATA
# =========================
with tab1:
    st.subheader("Well Data")

    col1, col2 = st.columns(2)

    with col1:
        well_name = st.text_input("Well Name", value="WIDH-10")
        fortion = st.text_input("Formation", value="TAF Sandstone")


# =========================
# CLAY
# =========================
with tab2:
    st.subheader("Clay Analysis")

    # =========================
    # SWELLING
    # =========================
    swelling = st.selectbox("Swelling Clay?", ["NO", "YES"])

    st.markdown("---")

    # =========================
    # CEMENTATION (ARCHIE)
    # =========================
    st.subheader("Cementation Calculation (Archie)")

    col1, col2, col3 = st.columns(3)

    with col1:
        phi = st.number_input("Porosity (Φ)", value=0.25)

    with col2:
        Ro = st.number_input("Ro (ohm-m)", value=10.0)

    with col3:
        Rw = st.number_input("Rw (ohm-m)", value=0.1)

    # =========================
    # FORMATION STRENGTH
    # =========================
    st.markdown("---")
    st.subheader("Formation Strength")

    col4, col5, col6 = st.columns(3)

    with col4:
        Vclay = st.number_input("Clay Volume (fraction)", value=0.2)

    with col5:
        rho_b = st.number_input("Bulk Density (g/cc)", value=2.3)

    with col6:
        dts = st.number_input("Δts (us/ft)", value=120.0)
    
    #Critical Rate
    st.subheader("Critical Rate Calculation")

    col1, col2, col3 = st.columns(3)

    with col1:
        k = st.number_input("Permeability (k, mD)", value=7.590, step=0.0001)
        Nz = st.number_input("Nz (Perforation Density)", value=480.0, step=0.0001)

    with col2:
        Bz = st.number_input("Bz (RB/STB)", value=1.1)

    with col3:
        mu = st.number_input("Viscosity (cp)", value=1.0)


# =========================
# PSD
# =========================
# =========================
# PSD
# =========================
with tab3:
    st.subheader("Particle Size Distribution")


    # =========================
    # SIEVE INPUT TABLE
    # =========================
    with st.expander("Sieve Input Table", expanded=True):

        if "sieve_input" not in st.session_state:
            st.session_state.sieve_input = psd_calc.default_sieve_table()

        sieve_input = st.data_editor(
            st.session_state.sieve_input,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sieve Size": st.column_config.SelectboxColumn(
                    "Sieve Size",
                    options=list(psd_calc.SIEVE_OPENING_IN.keys()),
                    required=True
                ),
                "Sand Weight (g)": st.column_config.NumberColumn(
                    "Sand Weight (g)",
                    min_value=0.0,
                    step=0.01,
                    format="%.4f"
                ),
            }
        )

        st.session_state.sieve_input = sieve_input

    # =========================
    # CALCULATION
    # =========================
    sieve_df, psd_summary, psd_warnings = psd_calc.calculate_sieve_analysis(sieve_input)

    st.session_state.psd_summary = psd_summary

    for warning in psd_warnings:
        st.warning(warning)

    # =========================
    # CALCULATED SIEVE TABLE
    # =========================
    with st.expander("Calculated Sieve Table", expanded=False):
        st.dataframe(
            sieve_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sieve Opening (in)": st.column_config.NumberColumn(format="%.5f"),
                "Sand Weight (g)": st.column_config.NumberColumn(format="%.4f"),
                "Cum Weight (g)": st.column_config.NumberColumn(format="%.4f"),
                "Cum % Retained": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    # =========================
    # PSD SUMMARY
    # =========================
    main_psd_keys = [
        "Total Weight (g)",
        "D10 (in)",
        "D40 (in)",
        "D50 (in)",
        "D90 (in)",
        "D95 (in)",
        "UC (D40/D90)",
        "SC (D10/D95)",
        "Fines (%)",
    ]

    def format_psd_value(key, value):
        if value is None:
            return "-"

        if isinstance(value, str):
            return value

        if pd.isna(value):
            return "-"

        if "Weight" in key:
            return f"{value:.2f} g"

        elif "(in)" in key:
            return f"{value:.5f} in."

        elif "(%)" in key:
            return f"{value:.2f}%"

        else:
            return f"{value:.2f}"

    summary_df = pd.DataFrame({
        "Parameter": main_psd_keys,
        "Value": [
            format_psd_value(key, psd_summary.get(key, None))
            for key in main_psd_keys
        ]
    })

    with st.expander("PSD Summary", expanded=True):
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )

    # =========================
    # RECOMMENDED GRAVEL SCREEN
    # =========================
    screen_df = pd.DataFrame({
        "Parameter": [
            "Recommended Gravel Size",
            "Recommended Gravel Screen Type",
            "Recommended GP Slot Width"
        ],
        "Value": [
            psd_summary.get("Recommended Gravel Size", "-"),
            psd_summary.get("Recommended Gravel Screen Type", "-"),
            (
                "-"
                if pd.isna(psd_summary.get("Recommended GP Slot Width (in)", None))
                else f'{psd_summary["Recommended GP Slot Width (in)"]:.3f} in.'
            )
        ]
    })

    with st.expander("Recommended Gravel Screen", expanded=True):
        st.dataframe(
            screen_df,
            use_container_width=True,
            hide_index=True
        )

    # =========================
    # PSD VALUES USED FOR SELECTION
    # =========================
    uc = psd_summary.get("UC (D40/D90)", np.nan)
    sc = psd_summary.get("SC (D10/D95)", np.nan)
    fines = psd_summary.get("Fines (%)", np.nan)    

    with st.expander("PSD Values Used in Sand Control Evaluation", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "UC (D40/D90)",
                "-" if not np.isfinite(uc) else f"{uc:.2f}"
            )

        with col2:
            st.metric(
                "SC (D10/D95)",
                "-" if not np.isfinite(sc) else f"{sc:.2f}"
            )

        with col3:
            st.metric(
                "Fines (%)",
                "-" if not np.isfinite(fines) else f"{fines:.2f}%"
            )

    # =========================
    # FALLBACK INPUT
    # =========================
    if not np.isfinite(uc):
        st.warning("UC cannot be calculated. Check whether D40 and D90 are inside the sieve data range.")
        uc = st.number_input("Manual UC Fallback", value=5.0)

    if not np.isfinite(fines):
        st.warning("Fines cannot be calculated. Manual fines input is required.")
        fines = st.number_input("Manual Fines Fallback (%)", value=0.0)

    # =========================
    # SIEVE ANALYSIS PLOT
    # =========================
    plot_df = sieve_df[
        sieve_df["Sieve Opening (in)"].notna()
        & (sieve_df["Sieve Opening (in)"] > 0)
    ].copy()

    with st.expander("Sieve Analysis Plot", expanded=False):

        if not plot_df.empty:
            fig, ax = plt.subplots(figsize=(7, 4))

            ax.plot(
                plot_df["Sieve Opening (in)"],
                plot_df["Cum % Retained"],
                marker="o"
            )

            ax.set_xscale("log")
            ax.invert_xaxis()
            ax.set_xlabel("Paticle Size Diameter (in)")
            ax.set_ylabel("Cumulative Retained (%)")
            ax.set_title("Particle Size Distribution")
            ax.grid(True, which="both")

            st.pyplot(fig)

        else:
            st.info("No valid sieve opening data available for plotting.")


# COMPLETION
# =========================
with tab4:
    st.subheader("Completion & Operational")

    col1, col2 = st.columns(2)

    with col1:
        completion = st.selectbox("Well Type", ["NEW", "OLD"])
        hole = st.selectbox("Hole Type", ["Cased Hole", "Open Hole"])
        inclination = st.number_input("Inclination (deg)", value=80.0)

    with col2:
        depth_perf = st.number_input("Length Perfo (ft)", value=25.0)
        well_issue = st.selectbox("Well Integrity Issue?", ["No", "Yes"])
        cement = st.selectbox("Cement Bonding Good?", ["Yes", "No"])

# =========================
# RESERVOIR & ECONOMICS
# =========================
with tab5:
    st.subheader("Reservoir Properties")

    col1, col2, col3 = st.columns(3)

    with col1:
        perm = st.number_input("Permeability (mD)", value=260.0)
        clay = st.number_input("Clay Mineral (%)", value=2.0)

    with col2:
        pressure = st.number_input("Pressure (psi)", value=708.0)
        temp = st.number_input("Temperature (°F)", value=180.0)


 
# =========================
# ECONOMICS INPUT
# =========================
# =========================
# ECONOMICS INPUT
# =========================
with tab6:
    st.subheader("Economic Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        rate = st.number_input("Production Rate (bopd)", value=178.0)

    with col2:
        oil_price = st.number_input("Oil Price ($/bbl)", value=70.0)

    with col3:
        opex = st.number_input("Operating Cost ($/year)", value=1000.0)

    Qo_oil = rate
    st.markdown("---")
    st.subheader("Fixed Cost per ft Assumption")

    st.metric(
        label="Perforation Length",
        value=f"{depth_perf:.2f} ft"
    )

    fixed_cost_df = pd.DataFrame([
        {
            "Method": method,
            "Fixed Cost per ft ($/ft)": cost,
        }
        for method, cost in economics.FIXED_COST_PER_FT.items()
    ])

    st.dataframe(
        fixed_cost_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fixed Cost per ft ($/ft)": st.column_config.NumberColumn(
                "Fixed Cost per ft ($/ft)",
                format="$%,.2f"
            )
        }
    )
# =========================
# RUN BUTTON
# =========================
with st.sidebar:
    run = st.button("Run Analysis")

    if run:
        st.session_state.run_triggered = True

# =========================
# OUTPUT
# =========================
# =========================
# OUTPUT (PINDAH KE TAB RESULTS)
# =========================
with tab7:
    st.subheader("Analysis Results")

    if st.session_state.run_triggered:

   # =========================
        # FORMATION SUMMARY CALCULATION
        # =========================
        F_val, m, cementation_level = formation.calculate_cementation(phi, Ro, Rw)
        strength = formation.calculate_formation_strength(Vclay, rho_b, dts)

        if strength:
            G = strength["Shear Modulus"]
            G_Cb = strength["Formation Strength Index (G/Cb)"]
        else:
            G = 0
            G_Cb = None

        Qz = formation.calculate_critical_rate(k, Nz, G, Bz, mu)

        # =========================
        # SANDING SCREENING
        # =========================
        sanding_flag = is_sanding_risk(
            uc=uc,
            fines=fines,
            production_target=rate,
            critical_rate=Qz
        )

        if not sanding_flag:
            st.warning(
                f"No sanding risk detected → UC = {uc:.2f}, Fines = {fines:.2f}%, "
                f"Production Target = {rate:.2f} BOPD, and Qz = {Qz:.2f} BOPD"
            )
            st.stop()

        st.success(
            f"Sanding risk detected → UC = {uc:.2f}, Fines = {fines:.2f}%, "
            f"Production Target = {rate:.2f} BOPD, Qz = {Qz:.2f} BOPD"
        )

        df_summary = pd.DataFrame({
            "Variable": [
                "Formation Factor",
                "Cementation Exponent",
                "Critical Rate",
                "Formation Strength (G)"
            ],
            "Value": [
                f"{F_val:.3f}",
                f"{m:.3f}",
                f"{Qz:.5f}",
                f"{G:.2e}" if G_Cb else "N/A"
            ],
            "Remark": [
                "-",
                cementation_level,
                "BOPD",
                "psi"
            ]
        })

        st.subheader("Formation Summary")
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        # TECH RESULT
        clay_res = evaluate_clay(swelling)
        psd_res = evaluate_psd(uc, fines)
        comp_res = evaluate_completion(rate, inclination)
        chem_res = evaluate_chemical(rate, clay, fines, completion, hole, cement, depth_perf, temp)

        psd_remark = remark_psd(psd_res)
        comp_remark = remark_completion(comp_res)
        chem_remark = remark_chemical(chem_res)

        df = pd.DataFrame({
            "Variable": ["Base on Clay Content", "Base on Sand Sieve Analysis", "Base on Completion & Production", "Chemical Sand Consolidation"],
            "Recommendation": [clay_res, psd_res, comp_res, chem_res],
            "Remark": ["-", psd_remark, comp_remark, chem_remark]
        })

        st.subheader("Sand Control Evaluation")
        st.dataframe(df, use_container_width=True)
        
        # =========================
        # RECOMMENDED METHODS
        # =========================
        recommended_methods = [
            psd_res,
            comp_res,
            chem_res
        ]

        method_mapping = {
            "SAS Wire Wrapped": "SAS Wire-Wrap",
            "SAS Premium Mesh": "SAS Premium Mesh",
            "Gravel Pack": "Gravel Pack",
            "Resin Sand Consolidation": "Resin Consolidation",
            "Polymer Sand Consolidation": "Polymer Sand Consolidation",
            "Frac Pack / Chemical Sand Control": "Frac Pack", 
        }

        filtered_methods = []
        for m in recommended_methods:
            if m in method_mapping:
                filtered_methods.append(method_mapping[m])

       # =========================
       # =========================
        # ECONOMICS - LENGTH-BASED COST
        # =========================
        gp = economics.cost_by_perfo_length(
            method="Gravel Pack",
            length_perfo=depth_perf
        )

        wire = economics.cost_by_perfo_length(
            method="SAS Wire-Wrap",
            length_perfo=depth_perf
        )

        sas = economics.cost_by_perfo_length(
            method="SAS Premium Mesh",
            length_perfo=depth_perf
        )

        polymer = economics.cost_by_perfo_length(
            method="Polymer Sand Consolidation",
            length_perfo=depth_perf
        )

        resin = economics.cost_by_perfo_length(
            method="Resin Consolidation",
            length_perfo=depth_perf
        )

        frac = economics.cost_by_perfo_length(
            method="Frac Pack",
            length_perfo=depth_perf
        )

        df_cost = pd.DataFrame([
        {
            "Method": gp["Method"],
            "Length Perfo (ft)": gp["Length Perfo (ft)"],
            "Cost per ft": gp["Cost per ft"],
            "Total Cost": gp["Total Cost"]
        },
        {
            "Method": sas["Method"],
            "Length Perfo (ft)": sas["Length Perfo (ft)"],
            "Cost per ft": sas["Cost per ft"],
            "Total Cost": sas["Total Cost"]
        },
        {
            "Method": polymer["Method"],
            "Length Perfo (ft)": polymer["Length Perfo (ft)"],
            "Cost per ft": polymer["Cost per ft"],
            "Total Cost": polymer["Total Cost"]
        },
        {
            "Method": resin["Method"],
            "Length Perfo (ft)": resin["Length Perfo (ft)"],
            "Cost per ft": resin["Cost per ft"],
            "Total Cost": resin["Total Cost"]
        },
        {
            "Method": wire["Method"],
            "Length Perfo (ft)": wire["Length Perfo (ft)"],
            "Cost per ft": wire["Cost per ft"],
            "Total Cost": wire["Total Cost"]
        },
        {
            "Method": frac["Method"],
            "Length Perfo (ft)": frac["Length Perfo (ft)"],
            "Cost per ft": frac["Cost per ft"],
            "Total Cost": frac["Total Cost"]
        }
    ])

        # =========================
        # PAYOUT PERIOD
        # =========================
        df_cost["Payout Time (year)"] = df_cost["Total Cost"].apply(
            lambda cost: payout.payout_period(
                capex=cost,
                Qo=Qo_oil,
                price=oil_price,
                opex=opex
            )
        )

        # FILTER BASED ON RECOMMENDATION
        df_filtered = df_cost[df_cost["Method"].isin(filtered_methods)].copy()

        if df_filtered.empty:
            st.error("No economic method matched the technical recommendation. Check method_mapping and df_cost method names.")
            st.stop()

        df_sorted = df_filtered.sort_values(by="Payout Time (year)").reset_index(drop=True)
        df_sorted.index = df_sorted.index + 1

  # =========================
        # DISPLAY TABLE WITHOUT COST BASIS
        # =========================
        df_display = df_sorted[
            [
                "Method",
                "Length Perfo (ft)",
                "Cost per ft",
                "Total Cost",
                "Payout Time (year)"
            ]
        ]

        st.subheader("Cost and Payout Ranking")
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Length Perfo (ft)": st.column_config.NumberColumn(
                    "Length Perfo",
                    format="%.2f ft"
                ),
                "Cost per ft": st.column_config.NumberColumn(
                    "Cost per ft",
                    format="$%,.2f"
                ),
                "Total Cost": st.column_config.NumberColumn(
                    "Total Cost",
                    format="$%,.2f"
                ),
                "Payout Time (year)": st.column_config.NumberColumn(
                    "Payout Time",
                    format="%.2f years"
                )
            }
        )
        best = df_sorted.iloc[0]
        # ===== SAVE HISTORY =====
        st.session_state.history = [
            h for h in st.session_state.history if h["Well Name"] != well_name
        ]

        st.session_state.history.append({
            "Well Name": well_name,
            "Best Method": best["Method"],
            "Total Cost": best["Total Cost"],
            "Payout Time (year)": best["Payout Time (year)"]
        })

        # ===== DISPLAY HISTORY =====
        # ===== DISPLAY HISTORY =====
        st.subheader("Best Method History")

        def format_payout_time(value):
            if value is None or pd.isna(value):
                return "-"
            if value == float("inf"):
                return "No payout"
            return f"{value:.2f} years"

        # header
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 1])
        col1.write("Well Name")
        col2.write("Method")
        col3.write("Cost")
        col4.write("Payout Time")
        col5.write("Delete")

        # rows
        for i, row in enumerate(st.session_state.history):
            c1, c2, c3, c4, c5 = st.columns([3, 3, 3, 3, 1])

            c1.write(row["Well Name"])
            c2.write(row["Best Method"])
            c3.write(f"${row['Total Cost']:,.2f}")
            c4.write(format_payout_time(row.get("Payout Time (year)")))

            if c5.button("🗑", key=f"delete_{i}"):
                st.session_state.history.pop(i)
                st.rerun()