import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# -----------------------------------
# Antenna Material Restrictions (Design Mode Only)
# -----------------------------------
component_materials = {
    "Substrate": ["FR4", "Rogers RO4003C", "Taconic TLY-5", "Alumina", "PTFE", "Ceramic", "FR-4"],
    "Patch": ["Copper", "Silver", "Gold", "Aluminum"],
    "Ground": ["Copper", "Silver", "Gold", "Aluminum"]
}

# -----------------------------------
# Load Material Data with Caching
# -----------------------------------
@st.cache_data(show_spinner=True)
def load_materials(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df = df[['Filename', 'Epsilon', 'Mu', 'TanD', 'Sigma']].dropna(subset=['Epsilon'])
        return df
    except Exception as e:
        st.error(f"❌ Failed to load material data: {e}")
        return None

# -----------------------------------
# Patch Dimension Calculation
# -----------------------------------
def calculate_patch_dimensions(fr, h, epsilon):
    c = 3e8  # Speed of light in m/s

    # Patch width (W)
    W = c / (2 * fr * math.sqrt(epsilon))

    # Effective dielectric constant
    eff_er = (epsilon + 1) / 2 + (epsilon - 1) / 2 * (1 + 12 * h / W) ** -0.5

    # Effective length and extension
    leff = c / (2 * fr * math.sqrt(eff_er))
    delta_L = 0.412 * h * ((eff_er + 0.3) * (W / h + 0.264)) / ((eff_er - 0.258) * (W / h + 0.8))
    L = leff - 2 * delta_L

    # Ground plane dimensions
    ground_plane_length = 6 * h + L
    ground_plane_width = 6 * h + W

    # Feed point (inset feed for simple rectangular patch)
    feed_location_x = W / 2
    feed_location_y = L / 2

    # Convert to mm and round
    return round(L * 1000, 3), round(W * 1000, 3), round(ground_plane_length * 1000, 3), round(ground_plane_width * 1000, 3), round(feed_location_x * 1000, 3), round(feed_location_y * 1000, 3)

# -----------------------------------
# Streamlit UI Layout
# -----------------------------------
st.set_page_config(page_title="Antenna Designer", page_icon="📡", layout="centered")
st.title("📡 Microstrip Patch Antenna Dimension Calculator")

df = load_materials("cst_materials_extracted.csv")
if df is None:
    st.warning("CSV file not found or failed to load.")
    st.stop()

# -----------------------------------
# Mode Selection
# -----------------------------------
mode = st.radio("Choose Calculation Mode:", ["Standard Patch Calculator Mode", "Design-Oriented Mode"])

# ===================================
# 🔹 Standard Patch Calculator Mode
# ===================================
if mode == "Standard Patch Calculator Mode":
    st.markdown("### 📁 Choose Substrate Material")
    material_names = df['Filename'].tolist()
    material_choice = st.selectbox("Substrate Material", material_names)

    selected_row = df[df['Filename'] == material_choice].iloc[0]
    epsilon = selected_row['Epsilon']
    tand = selected_row['TanD']
    sigma = selected_row['Sigma']

    with st.expander("🔍 Material Properties"):
        st.write(f"**Relative Permittivity (εr):** {epsilon}")
        st.write(f"**Loss Tangent (tanδ):** {tand}")
        st.write(f"**Conductivity (σ):** {sigma} S/m")

    st.markdown("### 📥 Enter Design Parameters")
    freq = st.number_input("Operating Frequency (GHz)", min_value=0.1, max_value=100.0, value=2.4, step=0.1)
    h_mm = st.number_input("Substrate Height (mm)", min_value=0.1, max_value=10.0, value=1.6, step=0.1)

    if st.button("🧮 Calculate"):
        fr = freq * 1e9  # Hz
        h = h_mm / 1000  # meters

        L, W, g_len, g_wid, fx, fy = calculate_patch_dimensions(fr, h, epsilon)

        st.success("📐 Patch Dimensions")
        st.write(f"📏 Width (W): `{W} mm`")
        st.write(f"📐 Length (L): `{L} mm`")
        st.write(f"📦 Ground Plane: `{g_len} mm x {g_wid} mm`")
        st.write(f"📍 Feed Point: `({fx}, {fy}) mm`")

        # Plot geometry
        fig, ax = plt.subplots()
        ax.set_title("Antenna Geometry")
        ax.add_patch(plt.Rectangle((0, 0), g_wid, g_len, fill=False, edgecolor='black', linewidth=2, label='Ground Plane'))
        patch_x = (g_wid - W) / 2
        patch_y = (g_len - L) / 2
        ax.add_patch(plt.Rectangle((patch_x, patch_y), W, L, color='skyblue', label='Patch'))
        ax.plot(patch_x + fx, patch_y + fy, 'ro', label='Feed Point')
        ax.set_xlim(0, g_wid)
        ax.set_ylim(0, g_len)
        ax.set_aspect('equal')
        ax.set_xlabel("Width (mm)")
        ax.set_ylabel("Length (mm)")
        ax.legend()
        st.pyplot(fig)

# ===================================
# 🔹 Design-Oriented Mode
# ===================================
elif mode == "Design-Oriented Mode":
    st.markdown("### 🎯 Design with Component-Specific Material Restrictions")

    def filter_materials(component):
        allowed = component_materials.get(component, [])
        # Filter df where any allowed material string is substring (case insensitive) of Filename
        filtered = df[df['Filename'].apply(lambda x: any(mat.lower() in x.lower() for mat in allowed))]
        return filtered

    substrate_df = filter_materials("Substrate")
    patch_df = filter_materials("Patch")
    ground_df = filter_materials("Ground")

    if substrate_df.empty or patch_df.empty or ground_df.empty:
        st.error("No materials found matching the component restrictions. Please check your CSV and restrictions.")
        st.stop()

    substrate_choice = st.selectbox("Substrate Material", substrate_df['Filename'].tolist())
    patch_choice = st.selectbox("Patch Material", patch_df['Filename'].tolist())
    ground_choice = st.selectbox("Ground Material", ground_df['Filename'].tolist())

    st.markdown("### 📊 Selected Material Properties")

    def display_material_props(name, role):
        row = df[df['Filename'] == name].iloc[0]
        st.write(f"**{role}:** `{row['Filename']}`")
        st.write(f" - εr: {row['Epsilon']}")
        st.write(f" - tanδ: {row['TanD']}")
        st.write(f" - σ: {row['Sigma']} S/m")

    display_material_props(substrate_choice, "Substrate")
    display_material_props(patch_choice, "Patch")
    display_material_props(ground_choice, "Ground")

    st.markdown("### 📥 Enter Design Parameters")
    freq = st.number_input("Frequency (GHz)", min_value=1.0, max_value=5.0, value=2.4, step=0.1)
    h_mm = st.number_input("Substrate Height (mm)", min_value=0.5, max_value=5.0, value=1.6, step=0.1)

    if st.button("🧮 Calculate Design"):
        fr = freq * 1e9
        h = h_mm / 1000
        epsilon_sub = df[df['Filename'] == substrate_choice].iloc[0]['Epsilon']
        L, W, g_len, g_wid, fx, fy = calculate_patch_dimensions(fr, h, epsilon_sub)

        patch_x = (g_wid - W) / 2
        patch_y = (g_len - L) / 2

        feed_abs_x = patch_x + fx
        feed_abs_y = patch_y + fy

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

        # 3D Plot: Simplified patch and ground using surfaces instead of mesh3d for clarity

        # Ground plane corners
        ground_x = [0, g_wid]
        ground_y = [0, g_len]
        ground_z = [[0, 0], [0, 0]]

        # Patch corners (slightly elevated)
        patch_x_arr = [patch_x, patch_x + W]
        patch_y_arr = [patch_y, patch_y + L]
        patch_z = [[0.1, 0.1], [0.1, 0.1]]

        fig = go.Figure()

        # Ground plane surface
        fig.add_trace(go.Surface(
            x=[[ground_x[0], ground_x[1]], [ground_x[0], ground_x[1]]],
            y=[[ground_y[0], ground_y[0]], [ground_y[1], ground_y[1]]],
            z=ground_z,
            colorscale=[[0, 'gray'], [1, 'gray']],
            opacity=0.4,
            showscale=False,
            name='Ground Plane'
        ))

        # Patch surface
        fig.add_trace(go.Surface(
            x=[[patch_x_arr[0], patch_x_arr[1]], [patch_x_arr[0], patch_x_arr[1]]],
            y=[[patch_y_arr[0], patch_y_arr[0]], [patch_y_arr[1], patch_y_arr[1]]],
            z=patch_z,
            colorscale=[[0, 'royalblue'], [1, 'royalblue']],
            opacity=0.9,
            showscale=False,
            name='Patch'
        ))

        # Feed point
        fig.add_trace(go.Scatter3d(
            x=[feed_abs_x],
            y=[feed_abs_y],
            z=[0.11],
            mode='markers',
            marker=dict(size=6, color='red'),
            name='Feed Point'
        ))

        fig.update_layout(
            title="3D Patch Antenna Design",
            scene=dict(
                xaxis_title='Width (mm)',
                yaxis_title='Length (mm)',
                zaxis_title='Height (mm)',
                aspectratio=dict(x=1, y=1.5, z=0.1)
            ),
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)
      
