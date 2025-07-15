import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_tissue_data(csv_path="tissues_properties.csv"):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip().lower().replace("(", "").replace(")", "").replace(" ", "_") for col in df.columns]
    return df

def compare_values(user_val, ref_val, tolerance):
    rel_diff = abs(user_val - ref_val) / (abs(ref_val) + 1e-8)
    return rel_diff <= tolerance, rel_diff

def generate_report(user_vals, row, tolerance):
    compatibility = []
    rel_diffs = []
    for field in user_vals:
        compatible, diff = compare_values(user_vals[field], row[field], tolerance)
        compatibility.append(compatible)
        rel_diffs.append(diff)
    avg_diff = np.mean(rel_diffs)
    return all(compatibility), rel_diffs, avg_diff

def plot_comparison(user_vals, ref_vals, tissue_name, compat_list):
    fields = list(user_vals.keys())
    user_y = [user_vals[f] for f in fields]
    ref_y = [ref_vals[f] for f in fields]
    colors = ['green' if c else 'red' for c in compat_list]

    x = np.arange(len(fields))

    fig, ax = plt.subplots()

    ax.plot(x, user_y, marker='o', label='Your Values', color='blue', linewidth=2)

    ax.plot(x, ref_y, marker='s', label='Reference Values', color='gray', linewidth=2)
    
    for i in range(len(x)):
        ax.plot(x[i], ref_y[i], marker='s', color=colors[i], markersize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(fields)
    ax.set_ylabel("Value")
    ax.set_title(f"Comparison with {tissue_name}")
    ax.legend()
    ax.grid(True)

    return fig

def find_closest_frequency_row(df, tissue_name, user_freq):
    tissue_rows = df[df['tissue'].str.lower() == tissue_name.lower()]
    if tissue_rows.empty:
        return None

    tissue_rows = tissue_rows.copy()
    tissue_rows['freq_diff'] = abs(tissue_rows['frequency'] - user_freq)
    closest_row = tissue_rows.loc[tissue_rows['freq_diff'].idxmin()]
    return closest_row

def check_compatibility(df, tissue_choice, permittivity, elec_cond, freq_ghz, tolerance):
    user_vals = {'permittivity': permittivity, 'elec_cond': elec_cond}
    row = find_closest_frequency_row(df, tissue_choice, freq_ghz)
    if row is None:
        return None, None, None, None

    compatible, diffs, avg_diff = generate_report(user_vals, row, tolerance)
    compat_list = [d <= tolerance for d in diffs]
    fig = plot_comparison(user_vals, row, tissue_choice, compat_list)

    return compatible, diffs, avg_diff, fig
