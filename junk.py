
st.header("Radial Flow Equation")

st.latex(r"""
q = \frac{2 \pi k h (p_r - p_w)}{\mu \ln{\frac{r_e}{r_w}}}
""")


# Inputs for the equation
st.subheader("Input Parameters")
k = st.number_input("Permeability (k) [mD]:", value=1.0, min_value=0.0)
h = st.number_input("Reservoir thickness (h) [ft]:", value=100.0, min_value=0.0)
p_r = st.number_input("Reservoir pressure (p_r) [psi]:", value=10000.0, min_value=0.0)
p_w = st.number_input("Wellbore pressure (p_w) [psi]:", value=11000.0, min_value=0.0)
mu = st.number_input("Fluid viscosity (μ) [cp]:", value=.06, min_value=0.0)
r_e = st.number_input("External radius (r_e) [ft]:", value=5000.0, min_value=0.1)
r_w = st.number_input("Wellbore radius (r_w) [ft]:", value=0.5, min_value=0.1)

# Calculate q
if r_e > r_w:
    try:
        q = .001128*(2 * math.pi * k * h * (p_w - p_r)) / (mu * math.log(r_e / r_w))
        st.subheader("Results")
        st.success(f"Flow Rate (q): {q:,.2f} bbls/day")
    except ZeroDivisionError:
        st.error("Check input values to avoid division by zero.")
else:
    st.error("Ensure that r_e > r_w for valid input.")

