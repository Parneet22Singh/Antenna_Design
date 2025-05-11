import os
import csv

# Folder containing the .mtd files
folder_path = r'Path/to/the/folder/here'

# Fields to extract
target_fields = [
    'Epsilon', 'Mu', 'Sigma', 'TanD', 'TanDFreq', 'EpsInfinity',
    'DispModelEps', 'DispCoeff1Eps', 'DispCoeff2Eps', 'UseGeneralDispersionEps',
    'ThermalConductivity', 'ThermalConductivityX', 'ThermalConductivityY', 'ThermalConductivityZ',
    'HeatCapacity', 'ThermalExpansionRate', 'Emissivity', 'YoungsModulus',
    'PoissonsRatio', 'Rho'
]

# List to store extracted data
materials_data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".mtd"):
        file_path = os.path.join(folder_path, filename)
        material_info = {'Filename': filename}
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(".") and '"' in line:
                        try:
                            key, val = line.split(" ", 1)
                            key = key[1:]  # Remove leading dot
                            val = val.strip().strip('"')
                            if key in target_fields:
                                material_info[key] = val
                        except ValueError:
                            continue
            materials_data.append(material_info)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Save to CSV
csv_file_path = "data/cst_materials_extracted.csv"
fieldnames = ['Filename'] + target_fields

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for material in materials_data:
        writer.writerow({key: material.get(key, 'N/A') for key in fieldnames})

print(f"CSV file saved to: {csv_file_path}")
