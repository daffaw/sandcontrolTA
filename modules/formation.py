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
def calculate_critical_rate(k, Nz, Gz, Bz, mu):
    """
    Simplified critical rate (Az = At)
    """

    if any(v <= 0 for v in [k, Nz, Gz, Bz, mu]):
        return 0

    try:
        Qz = 0.025e-6 * (k * Nz * Gz) / (Bz * mu)
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