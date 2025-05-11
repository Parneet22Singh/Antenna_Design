import pandas as pd
import math

# Function to load material data from CSV
def get_material_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df = df[['Filename', 'Epsilon', 'Mu', 'TanD', 'Sigma']]  # Only required fields
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

# Function to select material from the list
def select_material(df):
    print("\nAvailable Materials:\n")
    for i, name in enumerate(df['Filename']):
        print(f"{i + 1}. {name}")

    try:
        index = int(input("\nSelect material by number: ")) - 1
        if index not in range(len(df)):
            raise ValueError
        return df.iloc[index]
    except:
        print("Invalid selection.")
        return None

# Function to get user inputs for frequency and substrate height
def get_user_inputs():
    try:
        fr = float(input("\nEnter target resonance frequency (in GHz): ")) * 1e9  # Convert GHz to Hz
        h = float(input("Enter substrate height (in mm): ")) / 1000  # Convert mm to meters
        return fr, h
    except:
        print("Invalid input.")
        return None, None

# Function to calculate the antenna patch dimensions (L, W) and other parameters
def calculate_patch_dimensions(fr, h, epsilon):
    c = 3e8  # Speed of light in m/s

    # Patch width (W) using standard formula
    W = c / (2 * fr * math.sqrt(epsilon))

    # Effective permittivity calculation for the patch
    eff_er = (epsilon + 1) / 2 + (epsilon - 1) / 2 * (1 + 12 * h / W) ** -0.5

    # Effective length (Leff) calculation for the patch
    leff = c / (2 * fr * math.sqrt(eff_er))

    # Length extension (delta L) calculation
    delta_L = 0.412 * h * ((eff_er + 0.3) * (W / h + 0.264)) / ((eff_er - 0.258) * (W / h + 0.8))

    # Actual length (L) after applying the length extension
    L = leff - 2 * delta_L

    # Ground plane dimensions (larger than the patch)
    ground_plane_length = 6 * h + L
    ground_plane_width = 6 * h + W

    # Feed location calculation (usually at the center of the patch)
    feed_location_x = W / 2  # Center of the patch along width
    feed_location_y = L / 2  # Center of the patch along length

    return round(L * 1000, 3), round(W * 1000, 3), round(ground_plane_length * 1000, 3), round(ground_plane_width * 1000, 3), feed_location_x, feed_location_y

# Main function to run the program
def main():
    print("📡 CST Material-based Antenna Dimension Calculator 📡")
    print("\n📚 Recommended Materials for Fabrication:")
    print("🔹 Substrate Materials:")
    print("   - FR4 (εr ≈ 4.4, low cost, moderate performance)")
    print("   - Rogers RO4003 (εr ≈ 3.55, low loss, good stability)")
    print("   - RT/duroid 5870 (εr ≈ 2.33, very low loss, for high-frequency designs)")

    print("\n🔹 Patch Materials (Conductive):")
    print("   - Copper (most common, good conductivity)")
    print("   - Silver (excellent conductivity but expensive)")
    print("   - Gold (great for corrosion resistance, expensive)")

    print("\n🔹 Feed Line Materials:")
    print("   - Copper traces on the same PCB")
    print("   - Coaxial connectors (SMA, etc., for external feed)")

    df = get_material_data("data/cst_materials_extracted.csv")
    if df is None:
        return

    material = select_material(df)
    if material is None:
        return

    fr, h = get_user_inputs()
    if fr is None or h is None:
        return

    epsilon = material['Epsilon']
    L, W, ground_length, ground_width, feed_x, feed_y = calculate_patch_dimensions(fr, h, epsilon)

    print("\n📐 Antenna Dimensions:")

    print(f"Material: {material['Filename']}")
    print(f"Relative Permittivity (εr): {epsilon}")
    print(f"Calculated Patch Length (L): {L} mm")
    print(f"Calculated Patch Width (W): {W} mm")
    print(f"Ground Plane Length: {ground_length} mm")
    print(f"Ground Plane Width: {ground_width} mm")
    print(f"Feed Location: ({feed_x} (x), {feed_y} (y))")

    if pd.notna(material['TanD']):
        print(f"Loss Tangent (tanδ): {material['TanD']}")
    if pd.notna(material['Sigma']):
        print(f"Conductivity (σ): {material['Sigma']} S/m")

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
