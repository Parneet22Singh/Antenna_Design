import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

def plot_antenna_geometry(L, W, g_len, g_wid, fx, fy):
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

def plot_antenna_3d(L, W, g_len, g_wid, fx, fy, substrate_height_mm):
    patch_height = 0.035  # metal thickness in mm
    patch_x = (g_wid - W) / 2
    patch_y = (g_len - L) / 2
    feed_abs_x = patch_x + fx
    feed_abs_y = patch_y + fy

    fig = go.Figure()

    # Ground plane at z=0
    fig.add_trace(go.Surface(
        x=[[0, g_wid], [0, g_wid]],
        y=[[0, 0], [g_len, g_len]],
        z=[[0, 0], [0, 0]],
        colorscale=[[0, 'gray'], [1, 'gray']],
        opacity=0.4,
        showscale=False,
        name='Ground Plane'
    ))

    # Patch top surface at substrate_height + patch_height
    fig.add_trace(go.Surface(
        x=[[patch_x, patch_x + W], [patch_x, patch_x + W]],
        y=[[patch_y, patch_y], [patch_y + L, patch_y + L]],
        z=[[substrate_height_mm + patch_height, substrate_height_mm + patch_height],
           [substrate_height_mm + patch_height, substrate_height_mm + patch_height]],
        colorscale=[[0, 'royalblue'], [1, 'royalblue']],
        opacity=0.9,
        showscale=False,
        name='Patch Top Surface'
    ))

    # Patch bottom surface at substrate_height (metal bottom)
    fig.add_trace(go.Surface(
        x=[[patch_x, patch_x + W], [patch_x, patch_x + W]],
        y=[[patch_y, patch_y], [patch_y + L, patch_y + L]],
        z=[[substrate_height_mm, substrate_height_mm],
           [substrate_height_mm, substrate_height_mm]],
        colorscale=[[0, 'royalblue'], [1, 'royalblue']],
        opacity=0.9,
        showscale=False,
        name='Patch Bottom Surface'
    ))

    # Feed point marker at mid thickness of patch
    fig.add_trace(go.Scatter3d(
        x=[feed_abs_x],
        y=[feed_abs_y],
        z=[substrate_height_mm + patch_height / 2],
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
            aspectratio=dict(x=1, y=1.5, z=0.2)
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True) 

