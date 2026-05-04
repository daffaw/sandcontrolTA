import numpy as np
import pandas as pd


SIEVE_OPENING_IN = {
    "10": 0.0787,
    "12": 0.0661,
    "14": 0.0555,
    "16": 0.0469,
    "18": 0.0394,
    "20": 0.0331,
    "25": 0.0280,
    "30": 0.0232,
    "35": 0.0197,
    "40": 0.0165,
    "45": 0.0138,
    "50": 0.0117,
    "60": 0.0098,
    "70": 0.0083,
    "80": 0.0070,
    "100": 0.0059,
    "120": 0.0049,
    "140": 0.0041,
    "170": 0.0035,
    "200": 0.0029,
    "230": 0.0025,
    "270": 0.0021,
    "325": 0.0017,
    "Pan": np.nan,
}


def default_sieve_table():
    return pd.DataFrame({
        "Sieve Size": ["20", "30", "45", "50", "60", "80", "100", "200", "325", "Pan"],
        "Sand Weight (g)": [0.07, 0.39, 1.75, 0.81, 1.56, 3.44, 2.06, 2.68, 0.80, 1.14],
    })


def _interpolate_d_value(df, target_percent):
    valid = df.copy()

    # Assign pseudo opening for Pan only for interpolation purpose
    pan_opening_assumption = 0.0010

    valid["Opening for Interpolation"] = valid["Sieve Opening (in)"]

    valid.loc[
        valid["Sieve Size"].astype(str).str.lower() == "pan",
        "Opening for Interpolation"
    ] = pan_opening_assumption

    valid = valid[
        valid["Opening for Interpolation"].notna()
        & (valid["Opening for Interpolation"] > 0)
        & valid["Cum % Retained"].notna()
    ].copy()

    if valid.empty:
        return np.nan

    valid = valid.sort_values("Cum % Retained")

    y = valid["Cum % Retained"].to_numpy(dtype=float)
    x = valid["Opening for Interpolation"].to_numpy(dtype=float)

    if target_percent < y.min() or target_percent > y.max():
        return np.nan

    log_d = np.interp(target_percent, y, np.log10(x))
    return 10 ** log_d


def _nearest_mesh(opening_in):
    if not np.isfinite(opening_in) or opening_in <= 0:
        return None

    sieve_only = {
        mesh: opening
        for mesh, opening in SIEVE_OPENING_IN.items()
        if mesh != "Pan" and np.isfinite(opening)
    }

    return min(
        sieve_only.keys(),
        key=lambda mesh: abs(sieve_only[mesh] - opening_in)
    )
def _recommend_gravel_screen(d50):
    """
    First-pass gravel pack screen recommendation based on D50.
    Final slot width should still be checked against actual gravel supplier and screen vendor catalog.
    """

    if not np.isfinite(d50) or d50 <= 0:
        return {
            "Recommended Gravel Size": "-",
            "Recommended Gravel Screen Type": "-",
            "Recommended GP Slot Width (in)": np.nan,
            "Recommended Prepacked Slot Width (in)": np.nan,
            "Standalone Screen Slot Width Min (in)": np.nan,
            "Standalone Screen Slot Width Max (in)": np.nan,
        }

    d50_4 = 4 * d50
    d50_6 = 6 * d50
    d50_8 = 8 * d50

    mid_mesh = _nearest_mesh(d50_6)

    if mid_mesh is None:
        gravel_size = "-"
        gp_slot = np.nan

    else:
        mid_mesh_num = int(mid_mesh)

        # Simple commercial gravel-size mapping.
        # This can be adjusted to match the gravel supplier catalog.
        if mid_mesh_num <= 14:
            gravel_size = "12-20 U.S. Mesh"
            gp_slot = 0.030

        elif 14 < mid_mesh_num <= 25:
            gravel_size = "16-30 U.S. Mesh"
            gp_slot = 0.020

        elif 25 < mid_mesh_num <= 35:
            gravel_size = "20-40 U.S. Mesh"
            gp_slot = 0.012

        elif 35 < mid_mesh_num <= 45:
            gravel_size = "30-50 U.S. Mesh"
            gp_slot = 0.010

        elif 45 < mid_mesh_num <= 60:
            gravel_size = "40-60 U.S. Mesh"
            gp_slot = 0.008

        else:
            gravel_size = "50-70 U.S. Mesh"
            gp_slot = 0.006

    # For standalone screen without gravel pack.
    # This is a practical first-pass range based on formation sand D50.
    standalone_min = 2.5 * d50
    standalone_max = 5.0 * d50

    return {
        "Recommended Gravel Size": gravel_size,
        "Recommended Gravel Screen Type": "Gravel Pack Wire Wrapped Screen",
        "Recommended GP Slot Width (in)": gp_slot,
        "Recommended Prepacked Slot Width (in)": gp_slot,
        "Standalone Screen Slot Width Min (in)": standalone_min,
        "Standalone Screen Slot Width Max (in)": standalone_max,
    }


