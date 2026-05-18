# =========================
# ECONOMICS MODULE
import math
# =========================
# =========================
# CHEMICAL CONSOLIDATION COST
# =========================

def cost_chemical_consolidation(
    method,
    length_perfo_ft,
    porosity,
    rw_ft,
    rt_ft,
    excess_factor,
    chemical_price_per_gal,
    fixed_treatment_cost,
    min_gal_per_ft,
    max_gal_per_ft
):
    """
    Chemical sand consolidation cost based on radial pore volume.

    Total Cost = Fixed Treatment Cost + Chemical Volume × Chemical Price
    Chemical Volume = pi × Lperf × porosity × (rt^2 - rw^2) × 7.4805 × EF
    """

    if length_perfo_ft < 0:
        length_perfo_ft = 0.0

    if porosity < 0:
        porosity = 0.0

    if rw_ft < 0:
        rw_ft = 0.0

    if rt_ft <= rw_ft:
        rt_ft = rw_ft

    if excess_factor <= 0:
        excess_factor = 1.0

    chemical_volume_gal = (
        math.pi
        * length_perfo_ft
        * porosity
        * (rt_ft**2 - rw_ft**2)
        * 7.4805
        * excess_factor
    )

    if length_perfo_ft > 0:
        gal_per_ft = chemical_volume_gal / length_perfo_ft
    else:
        gal_per_ft = 0.0

    material_cost = chemical_volume_gal * chemical_price_per_gal
    total_cost = fixed_treatment_cost + material_cost

    if gal_per_ft < min_gal_per_ft:
        volume_status = "Below literature range"
    elif gal_per_ft > max_gal_per_ft:
        volume_status = "Above literature range"
    else:
        volume_status = "Within literature range"

    return {
        "Method": method,
        "Length Perfo (ft)": length_perfo_ft,
        "Porosity": porosity,
        "rw (ft)": rw_ft,
        "rt (ft)": rt_ft,
        "Excess Factor": excess_factor,
        "Chemical Volume (gal)": chemical_volume_gal,
        "Chemical Volume (bbl)": chemical_volume_gal / 42.0,
        "Chemical Volume per ft (gal/ft)": gal_per_ft,
        "Literature Min (gal/ft)": min_gal_per_ft,
        "Literature Max (gal/ft)": max_gal_per_ft,
        "Volume Status": volume_status,
        "Chemical Price (USD/gal)": chemical_price_per_gal,
        "Material Cost": material_cost,
        "Fixed Treatment Cost": fixed_treatment_cost,
        "Total Cost": total_cost
    }


def cost_polymer_consolidation(
    length_perfo_ft,
    porosity,
    rw_ft,
    rt_ft=2.0,
    excess_factor=1.0,
    chemical_price_per_gal=33.5,
    fixed_treatment_cost=6140.0
):
    return cost_chemical_consolidation(
        method="Polymer Sand Consolidation",
        length_perfo_ft=length_perfo_ft,
        porosity=porosity,
        rw_ft=rw_ft,
        rt_ft=rt_ft,
        excess_factor=excess_factor,
        chemical_price_per_gal=chemical_price_per_gal,
        fixed_treatment_cost=fixed_treatment_cost,
        min_gal_per_ft=30.0,
        max_gal_per_ft=50.0
    )


def cost_resin_consolidation(
    length_perfo_ft,
    porosity,
    rw_ft,
    rt_ft=3.0,
    excess_factor=1.0,
    chemical_price_per_gal=60.0,
    fixed_treatment_cost=10000.0
):
    return cost_chemical_consolidation(
        method="Resin Consolidation",
        length_perfo_ft=length_perfo_ft,
        porosity=porosity,
        rw_ft=rw_ft,
        rt_ft=rt_ft,
        excess_factor=excess_factor,
        chemical_price_per_gal=chemical_price_per_gal,
        fixed_treatment_cost=fixed_treatment_cost,
        min_gal_per_ft=50.0,
        max_gal_per_ft=80.0
    )
# =========================
# 1. GRAVEL PACK
# =========================
def cost_gravel_pack(chem_pumping, equipment, install):
    total = chem_pumping + equipment + install

    return {
        "Method": "Gravel Pack",
        "Chemical & Pumping": chem_pumping,
        "Equipment": equipment,
        "Install": install,
        "Total Cost": total
    }


# =========================
# 2. SAS (PREMIUM MESH)
# =========================
def cost_sas_wirewrapped(equipment, install):
    total = equipment + install

    return {
        "Method": "SAS Premium Mesh",
        "Equipment": equipment,
        "Install": install,
        "Total Cost": total
    }

#3 Wire Wrapped
def cost_sas(length, price_per_ft=500, base_cost=20000):
    total = (length * price_per_ft) + base_cost
    return {
        "Method": "SAS Wire-Wrap",
        "Total Cost": total
    }

