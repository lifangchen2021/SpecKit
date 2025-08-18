# SPECKIT

![SPECKIT Logo](./fig/fig0.png)

*SpecKit: An Integrated Toolkit for Neutron Spectrum Unfolding Using Activation Reactions*

---

## 📖 Introduction
SPECKIT (Spectrum Unfolding Kit) is a Python-based open-source software designed for reconstructing neutron energy spectra from activation data. It provides researchers with an accessible, modular, and transparent framework for spectrum unfolding, making it easier to integrate into both academic research and applied nuclear technology workflows.

The toolkit was developed as part of research on **neutron activation methods** for estimating flux distributions in quasi-monoenergetic neutron fields. The work is described in detail in the accompanying publication:

> Chen, L.-F. *利用中子活化反應推估擬單能靶中子場之通量分佈*. (Manuscript in preparation)

---

## ✨ Features
- 📊 Implements unfolding algorithms including:
  - SAND-II
  - MAXED (Maximum Entropy)
  - GRAVEL (Generalized Least-Squares)
- ⚡ Simple command-line interface (CLI) and Python API
- 🧰 Modular design for extensibility
- 📈 Built-in plotting for neutron spectrum visualization
- 🐱 Friendly mascot to guide your journey 😉

---

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/your-username/speckit.git
cd speckit

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage
### Command Line Example
```bash
python src/speckit.py --input activation_data.csv --method maxed --output spectrum.png
```

### Python API Example
```python
from speckit import Unfolder

unfolder = Unfolder(method="maxed")
spectrum = unfolder.unfold("activation_data.csv")
spectrum.plot()
```

---

## 📂 Repository Structure
```
SPECKIT/
├── src/               # Source code
├── examples/          # Example datasets and scripts
├── images/            # Figures, logos, mascot
├── tests/             # Unit tests
└── README.md          # Project documentation
```

---

## 📚 References
- M. Reginatto, P. Goldhagen, S. Neumann, "Spectrum unfolding, sensitivity analysis and propagation of uncertainties with the maximum entropy deconvolution code MAXED," *Nucl. Instrum. Methods Phys. Res. A*, vol. 476, pp. 242–246, 2002. [https://doi.org/10.1016/S0168-9002(01)01439-5](https://doi.org/10.1016/S0168-9002(01)01439-5)
- SAND-II, "A Computer Program for Neutron Flux Spectra Determination by Multiple Foil Activation," Argonne National Laboratory, ANL-6984, 1964.
- D. L. Smith, "GRAVEL: A Generalized Least-Squares Program for Neutron Spectrum Unfolding," Argonne National Laboratory Report, 1990.

---

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Contributing
Contributions are welcome! Feel free to open issues, submit pull requests, or suggest new features. 

---

## 🌟 Acknowledgements
This toolkit was developed in the context of neutron activation analysis research at the **National Atomic Energy Technology Research Institute**. Special thanks to the open-source scientific computing community for foundational tools that made SPECKIT possible.
