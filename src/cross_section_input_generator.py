# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 14:20:23 2025

@author: user
"""
# cross_section_input_generator.py
# Converted to a Frame-based widget for BackSpec GUI integration


import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import csv
import math
import os


def create_cross_section_tab(parent):
    frame = tk.Frame(parent)

    file_path_var = tk.StringVar()
    energy_file_path_var = tk.StringVar()
    entries = {}
    
    
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            file_path_var.set(file_path)
            messagebox.showinfo("Select File", f"Selected File: {file_path}")

    def select_energy_file():
        energy_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if energy_file_path:
            energy_file_path_var.set(energy_file_path)
            messagebox.showinfo("Energy Bin File Selection (Unit: MeV)", f"Selected File: {energy_file_path}")


    def load_energy_bins(energy_file_path):
        if not os.path.exists(energy_file_path):
            messagebox.showerror("Error", "The specified energy bin file does not exist. Please select again.")
            return []
        try:
            bins = []
            with open(energy_file_path, 'r') as file:
                lines = file.readlines()[1:]  # Skip the first line, start from the second line
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 3:  # Ensure each line has at least 3 numbers
                        try:
                            value = float(parts[0]) * 1e6  # Take the first number and convert to eV
                            bins.append(value)
                        except ValueError:
                            continue
            return bins
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the energy bin file: {e}")
            return []

    def process_file(file_path, material_mass, atomic_mass, half_life, irradiation_time, cooling_time, energy_bins):
        with open(file_path, 'r') as file:
            lines = file.readlines()  #Read the entire file at once and store each line as an element in a list
        
        data = []
        start_index = 8  # Assume the data starts from line 9
        for line in lines[start_index:]:
            parts = line.strip().split()  #line.strip(): Remove all leading and trailing whitespace characters from the line.
                                          #.split(): Split the string into a list using whitespace as the delimiter.
            if len(parts) >= 2:
                try:
                    x1 = float(parts[0].replace('D', 'E'))
                    x2 = float(parts[1].replace('D', 'E'))
                    data.append((x1, x2)) #Store the first and second values of each line into data (x1, x2)
                except ValueError:
                    continue
        
        result_list = [0]
        for i in range(len(energy_bins) - 1):
            lower, upper = energy_bins[i], energy_bins[i + 1]
            filtered_values = [x2 for x1, x2 in data if lower <= x1 < upper]

            if filtered_values:
                avg_value = sum(filtered_values) / len(filtered_values)
            else:
                # This bin has no data; determine whether linear interpolation is possible.
                midpoint = (lower + upper) / 2
                left = None
                right = None

                for x1, x2 in data:
                    if x1 < midpoint:
                        left = (x1, x2)
                    elif x1 > midpoint and right is None:
                        right = (x1, x2)
                        break

                if left and right:
                    # Interpolable
                    x0, y0 = left
                    x1, y1 = right
                    avg_value = y0 + (midpoint - x0) * (y1 - y0) / (x1 - x0)
                else:
                    # Not interpolable (at boundary)
                    avg_value = 0

            result_list.append(avg_value)
        
        decay_constant = 0.693 / half_life
        avogadro_number = 6.022e23
        last_input = (material_mass / atomic_mass) * avogadro_number * (1 - math.exp(-decay_constant * irradiation_time)) * math.exp(-decay_constant * cooling_time) * 10**-24
        result_list = [x * last_input for x in result_list]
        
        return result_list

    def process_and_save():
        file_path = file_path_var.get()
        energy_file_path = energy_file_path_var.get()
        if not file_path or not energy_file_path:
            messagebox.showerror("Error", "Please select both the file and the energy bin file!")
            return
        
        try:
            material_name = entries["material_name"].get()
            mass = float(entries["mass"].get())
            atomic_mass = float(entries["atomic_mass"].get())
            half_life = float(entries["half_life"].get())
            irradiation_time = float(entries["irradiation_time"].get())
            cooling_time = float(entries["cooling_time"].get())
            activity = float(entries["activity"].get())
            activity_error = float(entries["activity_error"].get())
            energy_bins = load_energy_bins(energy_file_path)
            if not energy_bins:
                return
            
            results = process_file(file_path, mass, atomic_mass, half_life, irradiation_time, cooling_time, energy_bins)
            
            output_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Select Save Location", confirmoverwrite=False )
            if not output_filename:
                messagebox.showwarning("Save Canceled", "No save location selected. The result was not saved.")
                return
            
   
            header = ["material message"] + [f"{e * 1e-6:.3e}" for e in energy_bins] + ["Measured Activity (Bq)", "Activity Error (Bq)"]
            write_header = not os.path.exists(output_filename)
            
            with open(output_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                if write_header:
                    writer.writerow(header)
                writer.writerow([material_name] + results + [activity, activity_error])
            
            messagebox.showinfo("Save Complete", f"Results have been saved to {output_filename}")
        except ValueError:
            messagebox.showerror("Error", "Please ensure all input values are valid numbers!")
    # --- UI ---
    tk.Button(frame, text="Select Reaction Cross-Section Data File", command=select_file).pack(pady=5)
    tk.Button(frame, text="Select Energy Bin File (Unit: MeV)", command=select_energy_file).pack(pady=5)

    fields = [
("Irradiation material name", "material_name"),
("Material mass (g)", "mass"),
("Material atomic mass", "atomic_mass"),
("Activation product half-life (hr)", "half_life"),
("Irradiation time (hr)", "irradiation_time"),
("Cooling time (hr)", "cooling_time"),
("Measured activity of the material (Bq)", "activity"),
("Uncertainty of the measured activity (Bq)", "activity_error")

    ]

    for label_text, key in fields:
        row = tk.Frame(frame)
        row.pack(pady=3)
        tk.Label(row, text=label_text).pack(side="left")
        entry = tk.Entry(row, width=10)
        entry.insert(0, "0.0")
        entry.pack(side="left", padx=5)
        entries[key] = entry

    tk.Button(frame, text="Start Processing", command=process_and_save, bg="lightblue").pack(pady=15)

    return frame    
#%%


