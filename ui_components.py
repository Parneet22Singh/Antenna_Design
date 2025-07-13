import streamlit as st

def show_material_props(row, role):
    st.write(f"**{role}:** `{row['Filename']}`")
    st.write(f" - εr: {row['Epsilon']}")
    st.write(f" - tanδ: {row['TanD']}")
    st.write(f" - σ: {row['Sigma']} S/m")

def filter_materials(df, allowed_materials):
    return df[df['Filename'].apply(lambda x: any(mat.lower() in x.lower() for mat in allowed_materials))]