#Frac Pack
def cost_frac_pack(chem, equipment, install):
    total = chem + equipment + install
    return {
        "Method": "Frac Pack",
        "Total Cost": total
    }

# =========================
# 3. POLYMER SAND CONSOLIDATION
# (MATCH EXCEL EXACT)
# =========================
def cost_polymer(thickness, porosity, radius, F, phi):

    # DESIGN
    volume = (thickness * porosity * radius**2 * F * phi) / 5.615

    # TREATMENT
    main = volume * 40
    water = 0.9 * main
    fsg = 0.1 * main

    # COST
    material = 33.5 * fsg
    pumping = 1800
    crew = 7 * 620

    total_cost = material + pumping + crew

    return {
        "Method": "Polymer Sand Consolidation",
        "Volume (bbl)": volume,
        "Main Treatment (gal)": main,
        "Water (gal)": water,
        "FSG (gal)": fsg,
        "Material FSG": material,
        "Pumping": pumping,
        "Crew": crew,
        "Total Cost": total_cost
    }


# =========================
# 4. RESIN SAND CONSOLIDATION (SANDTRAP)
# =========================
def cost_resin(design_values):

    data = [
        {"item": "Batch Mix Skid", "cost": 1484.38},
        {"item": "Technical Engineer", "cost": 4393.75},
        {"item": "Assistant", "cost": 1900},
        {"item": "Sandtrap Services", "cost": 111867.25},
        {"item": "Additional 3 ft", "cost": 31753.75},
        {"item": "Waterweb Services", "cost": 5.19},
    ]

    results = []
    total_cost = 0

    for d in data:
        item = d["item"]
        unit_cost = d["cost"]

        qty = design_values.get(item, 0)

        total = qty * unit_cost

        results.append({
            "Item": item,
            "Qty": qty,
            "Unit Cost": unit_cost,
            "Total": total
        })

        total_cost += total

    return {
        "Method": "Resin Sand Consolidation",
        "Breakdown": results,
        "Total Cost": total_cost
    }

def cost_by_perfo_length(method, length_perfo, reference_cost, reference_length):
    """
    Preliminary sand control cost estimate based on perforation length.

    method           : sand control method name
    length_perfo     : actual perforation length, ft
    reference_cost   : reference cost from literature/table
    reference_length : assumed reference interval length, ft
    """

    if reference_length <= 0:
        reference_length = 1

    if length_perfo < 0:
        length_perfo = 0

    total_cost = reference_cost * (length_perfo / reference_length)

    return {
        "Method": method,
        "Length Perfo (ft)": length_perfo,
        "Reference Cost": reference_cost,
        "Reference Length (ft)": reference_length,
        "Total Cost": total_cost
    }
# =========================
# 5. COST COMPARISON (ALL METHODS)
# =========================
def compare_costs(gp, sas, polymer, resin):

    return [
        {"Method": gp["Method"], "Total Cost": gp["Total Cost"]},
        {"Method": sas["Method"], "Total Cost": sas["Total Cost"]},
        {"Method": polymer["Method"], "Total Cost": polymer["Total Cost"]},
        {"Method": resin["Method"], "Total Cost": resin["Total Cost"]},
    ]
FIXED_COST_PER_FT = {
    "Gravel Pack": 53333.0,
    "SAS Wire-Wrap": 20000.0,
    "SAS Premium Mesh": 36000.0,
    "Polymer Sand Consolidation": 5399.0,
    "Resin Consolidation": 6000.0,
    "Frac Pack": 80000.0,
}


COST_BASIS = {
    "Gravel Pack": "Khamehchi et al. Table 8, normalized by 150 ft interval",
    "SAS Wire-Wrap": "Khamehchi et al. Table 8, normalized by 150 ft interval",
    "SAS Premium Mesh": "Pre-packed screen proxy from Khamehchi et al. Table 8",
    "Polymer Sand Consolidation": "Polymer completion cost reference, normalized by 25 ft default interval",
    "Resin Consolidation": "Fixed chemical sand consolidation screening assumption",
    "Frac Pack": "Conservative frac-pack screening assumption",
}


def cost_by_perfo_length(method, length_perfo):
    """
    Preliminary fixed cost-per-ft model for sand control economics.

    method       : sand control method name
    length_perfo : perforation interval length, ft
    """

    if length_perfo < 0:
        length_perfo = 0

    cost_per_ft = FIXED_COST_PER_FT.get(method, 0.0)
    total_cost = length_perfo * cost_per_ft

    return {
        "Method": method,
        "Length Perfo (ft)": length_perfo,
        "Cost per ft": cost_per_ft,
        "Cost Basis": COST_BASIS.get(method, "Fixed screening assumption"),
        "Total Cost": total_cost
    }