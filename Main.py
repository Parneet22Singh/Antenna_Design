import pandas as pd

# Material database
materials_db = {
    "FR4": {"Epsilon": 4.4, "Sigma": 1e-4, "TanD": 0.02},  # Typical material properties for FR4
    "Roger 4003": {"Epsilon": 3.55, "Sigma": 5e7, "TanD": 0.0025},  # Roger 4003
    "RT/duroid 5870": {"Epsilon": 2.33, "Sigma": 5e7, "TanD": 0.0012},  # RT/duroid 5870
}


# Function to calculate the antenna patch dimensions (Length and Width)
def calculate_patch_dimensions(frequency, substrate_height, epsilon_r):
    c = 3e8  # Speed of light in m/s

    # Calculate width (W) and length (L) using basic microstrip formulas
    W = c / (2 * frequency * (epsilon_r) ** 0.5)  # Width of the patch
    eff_er = (epsilon_r + 1) / 2 + (epsilon_r - 1) / 2 * (
                1 + 12 * substrate_height / W) ** -0.5  # Effective permittivity
    Leff = c / (2 * frequency * eff_er ** 0.5)  # Effective length
    delta_L = 0.412 * substrate_height * ((eff_er + 0.3) * (W / substrate_height + 0.264)) / \
              ((eff_er - 0.258) * (W / substrate_height + 0.8))  # Length extension

    L = Leff - 2 * delta_L  # Actual length of the patch

    # Return the dimensions in mm
    return round(W * 1000, 3), round(L * 1000, 3)


# Function to recommend a material based on its permittivity and target frequency
def recommend_material(frequency, substrate_height):
    # Calculate the required material's permittivity based on frequency (for example, using a range of typical permittivities)
    required_epsilon_r = 2.2 + 0.2 * (frequency / 1e9)  # Simplified formula for target permittivity (just an example)

    closest_material = None
    min_diff = float('inf')

    for material, props in materials_db.items():
        epsilon_r = props["Epsilon"]
        # Find the material with the closest permittivity to the target
        diff = abs(epsilon_r - required_epsilon_r)
        if diff < min_diff:
            min_diff = diff
            closest_material = material

    # Return the recommended material and its properties
    return closest_material, materials_db[closest_material]


# Function to get user inputs
def get_user_inputs():
    try:
        frequency = float(input("Enter target frequency (in GHz): ")) * 1e9  # Convert to Hz
        height = float(input("Enter substrate height (in mm): ")) / 1000  # Convert to meters
        return frequency, height
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return None, None


# Main function
def main():
    print("📡 Antenna Design Assistant 📡")

    frequency, height = get_user_inputs()
    if frequency is None or height is None:
        return

    # Calculate patch dimensions
    W, L = calculate_patch_dimensions(frequency, height, 4.4)  # Assuming a default material (FR4) for calculation

    print(f"\n📐 Calculated Antenna Patch Dimensions (using FR4 as material):")
    print(f"Patch Length (L): {L} mm")
    print(f"Patch Width (W): {W} mm")

    # Recommend a material based on frequency and substrate height
    material, properties = recommend_material(frequency, height)

    print(f"\nRecommended Material: {material}")
    print(f"Relative Permittivity (εr): {properties['Epsilon']}")
    print(f"Loss Tangent (tanδ): {properties['TanD']}")
    print(f"Conductivity (σ): {properties['Sigma']} S/m")


if __name__ == "__main__":
    main()