def _recommend_gravel_size(d50):
    if not np.isfinite(d50) or d50 <= 0:
        return {
            "Recommended Gravel Size": "-",
            "Recommended Gravel Screen Type": "-",
            "Recommended GP Slot Width (in)": np.nan,
            "Recommended Prepacked Slot Width (in)": np.nan,
            "Standalone Screen Slot Width Min (in)": np.nan,
            "Standalone Screen Slot Width Max (in)": np.nan,
        }

    gravel_mid = 6 * d50
    mid_mesh = _nearest_mesh(gravel_mid)

    if mid_mesh is None:
        gravel_size = "-"
        gp_slot = np.nan
    else:
        mid_mesh_num = int(mid_mesh)

        if mid_mesh_num <= 14:
            gravel_size = "12-20 U.S. Mesh"
            gp_slot = 0.030

        elif 14 < mid_mesh_num <= 25:
            gravel_size = "16-30 U.S. Mesh"
            gp_slot = 0.020

        elif 25 < mid_mesh_num <= 35:
            gravel_size = "20-40 U.S. Mesh"
            gp_slot = 0.012

        elif 35 < mid_mesh_num <= 45:
            gravel_size = "30-50 U.S. Mesh"
            gp_slot = 0.010

        elif 45 < mid_mesh_num <= 60:
            gravel_size = "40-60 U.S. Mesh"
            gp_slot = 0.008

        else:
            gravel_size = "50-70 U.S. Mesh"
            gp_slot = 0.006

    standalone_min = 2.5 * d50
    standalone_max = 5.0 * d50

    return {
        "Recommended Gravel Size": gravel_size,
        "Recommended Gravel Screen Type": "Gravel Pack Wire Wrapped Screen",
        "Recommended GP Slot Width (in)": gp_slot,
        "Recommended Prepacked Slot Width (in)": gp_slot,
        "Standalone Screen Slot Width Min (in)": standalone_min,
        "Standalone Screen Slot Width Max (in)": standalone_max,
    }


def calculate_sieve_analysis(raw_df):
    warnings = []

    df = raw_df.copy()

    if "Sieve Size" not in df.columns:
        raise ValueError("Column 'Sieve Size' is required.")

    if "Sand Weight (g)" not in df.columns:
        raise ValueError("Column 'Sand Weight (g)' is required.")

    df["Sieve Size"] = df["Sieve Size"].astype(str).str.strip()
    df = df[df["Sieve Size"].isin(SIEVE_OPENING_IN.keys())].copy()

    if df.empty:
        raise ValueError("No valid sieve data found.")

    if df["Sieve Size"].duplicated().any():
        warnings.append("Duplicate sieve sizes were found. The last value is used.")
        df = df.drop_duplicates(subset="Sieve Size", keep="last")

    df["Sieve Opening (in)"] = df["Sieve Size"].map(SIEVE_OPENING_IN)
    df["Sand Weight (g)"] = pd.to_numeric(df["Sand Weight (g)"], errors="coerce").fillna(0.0)

    if (df["Sand Weight (g)"] < 0).any():
        warnings.append("Negative sand weight was found and converted to zero.")
        df.loc[df["Sand Weight (g)"] < 0, "Sand Weight (g)"] = 0.0

    if "Pan" not in df["Sieve Size"].values:
        warnings.append("Pan is not included. Fines content cannot represent material passing the finest sieve.")

    df["_sort_key"] = df["Sieve Opening (in)"].fillna(-1)
    df = df.sort_values("_sort_key", ascending=False).drop(columns="_sort_key").reset_index(drop=True)

    total_weight = df["Sand Weight (g)"].sum()

    if total_weight <= 0:
        df["Cum Weight (g)"] = np.nan
        df["Cum % Retained"] = np.nan

        summary = {
            "Total Weight (g)": 0.0,
            "D10 (in)": np.nan,
            "D40 (in)": np.nan,
            "D50 (in)": np.nan,
            "D90 (in)": np.nan,
            "D95 (in)": np.nan,
            "UC (D40/D90)": np.nan,
            "SC (D10/D95)": np.nan,
            "Fines (%)": np.nan,
        }

        summary.update(_recommend_gravel_size(np.nan))
        warnings.append("Total sample weight is zero. PSD calculation cannot be completed.")

        return df, summary, warnings

    df["Cum Weight (g)"] = df["Sand Weight (g)"].cumsum()
    df["Cum % Retained"] = df["Cum Weight (g)"] / total_weight * 100

    d10 = _interpolate_d_value(df, 10)
    d40 = _interpolate_d_value(df, 40)
    d50 = _interpolate_d_value(df, 50)
    d90 = _interpolate_d_value(df, 90)
    d95 = _interpolate_d_value(df, 95)

    pan_weight = df.loc[df["Sieve Size"] == "Pan", "Sand Weight (g)"].sum()
    fines_pct = pan_weight / total_weight * 100

    uc = d40 / d90 if np.isfinite(d40) and np.isfinite(d90) and d90 > 0 else np.nan
    sc = d10 / d95 if np.isfinite(d10) and np.isfinite(d95) and d95 > 0 else np.nan

    summary = {
        "Total Weight (g)": total_weight,
        "D10 (in)": d10,
        "D40 (in)": d40,
        "D50 (in)": d50,
        "D90 (in)": d90,
        "D95 (in)": d95,
        "UC (D40/D90)": uc,
        "SC (D10/D95)": sc,
        "Fines (%)": fines_pct,
    }

    summary.update(_recommend_gravel_size(d50))

    return df, summary, warnings