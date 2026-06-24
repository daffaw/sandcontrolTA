import numpy as np

#Cementation
def calculate_cementation(phi, Ro, Rw):
    """
    Calculate:
    - Formation Factor (F)
    - Cementation Exponent (m)
    - Cementation Level (based on literature ranges)
    """

    # validasi input
    if phi <= 0 or Ro <= 0 or Rw <= 0:
        return 0, 0, "Invalid Input"

    try:
        # 🔥 step 1: formation factor
        F = Ro / Rw

        # 🔥 step 2: cementation exponent
        m = -(np.log(F) / np.log(phi))

    except:
        return 0, 0, "Error"

    # 🔥 step 3: classification (FIXED RANGE)
    if m <= 1.3:
        level = "Very Slightly Cemented"
    
    elif 1.3 < m <= 1.5:
        level = "Slightly Cemented"
    
    elif 1.5 < m <= 1.7:
        level = "Moderately Cemented"
    
    elif 1.7 < m <= 1.9:
        level = "Consolidated Sand"
    
    elif 1.9 < m <= 2.2:
        level = "Highly Cemented"
    
    else:
        level = "Out of Range"

    return F, m, level

#Critical Rate
def calculate_critical_rate(k, Nz, Gz, Bo, Bw, mu_o, mu_w, water_cut):
    """
    Calculate critical sand-free liquid rate using mixed liquid properties.

    Output:
    Qz : float, BFPD
    """

    # =========================
    # INPUT VALIDATION
    # =========================
    if any(v <= 0 for v in [k, Nz, Gz, Bo, Bw, mu_o, mu_w]):
        return 0

    try:
        # =========================
        # WATER CUT FRACTION
        # =========================
        if water_cut < 0:
            water_cut = 0

        if water_cut > 100:
            water_cut = 100

        fw = water_cut / 100
        fo = 1 - fw

        # =========================
        # MIXED LIQUID FVF
        # Bliq = fo * Bo + fw * Bw
        # =========================
        Bliq = (fo * Bo) + (fw * Bw)

        if Bliq <= 0:
            return 0

        # =========================
        # RESERVOIR VOLUME FRACTION
        # =========================
        alpha_o = (fo * Bo) / Bliq
        alpha_w = (fw * Bw) / Bliq

        # =========================
        # MIXED LIQUID VISCOSITY
        # muliq = alpha_o * mu_o + alpha_w * mu_w
        # =========================
        muliq = (alpha_o * mu_o) + (alpha_w * mu_w)

        if muliq <= 0:
            return 0

        # =========================
        # CRITICAL RATE
        # =========================
        Qz = 0.025e-6 * (k * Nz * Gz) / (Bliq * muliq)

    except:
        return 0

    return Qz

#Formation Strength
def calculate_formation_strength(Vclay, rho_b, dts):
    """
    Calculate formation mechanical properties:
    - Poisson's ratio (U)
    - A & B constants
    - Shear modulus (G)
    - Bulk modulus inverse (1/Cb)
    - Formation Strength Index (G/Cb)
    """

    if any(v <= 0 for v in [rho_b, dts]):
        return None

    try:
        # 1. Poisson ratio
        U = 0.125 * Vclay + 0.27

        # 2. A & B
        A = (1 - 2 * U) / (2 * (1 - U))
        B = (1 + U) / (3 * (1 - U))

        # 3. Shear modulus
        G = 1.34e10 * A * (rho_b / (dts ** 2))

        # 4. Bulk modulus inverse
        Cb_inv = 1.34e10 * B * (rho_b / (dts ** 2))

        # 🔥 5. Formation Strength Index (G/Cb)
        strength_index = G * Cb_inv

    except:
        return None

    return {
        "Poisson Ratio": U,
        "A": A,
        "B": B,
        "Shear Modulus": G,
        "Bulk Modulus Inverse": Cb_inv,
        "Formation Strength Index (G/Cb)": strength_index
    }