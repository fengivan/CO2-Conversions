"""Expanded compositional property calculator using CoolProp."""

import math

import pandas as pd
import streamlit as st
from CoolProp.CoolProp import PropsSI


st.set_page_config(page_title="Compositional Properties", layout="centered")
st.header("Compositional Properties")

# Keep display names separate from CoolProp's fluid identifiers.
COMPONENTS = [
    ("CO2", "CO2"),
    ("H2S", "HydrogenSulfide"),
    ("Methane (CH4)", "Methane"),
    ("Ethane (C2H6)", "Ethane"),
    ("Propane (C3H8)", "Propane"),
    ("Isobutane (i-C4)", "IsoButane"),
    ("n-Butane (n-C4)", "n-Butane"),
    ("Isopentane (i-C5)", "Isopentane"),
    ("n-Pentane (n-C5)", "n-Pentane"),
    ("Hexanes plus (C6+)", "n-Hexane"),
    ("Nitrogen (N2)", "Nitrogen"),
]

st.write("**Temperature and Pressure**")
temperature = st.number_input(
    "Temperature (°F)", min_value=32.0, max_value=1000.0, value=80.0
)
pressure = st.number_input(
    "Pressure (psia)", min_value=1.0, max_value=20000.0, value=1400.0
)
st.caption(
    "Enter mole percentages, mole fractions, or relative molar amounts. "
    "Inputs are normalized to a total mole fraction of 1."
)
st.info(
    "Hexanes plus (C6+) is modeled as n-hexane. This is an approximation, "
    "not a characterized heavy fraction; results depend on the actual C6+ composition."
)

input_column, summary_column = st.columns(2)
amounts = {}
with input_column:
    st.write("**Gas Composition (Molar Basis)**")
    for label, fluid in COMPONENTS:
        amounts[fluid] = st.number_input(
            label,
            min_value=0.0,
            max_value=100000.0,
            value=100.0 if fluid == "CO2" else 0.0,
            format="%.6f",
            key=f"composition_{fluid}",
        )

total = sum(amounts.values())
if not math.isfinite(total) or total <= 0:
    st.warning("Enter a positive amount for at least one gas component.")
    st.stop()

fractions = {fluid: amount / total for fluid, amount in amounts.items()}
# Exclude absent components so unused binary pairs cannot affect the calculation.
mixture = "&".join(
    f"{fluid}[{fraction:.16g}]"
    for fluid, fraction in fractions.items()
    if fraction > 0
)
with summary_column:
    st.write("**Summary of Inputs**")
    st.dataframe(
        pd.DataFrame(
            {
                "Parameter": ["Temperature", "Pressure"]
                + [label for label, _ in COMPONENTS],
                "Value": [temperature, pressure]
                + [fractions[fluid] for _, fluid in COMPONENTS],
                "Unit": ["°F", "psia"] + ["mole fraction"] * len(COMPONENTS),
            }
        ),
        hide_index=True,
    )

temperature_k = (temperature + 459.67) / 1.8
pressure_pa = pressure * 6894.76


def property_value(output, temp_k=temperature_k, pres_pa=pressure_pa, fluid=mixture):
    """Report unavailable properties without discarding other valid results."""
    try:
        value = PropsSI(output, "T", temp_k, "P", pres_pa, fluid)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("The calculated property is not finite and positive.")
        return value
    except (ValueError, RuntimeError) as error:
        st.warning(
            f"{output} could not be calculated at {temp_k:.2f} K and "
            f"{pres_pa / 6894.76:.2f} psia. CoolProp may not support this "
            "composition or phase at the selected conditions."
        )
        with st.expander(f"Calculation details: {output}"):
            st.text(str(error))
        return None


st.header("Results")
density = property_value("D")
if density is not None:
    st.write(f"Density (g/L): {density:.6g}")
    st.write(f"Density (Metric Ton/BBL): {density * 0.000158987294928:.6g}")
    st.write(f"Density (lb/gallon): {density * 0.00834540445:.6g}")

viscosity = property_value("VISCOSITY")
if viscosity is not None:
    st.write(f"Viscosity (cP): {1000 * viscosity:.6g}")

heat_capacity = property_value("Cpmass")
if heat_capacity is not None:
    st.write(f"Heat Capacity Cp (J/kg-K): {heat_capacity:.6g}")

if density is not None:
    base_density = property_value("D", (60 + 459.67) / 1.8, 14.65 * 6894.76)
    if base_density is not None:
        density_ratio = density / base_density
        st.write(f"Gas FVF (actual volume/base volume): {1 / density_ratio:.6g}")
        st.write(f"Density ratio (operating/base): {density_ratio:.6g}")
        st.caption(
            "Base conditions: 60°F and 14.65 psia. The existing calculator's "
            "‘Gas FVF’ is the operating/base density ratio, the inverse of "
            "the volume-based FVF shown here."
        )
        co2_density = property_value("D", fluid="CO2[1]")
        if co2_density is not None:
            equivalent_co2 = co2_density / density_ratio * 28316.846592
            st.write(f"Eq CO2 (Metric Ton/BCF): {equivalent_co2:.6g}")
            st.caption(
                "Equivalent pure CO2 mass occupying the same operating volume "
                "as 1 BCF of this mixture at base conditions; not the mixture's CO2 content."
            )

st.divider()
st.markdown("[CoolProp mixture documentation](https://coolprop.org/fluid_properties/Mixtures.html)")
