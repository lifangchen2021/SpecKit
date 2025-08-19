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

## 📂 Repository Structure
```
SPECKIT/
├── src/               # Source code
├── examples/          # Example datasets and scripts
├── fig/            # Figures, logos, mascot
         
└── README.md          # Project documentation
```

---



---

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Contributing
Contributions are welcome! Feel free to open issues, submit pull requests, or suggest new features. 

---

## 🌟 Acknowledgements
This toolkit was developed in the context of neutron activation analysis research at the **National Atomic Energy Technology Research Institute**. Special thanks to the open-source scientific computing community for foundational tools that made SPECKIT possible.
