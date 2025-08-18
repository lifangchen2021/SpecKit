# -*- coding: utf-8 -*-
"""
Created on Thu May 15 11:51:10 2025

@author: user
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SpectrumErrorBarApp:
    def __init__(self, root):
        self.root = root
        # If this is the main window, set title and geometry (to avoid errors in tabs)
        if isinstance(root, tk.Tk):
            self.root.title("Neutron Spectrum Error Plotting Tool")
            self.root.geometry("900x700")


        # 建立 UI
        tk.Button(root, text="Select inversion result CSV file", command=self.load_csv).pack(pady=10)

        self.status_label = tk.Label(root, text="No file selected")
        self.status_label.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 增加按鈕區塊
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Save chart as image", command=self.save_plot).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit program", command=root.quit).pack(side=tk.LEFT, padx=5)

        # 儲存上次分析結果
        self.last_result_df = None
        self.last_result_path = None

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select inversion result CSV file",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file_path:
            self.status_label.config(text="Cancel selection")
            return

        try:
            # ✅ Read in: The first column is the simulation ID and is not used in numerical calculations
            df = pd.read_csv(file_path, index_col=0)


            # ✅ Attempt to convert column names to energy values (for verification)
            try:
                energy_bins = df.columns.astype(float)
            except Exception as e:
                raise ValueError("The column names in the CSV file (starting from the 2nd column) must be numeric energy values") from e

            # ✅ Calculate the average spectrum and standard deviation (each column corresponds to an energy bin)
            mean_spectrum = df.mean(axis=0)
            std_spectrum = df.std(axis=0, ddof=1)

            # ✅ Calculate the total flux for each simulation (sum of each row)
            total_flux_per_run = df.sum(axis=1)
            mean_total_flux = total_flux_per_run.mean()
            std_total_flux = total_flux_per_run.std(ddof=1)
            rsd = std_total_flux / mean_total_flux

            # ✅ Combine the results table
            result_df = pd.DataFrame({
                "Energy": energy_bins,
                "Mean Flux": mean_spectrum.values,
                "Std Dev": std_spectrum.values
            })

            # save
            self.last_result_df = result_df
            self.last_result_path = file_path
            output_path = file_path.replace(".csv", "_mean_std.csv")
            result_df.to_csv(output_path, index=False)

            # Display in status bar and console
            self.status_label.config(
                text=f"✅ Saved results to {output_path}\n"
                     f"Average total flux: {mean_total_flux:.2e} ± {std_total_flux:.2e} "
                     f"(RSD={rsd:.2%})"
            )
            print(f"Average total flux: {mean_total_flux:.3e} /cm²")
            print(f"Total flux standard deviation: {std_total_flux:.3e} /cm²")
            print(f"Relative standard deviation RSD: {rsd:.2%}")

            # 畫圖
            self.ax.clear()
            self.ax.step(result_df["Energy"], result_df["Mean Flux"],
                         where='mid', label="Mean Flux", color='green')
            self.ax.fill_between(result_df["Energy"],
                                 result_df["Mean Flux"] - result_df["Std Dev"],
                                 result_df["Mean Flux"] + result_df["Std Dev"],
                                 step='mid', color='green', alpha=0.3, label="Error Bar")

            self.ax.set_xscale("log")
            self.ax.set_yscale("log")
            self.ax.set_xlabel("Neutron Energy (MeV)")
            self.ax.set_ylabel("Flux (/cm²)")
            self.ax.set_ylim(bottom=1)
            self.ax.set_title("Mean Spectrum with Error Bar")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            self.status_label.config(text=f"❌ error：{str(e)}")
            print("File read error：", e)


        

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("PDF File", "*.pdf"), ("All Files", "*.*")],
            title="Save image"
        )
        if file_path:
            try:
                self.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                self.status_label.config(text=f"✅ Image saved：{file_path}")
            except Exception as e:
                self.status_label.config(text=f"❌ Save failed：{str(e)}")

    def save_csv(self):
        if self.last_result_df is None:
            messagebox.showwarning("No data", "Please load the inversion result file first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save average and error CSV"
        )
        if file_path:
            try:
                self.last_result_df.to_csv(file_path, index=False)
                self.status_label.config(text=f"✅ Average and error data saved to：{file_path}")
            except Exception as e:
                self.status_label.config(text=f"❌ Save CSV failed：{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumErrorBarApp(root)
    root.mainloop()
#%%
