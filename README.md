# Antenna_Design
# 📡 Antenna Dimension Calculator

A Python tool to calculate patch antenna dimensions based on user-selected material and target frequency. Automatically computes substrate height using permittivity and frequency.

## Features
- Recommends appropriate material for each component
- Select material from CST database
- Auto-calculates substrate height
- Computes patch length and width
- Displays material properties

## How to Use
1. Run `main.py`
2. Select material number
3. Enter frequency in GHz
4. Enter substrate height in mm

The dataset ustilized is directly extracted by parsing through the .mtd files in Materials folder in the CST STUDIO SUITE folder.
The dataset contains only the fields deemed necessary for this particular project, rest are set to N.A. (be careful while converting the dataset values to float or integer datatypes, the N.A. strings will throw error).
If you want the data of all the fields, you may execute the script provided in parse.py

## Requirements
- pandas
- math
  
Install dependencies:
```bash
pip install pandas
