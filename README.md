# SPECKIT

![SPECKIT Logo](./fig/fig0.png)

*SpecKit: An Integrated Toolkit for Neutron Spectrum Unfolding Using Activation Reactions*

---

## 📖 Introduction
**SpecKit** is an open-source software toolkit designed for **neutron spectrum unfolding using activation reactions**.  
It integrates **reaction matrix preparation, spectrum inversion, uncertainty analysis, and visualization** into a single platform, supporting both **GUI operations and standardized CSV I/O**, making it suitable for research and educational applications.  

Compared with classical unfolding codes (e.g., SAND-II, MAXED, GRAVEL), SpecKit highlights:  
- Built-in **log-smoothness regularization** to stabilize the solution  
- **GUI interface and standardized CSV I/O** to reduce the learning curve  
- **Minimal dataset with one-click reproducibility** to ensure cross-platform reproducibility  
- **Uncertainty quantification embedded in the workflow**, eliminating the need for separate post-processing  

The core algorithm is based on:  
- Least-squares residual minimization  
- Log-smoothness regularization  
- Gradient descent optimization  
- Multiple fittings and Monte Carlo sampling for uncertainty estimation  

> SpecKit is not intended to replace classical codes, but rather to provide a **modern complement**: integrating unfolding and uncertainty quantification into a reproducible and user-friendly workflow for both research and teaching.

---
## 📦 Dependencies

- Python >= 3.8  
- numpy  
- matplotlib  
- pandas  
- scipy  
- tkinter (pre-installed in most Python distributions)  

---

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/lifangchen2021/speckit.git
cd speckit

# Install dependencies
pip install -r requirements.txt
```

---
## 📂 Repository Structure
```
SpecKit/
├── benchmark/                     # Performance verification cases
│    ├── double_peak/              # Double-peak spectrum case
│    │    ├── mcnp_input/          # MCNP input files
│    │    └── results/             # Unfolding results (CSV, figures, tables)
│    └── quasi_single_peak/        # Quasi-single-peak spectrum case
│         ├── mcnp_input/          # MCNP input files
│         └── results/             # Unfolding results (CSV, figures, tables)
├── cross_section/                 # Cross-section datasets (ENDF/B, IRDF formatted files)
├── fig/                           # Figures (example plots, documentation images)
├── src/                           # Source code (core Python scripts)
│    ├── cross_section_input_generator.py
│    ├── neutron_spectrum_solver.py
│    └── spectrum_errorbar_viewer.py
├── .gitignore                     # Git ignore rules
├── LICENSE                        # License file (MIT)
└── README.md                      # Project description and usage guide

```
---

## 🚀 Usage
## 🧩 Module 1: Data Preparation
**Script:** `cross_section_input_generator.py`
**User Interface**  
![Data Preparation UI](./fig/fig1.png)

This module prepares the **reaction cross-section data** and **energy group structure** before spectrum unfolding.

### Features
- Imports activation reaction cross-section libraries  
  (pre-packaged datasets are provided, from IAEA Nuclear Data Services: https://www-nds.iaea.org/exfor/endf.htm)
  ![Data Preparation UI](./fig/fig2.png)
- Reads user-defined **energy group boundary file** (e.g., in MeV, converted to eV)
  ![Data Preparation UI](./fig/fig3.png)  
- Combines physical parameters of activation materials  
  (mass, atomic weight, half-life, irradiation time, cooling time, measured activity ± error)  
- Produces a standardized **CSV file** containing coefficients and activity data for unfolding
  ![Data Preparation UI](./fig/fig4.png)  

### Input
1. Cross-section data file (formatted from ENDF/B, IRDF, etc.)  
   - The first 8 lines contain metadata (library version, isotope, reaction type, etc.)  
   - Numerical cross-section values are read **starting from line 9**  
2. Energy group boundary file (defines group structure and prior spectrum)
   - The first line is header information  
   - Group boundary data are read **starting from line 2**

### Processing
- Interpolates/averages cross-section values over energy groups  
- Applies decay constants and calculates coefficients independent of flux  
- Supports writing multiple activation reactions into the same CSV file,  
  enabling **multi-material spectrum unfolding** in the inversion step  

### Output
- A CSV file with:
  - Group-wise coefficients  
  - Measured activities and associated uncertainties  
- Serves as the input matrix for the **Spectrum Inversion** module
---
## 🧩 Module 2: Spectrum Inversion
**Script:** `neutron_spectrum_solver.py`
 ![Data Preparation UI](./fig/fig5.png) 

This module performs the **core spectrum unfolding algorithm**.  
It takes the prepared reaction matrix (A) and activity vector (b) from the Data Preparation step,  
and reconstructs the unknown neutron spectrum (x).

### Method
- Based on **least-squares minimization**  
- Uses **gradient descent optimization** with **log-smoothness regularization** to stabilize the solution  
- Default convergence threshold is automatically calculated using the **chi-square distribution** (95% confidence level), ensuring statistical interpretability  

### Features
- **Developer Mode**: adjust learning rate, max iterations, and loss threshold  
- **Real-time plotting**: visualize loss convergence and spectrum reconstruction  
- **Multiple runs**: supports Monte Carlo perturbations of activity data (b ± σ) to analyze uncertainty  

### Output
- CSV file of reconstructed neutron spectrum (per run)  
- Convergence curves and spectrum plots (exportable as PNG/PDF)  
 ![Data Preparation UI](./fig/fig6.png) 
---
## 🧩 Module 3: Spectrum Error Bar Viewer
**Script:** `spectrum_errorbar_viewer.py`
![Data Preparation UI](./fig/fig7.png)
This module processes the results from multiple spectrum inversion runs and generates statistical summaries with error bars.

### Features
- Loads multiple inversion results (CSV)  
- Calculates **mean flux** and **standard deviation** for each energy group  
- Computes **total flux**, its standard deviation, and relative standard deviation (RSD)  
- Visualizes results as error-band plots (Mean ± Std Dev) on log–log scale  

### Input
- CSV files from multiple spectrum inversion runs  

### Output
- CSV file containing group-wise mean flux and standard deviation  
- Error-band plot (Mean ± Std Dev), exportable as an image  

---

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Contributing
Contributions are welcome! Feel free to open issues, submit pull requests, or suggest new features. 

---

## 🌟 Acknowledgements
This toolkit was developed in the context of neutron activation analysis research at the **National Atomic Energy Technology Research Institute**. Special thanks to the open-source scientific computing community for foundational tools that made SPECKIT possible.
