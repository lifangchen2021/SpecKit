# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 16:25:18 2025

@author: user
"""

# spectrum_groupflux_comparison.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class SpectrumComparisonApp:
    def __init__(self, parent):
        """Initialize the Spectrum Comparison tab"""
        self.parent = parent

        label = tk.Label(parent, text="Please select an Excel file to generate a comparison plot of Group Flux and Spectrum.", font=("Arial", 12))
        label.pack(pady=20)

        btn = tk.Button(parent, text="Open Excel file and select columns", command=self.load_excel_and_select_columns)
        btn.pack()

    def draw_selected_lines(self, df, x, selected_cols):
        """Draw Group Flux (step) vs Spectrum (solid) comparison plot"""
        plt.figure(figsize=(14, 7))
        x = x.to_numpy()

        # Compute geometric mean energy-group boundaries
        x_edges = np.zeros(len(x) + 1)
        x_edges[1:-1] = np.sqrt(x[:-1] * x[1:])
        x_edges[0] = x[0] * (x[0] / x[1])
        x_edges[-1] = x[-1] * (x[-1] / x[-2])

        # Color cycle
        colors = plt.cm.tab10.colors

        for i, col in enumerate(selected_cols):
            y = df[col].replace(0, 1e-20).to_numpy()

            # Clean invalid values
            y[np.isnan(y)] = 1e-20
            y[np.isinf(y)] = 1e-20
            y[y < 1e-20] = 1e-20

            # Step plot (Group Flux)
            y_full = np.append(y, y[-1])
            plt.step(x_edges, y_full, where='mid',
                     linestyle='--', color=colors[i % len(colors)],
                     label=f"{col} (Group Flux)")

            # Spectrum (/lethargy)
            lethargy = np.log(x_edges[1:] / x_edges[:-1])
            spectrum = y / lethargy
            plt.plot(x, spectrum,
                     linestyle='-', color=colors[i % len(colors)],
                     label=f"{col} (Spectrum)")

        plt.xscale('log')
        plt.yscale('log')
        plt.xlim(1E-9, 30)
        plt.ylim(bottom=1)

        plt.xlabel("Energy (MeV) (log scale)")
        plt.ylabel("Flux (/cm²·s) (log scale)")
        plt.title("Spectrum vs Group Flux Comparison")
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.legend(loc="upper right", fontsize=9)
        plt.tight_layout()
        plt.show()

    def load_excel_and_select_columns(self):
        """Load Excel file and select columns to plot"""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            messagebox.showerror("Read Error", f"Unable to read Excel file:\n{e}")
            return

        col_names = list(df.columns)
        if len(col_names) < 2:
            messagebox.showwarning("Insufficient Columns", "Excel file must contain an energy column and at least one data column.")
            return

        x = df[col_names[0]]
        selectable_cols = col_names[1:]

        # Column selection window
        selection_win = tk.Toplevel(self.parent)
        selection_win.title("Select columns to plot")
        tk.Label(selection_win, text="Please select one or more columns to plot").pack(pady=5)

        listbox = tk.Listbox(selection_win, selectmode=tk.MULTIPLE, width=40, height=15)
        for col in selectable_cols:
            listbox.insert(tk.END, col)
        listbox.pack()

        def on_confirm():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one column.")
                return
            selected_cols = [selectable_cols[i] for i in selected_indices]
            self.draw_selected_lines(df, x, selected_cols)

        tk.Button(selection_win, text="Plot", command=on_confirm).pack(pady=10)
