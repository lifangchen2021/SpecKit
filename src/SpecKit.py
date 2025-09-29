# -*- coding: utf-8 -*-
"""
Created on Thu May 15 13:20:18 2025

@author: user
"""

# BackSpec.py
# Unified GUI for neutron spectrum analysis

import tkinter as tk
from tkinter import ttk

# These will be replaced with modular classes we are about to create
#from cross_section_input_generator import CrossSectionInputFrame
from cross_section_input_generator import create_cross_section_tab
from neutron_spectrum_solver import NeuralSolverApp
from spectrum_errorbar_viewer import SpectrumErrorBarApp
from spectrum_groupflux_comparison1 import SpectrumComparisonApp

def create_analysis_tab(parent):
    frame = tk.Frame(parent)
    app = SpectrumErrorBarApp(frame)
    return frame


class BackSpecApp:
        
    def __init__(self, root):
        root.title("BackSpec - Neutron Spectrum Analysis Platform")
        default_font = ("Arial", 16)  
        root.option_add("*Font", default_font)
        root.geometry("1000x1200")

        # Notebook tab label font
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 16))

        # Create tabbed notebook interface
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # Each page will be a modular frame class
        self.page1 = create_cross_section_tab(notebook)
        self.page2 = tk.Frame(notebook)
        self.page2_solver = NeuralSolverApp(self.page2)
        self.page3 = create_analysis_tab(notebook)
        self.page4 = tk.Frame(notebook)
        self.page4_app = SpectrumComparisonApp(self.page4)
       


        notebook.add(self.page1, text="1.  Data Preparation")
        notebook.add(self.page2, text="2.  Spectrum Inversion")
        notebook.add(self.page3, text="3.  Error Analysis")
        notebook.add(self.page4, text="4. Spectrum Comparison")



if __name__ == "__main__":
    root = tk.Tk()
    app = BackSpecApp(root)
    root.mainloop()
    