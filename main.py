
import streamlit as st
import pandas as pd
from material_data import load_materials, find_materials_by_names
from antenna_calc import calculate_patch_dimensions
from ui_components import show_material_props, filter_materials
from plotting import plot_antenna_geometry, plot_antenna_3d
from tissue_checker import load_tissue_data, check_compatibility

# -----------------------------------
# Component-specific restrictions
# -----------------------------------
component_materials = {
    "Substrate": ["FR4", "Rogers RO4003C", "Taconic TLY-5", "Alumina", "PTFE", "Ceramic", "FR-4"],
    "Patch": ["Copper", "Silver", "Gold", "Aluminum","FR-4"],
    "Ground": ["Copper", "Silver", "Gold", "Aluminum","FR-4"]
}

# -----------------------------------
# App config
# -----------------------------------
st.set_page_config(page_title="Antenna Designer", page_icon="📡", layout="centered")
st.title("📡 Microstrip Patch Antenna Dimension Calculator")

# Load materials
df = load_materials("cst_materials_extracted.csv")
if df is None:
    st.warning("CSV file not found or failed to load.")
    st.stop()

# Load tissue dataset
tissue_df = load_tissue_data("tissues_properties.csv")

# -----------------------------------
# Mode Selection
# -----------------------------------
mode = st.radio("Choose Calculation Mode:", [
    "Standard Patch Calculator Mode",
    "Design-Oriented Mode",
    "Tissue Compatibility Checker"
])

# ===================================
# 🔹 Standard Mode
# ===================================
if mode == "Standard Patch Calculator Mode":
    st.markdown("### 📁 Choose Materials for Components")
    substrate_list = df['Filename'].tolist()
    patch_materials = find_materials_by_names(df, component_materials["Patch"])
    ground_materials = find_materials_by_names(df, component_materials["Ground"])

    substrate_choice = st.selectbox("Substrate Material", substrate_list)
    patch_choice = st.selectbox("Patch Material", patch_materials)
    ground_choice = st.selectbox("Ground Material", ground_materials)

    with st.expander("🔍 Selected Material Properties"):
        show_material_props(df[df['Filename'] == substrate_choice].iloc[0], "Substrate")
        show_material_props(df[df['Filename'] == patch_choice].iloc[0], "Patch")
        show_material_props(df[df['Filename'] == ground_choice].iloc[0], "Ground")

    st.markdown("### 📥 Enter Design Parameters")
    freq = st.number_input("Operating Frequency (GHz)", min_value=0.1, max_value=100.0, value=2.4, step=0.1)
    h_mm = st.number_input("Substrate Height (mm)", min_value=0.1, max_value=10.0, value=1.6, step=0.1)

    if st.button("Calculate"):
        fr = freq * 1e9
        h = h_mm / 1000
        epsilon = df[df['Filename'] == substrate_choice].iloc[0]['Epsilon']

        L, W, g_len, g_wid, fx, fy = calculate_patch_dimensions(fr, h, epsilon)

        st.success("📐 Patch Dimensions")
        st.write(f"📏 Width (W): `{W} mm`")
        st.write(f"📐 Length (L): `{L} mm`")
        st.write(f"📦 Ground Plane: `{g_len} mm x {g_wid} mm`")
        st.write(f"📍 Feed Point: `({fx}, {fy}) mm`")

        plot_antenna_geometry(L, W, g_len, g_wid, fx, fy)

# ===================================
# 🔹 Design-Oriented Mode (till 8 GHz)
# ===================================
elif mode == "Design-Oriented Mode":
    st.markdown("### 🎯 Design with Component-Specific Material Restrictions")

    substrate_df = filter_materials(df, component_materials["Substrate"])
    patch_df = filter_materials(df, component_materials["Patch"])
    ground_df = filter_materials(df, component_materials["Ground"])

    if substrate_df.empty or patch_df.empty or ground_df.empty:
        st.error("No materials found matching the component restrictions. Please check your CSV and restrictions.")
        st.stop()

    substrate_choice = st.selectbox("Substrate Material", substrate_df['Filename'].tolist())
    patch_choice = st.selectbox("Patch Material", patch_df['Filename'].tolist())
    ground_choice = st.selectbox("Ground Material", ground_df['Filename'].tolist())

    st.markdown("### 📊 Selected Material Properties")
    show_material_props(df[df['Filename'] == substrate_choice].iloc[0], "Substrate")
    show_material_props(df[df['Filename'] == patch_choice].iloc[0], "Patch")
    show_material_props(df[df['Filename'] == ground_choice].iloc[0], "Ground")

    st.markdown("### 📥 Enter Design Parameters")
    freq = st.number_input("Frequency (GHz)", min_value=1.0, max_value=8.0, value=2.4, step=0.1)
    h_mm = st.number_input("Substrate Height (mm)", min_value=0.5, max_value=5.0, value=1.6, step=0.1)

    if st.button("Calculate Design"):
        fr = freq * 1e9
        h = h_mm / 1000
        epsilon_sub = df[df['Filename'] == substrate_choice].iloc[0]['Epsilon']
        L, W, g_len, g_wid, fx, fy = calculate_patch_dimensions(fr, h, epsilon_sub)

        warnings = []
        if L > 50:
            warnings.append(f"⚠️ Patch Length ({L} mm) exceeds recommended max of 50 mm")
        if W > 50:
            warnings.append(f"⚠️ Patch Width ({W} mm) exceeds recommended max of 50 mm")

        st.success("📐 Design Calculated with Constraints")
        st.write(f"📏 Width (W): `{W} mm`")
        st.write(f"📐 Length (L): `{L} mm`")
        st.write(f"📦 Ground Plane: `{g_len} mm x {g_wid} mm`")
        st.write(f"📍 Feed Point: `({fx}, {fy}) mm`")

        for w in warnings:
            st.warning(w)

        plot_antenna_3d(L, W, g_len, g_wid, fx, fy, h_mm)

# ===================================
# 🔹 Tissue Compatibility Checker
# ===================================
elif mode == "Tissue Compatibility Checker":
    st.header("🧪 Dielectric Tissue Compatibility Checker")

    unique_tissues = sorted(tissue_df['tissue'].unique())
    tissue_choice = st.selectbox("Select Tissue/Organ", unique_tissues)

    permittivity = st.number_input("Enter measured Permittivity", min_value=0.0, value=1.0, format="%.4f")
    elec_cond = st.number_input("Enter measured Electrical Conductivity (S/m)", min_value=0.0, value=0.1, format="%.4f")
    freq = st.number_input("Operating Frequency (GHz)", min_value=0.1, max_value=10.0, value=2.4, format="%.3f")
    threshold = st.number_input("Tolerance Threshold (e.g. 0.15 = 15%)", min_value=0.0, value=0.15, format="%.2f")

    if st.button("Check Compatibility"):
        compatible, diffs, avg_diff, fig = check_compatibility(
            tissue_df, tissue_choice, permittivity, elec_cond, freq, threshold
        )

        if compatible is None:
            st.error(f"No data found for tissue '{tissue_choice}'.")
        else:
            st.markdown(f"### Results for {tissue_choice}:")
            fields = ['permittivity', 'elec_cond']
            matching_rows = tissue_df[tissue_df['tissue'].str.lower() == tissue_choice.lower()]
            if matching_rows.empty:
                st.error("No matching tissue data found.")
                st.stop()

            row = matching_rows.iloc[(matching_rows['frequency'] - freq).abs().argsort().iloc[0]]

            for i, field in enumerate(fields):
                user_val = permittivity if field == 'permittivity' else elec_cond
                st.write(
                    f" - **{field.capitalize()}**: Your value = {user_val}, Reference = {row[field]:.4f} → "
                    f"{'✅ Compatible' if diffs[i] <= threshold else '❌ Not compatible'} (Δ {diffs[i]*100:.2f}%)"
                )

            st.write(f"**Overall similarity score:** {max(0, 100 - avg_diff * 100):.2f}%")
            st.write("✅ Compatible!" if compatible else "❌ Not compatible.")
            st.pyplot(fig)
