# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 10:38:39 2025

@author: user
"""

#%%

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import matplotlib
matplotlib.use('TkAgg')  
from tkinter import font  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import chi2
import gc


class NeuralSolverApp:
    def __init__(self, root):
        self.root = root

        if isinstance(root, tk.Tk):  
            self.root.title("Neutron Activation Method for Solving Neutron Spectrum System")
            self.root.geometry("800x1000")
        plt.rcParams.update({
    'font.size': 12,           
    'axes.titlesize': 14,      
    'axes.labelsize': 13,      
    'xtick.labelsize': 11,     
    'ytick.labelsize': 11,     
    'legend.fontsize': 11     
})
        
        
        # Initialize variables
        self.A = None
        self.b = None
        self.b_error = None  # Add: activity error vector
        self.x_dummy = None
        self.stop_training_flag = False  # Add: variable to control manual stop
        self.developer_mode = tk.BooleanVar(value=False)  #Developer Mode
        self.enable_live_plot = tk.BooleanVar(value=False)   # ➤ Enable plotting by default
        self.x_perturbation_scale = tk.DoubleVar(value=0.0)
        self.loss_threshold = tk.DoubleVar(value=1.0)
        self.initial_learning_rate = tk.DoubleVar(value=1.0)
        self.max_epochs = tk.IntVar(value=500000)
        
        # Build the UI interface
        self.create_widgets()
        
    def create_widgets(self):
        # Control button section
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, pady=10, anchor="center") 
        
        tk.Checkbutton(
            self.top_frame,
            text="Real-time plotting (update chart during training)",
            variable=self.enable_live_plot
        ).pack(pady=5)

        tk.Checkbutton(
            self.top_frame,
            text="Developer Mode",
            variable=self.developer_mode,
            command=self.toggle_developer_widgets
        ).pack(pady=5)

        tk.Label(self.top_frame, text="Select input data").pack(pady=5)
        tk.Button(self.top_frame, text="Select activation product parameter file", command=self.load_user_input).pack(pady=5)
        tk.Button(self.top_frame, text="Select initial spectrum file", command=self.load_initial_guess).pack(pady=5)

        tk.Label(self.top_frame, text="Number of iterations for inversion").pack()
        self.num_runs = tk.IntVar(value=1)
        tk.Entry(self.top_frame, textvariable=self.num_runs).pack()

        self.start_button = tk.Button(self.top_frame, text="Start training", command=self.run_multiple_trainings)
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(self.top_frame, text="Waiting for file selection...")
        self.status_label.pack(pady=5)

        self.save_button = tk.Button(self.top_frame, text="Save chart", command=self.save_canvas_plot)
        self.save_button.pack(pady=5)

        # -------- Developer parameter section above the chart --------
        self.developer_frame = tk.Frame(self.root)
        self.developer_frame.pack(side=tk.TOP, pady=(5, 0))
        self.dev_widgets = []

        def add_dev_row(label, variable):
            frame = tk.Frame(self.developer_frame)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            entry = tk.Entry(frame, textvariable=variable, width=10)
            entry.pack(side=tk.LEFT)
            self.dev_widgets.append(frame)
            return frame

        add_dev_row("Loss Threshold", self.loss_threshold).pack(side=tk.LEFT, padx=10)
        add_dev_row("Initial Learning Rate", self.initial_learning_rate).pack(side=tk.LEFT, padx=10)
        add_dev_row("Max Epochs", self.max_epochs).pack(side=tk.LEFT, padx=10)

        # Hidden by default
        for widget in self.dev_widgets:
            widget.pack_forget()

        # -------- Chart area --------
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                
    def load_user_input(self):
        # ① If the equation file changes, discard the old scaling_factor
        if hasattr(self, 'scaling_factor'):
            delattr(self, 'scaling_factor')

        filename = filedialog.askopenfilename(title="Select the file containing equation data", filetypes=[("Text files", "*.txt;*.csv")])
        if filename:
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(filename, header=None, skiprows=0)  # **Ensure the first line is read**
                else:
                    df = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=0)  # **Ensure the first line is read**

                if df.shape[1] < 2:  # Ensure there are at least two columns to prevent index errors
                    raise ValueError("CSV file must contain at least two columns of data")

                # **Ensure the x-axis labels are taken from the first row, from the second column to the second-to-last column.**
                self.A_header = df.iloc[0, 1:-2].to_numpy(dtype=np.float32)  # **Read the x-axis data from the first row**

                # **Ignore the first row and read the A matrix and b vector**
                data = df.iloc[1:, 1:].to_numpy(dtype=np.float32)  # **Read A and b starting from the second row**
                self.A = data[:, :-2]  # Matrix A
                self.b = data[:, -2].reshape(-1, 1)  # Target vector b
                self.b_error = data[:, -1].reshape(-1, 1)  # The last column is the activity error.
                
                # Calculate degrees of freedom (number of activation material entries)
                dof = self.b.shape[0]  

                # Set confidence interval (95%)
                confidence_level = 0.95

                # Use the chi-square distribution to find the threshold value.
                computed_loss_threshold = chi2.ppf(confidence_level, dof)
 
                self.loss_threshold.set(computed_loss_threshold)
#                print(f"Computed Loss Threshold: {computed_loss_threshold}") 
        
                self.status_label.config(text="Equation data loaded successfully")
                self.check_ready()
            except Exception as e:
                messagebox.showerror("Error", f"Error reading data: {str(e)}")


    def load_initial_guess(self):
        # ② If the initial spectrum file is changed, also clear the old scaling_factor
        if hasattr(self, 'scaling_factor'):
            delattr(self, 'scaling_factor')

        filename = filedialog.askopenfilename(
            title="Select the file containing the initial neutron spectrum flux values",
            filetypes=[("Text files", "*.txt;*.csv")]
        )

        if filename:
            try:
                # Read the file, ignore the first row
                df = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=1)

                if df.shape[1] < 2:  # Ensure at least two columns (energy & flux)
                    raise ValueError("File format error. Each line must contain at least two numbers (energy & flux).")

                # Take the 2nd column as initial flux values
                x_data = df.iloc[:, 1].to_numpy(dtype=np.float32)

                # Ensure consistency with matrix A if already loaded
                if self.A is not None and len(x_data) != self.A.shape[1]:
                    raise ValueError(f"Number of initial values ({len(x_data)}) does not match "
                                     f"the number of unknowns in A ({self.A.shape[1]}).")

                self.x_dummy = x_data.reshape(1, -1)
                self.original_x_dummy = self.x_dummy.copy()  # Backup initial data
                self.status_label.config(text="Initial spectrum loaded successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read initial spectrum file: {str(e)}")

        else:
            # If no file is selected, determine number of unknowns dynamically from A or A_header
            num_unknowns = self.A.shape[1] if self.A is not None else len(self.A_header)
            self.x_dummy = np.random.uniform(1e-6, 1.0, size=(1, num_unknowns)).astype(np.float32)
            self.status_label.config(text="No initial file selected — using random initial spectrum")

        self.check_ready()


    def check_ready(self):
        if self.A is not None and self.b is not None and self.x_dummy is not None:
            self.start_button.config(state=tk.NORMAL)
    
    def toggle_developer_widgets(self):
        if self.developer_mode.get():
            for widget in self.dev_widgets:
                widget.pack(pady=2)
        else:
            for widget in self.dev_widgets:
                widget.pack_forget()

    
    def start_training(self):
        self.stop_training_flag = False  
        loss_threshold_value = self.loss_threshold.get()
        
        print(f"Using Loss Threshold: {loss_threshold_value}")  

        self.start_button.config(state=tk.DISABLED)
        self.root.after(0, lambda: self.status_label.config(text="訓練中...請稍候"))
        
        # 使用多執行緒來運行 train_model
        Thread(target=self.train_model, args=(loss_threshold_value,)).start()

    def stop_training(self):
        self.stop_training_flag = True  

    def plot_results(self, loss_history, x_values):
        self.ax1.clear()
        self.ax1.plot(loss_history[5:], label="Training Loss", color='blue', linewidth=2)
        self.ax1.set_xlabel("Epochs")
        self.ax1.set_ylabel("Loss Value")
        self.ax1.set_title("Loss Function vs Training Epochs")
        self.ax1.legend()
        self.ax1.grid(True)

        self.ax2.clear()
        x_labels = np.array(self.A_header, dtype=float)  
        flux = np.array(x_values, dtype=float)           # Group flux

        # --- Group Flux  ---
        self.ax2.step(x_labels, flux, where='mid', color='orange', label="Group Flux (Φᵢ)")
        self.ax2.fill_between(x_labels, flux, step='mid', color='orange', alpha=0.5)

        # --- Per lethargy (green) ---
        E_edges = np.insert(x_labels, 0, x_labels[0] * 0.9)  
        dlnE = np.diff(np.log(E_edges))
        phi_u = flux / dlnE
        mask = (x_labels > 0) & (phi_u > 0)

        self.ax2.plot(x_labels[mask], phi_u[mask], linestyle="-", color="green",
                      label="dΦ/dlnE (per lethargy)")

      
        self.ax2.set_xlabel("Neutron Energy (MeV)")
        self.ax2.set_ylabel("Flux")
        self.ax2.set_ylim(bottom=1)  
        self.ax2.set_yscale("log")
        self.ax2.set_xscale("log")
        self.ax2.set_title("Neutron Spectrum Prediction")
        self.ax2.grid(True)
        self.ax2.legend()

        
        self.canvas.draw()
        self.root.update_idletasks()
        
        # --- print data ---
        print("Energy(MeV)            dΦ/dlnE")
        for e, u in zip(x_labels[mask], phi_u[mask]):
            print(f"{e:12.5e}    {u:12.5e}")


        
    def run_one_training(self, loss_threshold, b_vector):
        num_unknowns = self.x_dummy.shape[1]
        max_epochs = self.max_epochs.get()
        learning_rate = self.initial_learning_rate.get()
        
        zero_mask = (self.x_dummy == 0)  

        x_variable = np.maximum(self.x_dummy, 1e-6)    
        x_variable[zero_mask] = 0  

        loss_history = []
        min_loss = float('inf')
        no_improvement_epochs = 0

        for epoch in range(max_epochs):
            Ax_pred = np.dot(x_variable, self.A.T)
            error = Ax_pred - b_vector.T 
            smoothness_penalty = np.mean(np.square(np.diff(np.log(x_variable + 1e-12))))
           
            
            λ = 0.01  # Smoothness weight, adjustable
            loss = np.mean(np.square(error)) + λ * smoothness_penalty

            gradient = 2 * np.dot(error, self.A) / self.A.shape[0]
            x_variable -= learning_rate * gradient
            x_variable = np.maximum(x_variable, 1e-6)
            
            x_variable[zero_mask] = 0  

            loss_history.append(loss)

            if loss < min_loss:
                min_loss = loss
                no_improvement_epochs = 0
            else:
                no_improvement_epochs += 1

            if no_improvement_epochs >= 1000:
                no_improvement_epochs = 0
                min_loss = float('inf')
                x_variable = np.maximum(self.x_dummy, 1e-6)
                if hasattr(self, 'scaling_factor'):
                    x_variable = np.maximum(x_variable / self.scaling_factor, 1e-6)

            if epoch == 0 :
                scaling_values = Ax_pred / b_vector.T
                scaling_factor = np.mean(scaling_values)
                print("sacling factor=",scaling_factor)   
                x_variable = np.maximum(x_variable / scaling_factor, 1e-6)
                print( x_variable)
               
            
            if len(loss_history) >= 500:
                recent_losses = loss_history[-500:]
                max_loss = max(recent_losses)
                min_loss = min(recent_losses)
                if abs(max_loss - min_loss) / max_loss < 1e-5:
                    print(f"🟡 Loss function changed very little in the last 500 epochs, stopping training early")
                    break
            
            if self.enable_live_plot.get() and ((epoch + 1) % 100 == 0):
                
                self.plot_results(loss_history, x_variable.flatten())

            
            if epoch == max_epochs - 1 and self.enable_live_plot.get():
                self.plot_results(loss_history, x_variable.flatten())


            if loss < loss_threshold:
                break
        print("Final Loss Function Value (single run):", loss_history[-1])
        return x_variable, loss_history
        
    def run_multiple_trainings(self):
        
        # Clear canvas and memory
        plt.close('all')
        gc.collect()
        for child in self.plot_frame.winfo_children():
            child.destroy()

        # Rebuild canvas
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save all inversion results to CSV"
        )
        
        if self.b_error is None:
            raise ValueError("b_error not loaded, cannot perform error perturbation")

        if not save_path:
            messagebox.showwarning("Cancel Save", "No save path selected, training stopped.")
            return
        
        
        loss_threshold = self.loss_threshold.get()
        num_runs = self.num_runs.get()
        all_results = []
        
        # ✅ Back up the original x_dummy to avoid distortion from consecutive perturbations
        original_x_dummy = self.x_dummy.copy()

    # ✅ Save all initial spectrum lists
        initial_spectra_list = []

        for run in range(num_runs):
            print(f"✅ Iteration {run + 1}")
            print(f"Initial spectrum (Iteration {run + 1}):\n{self.x_dummy.flatten()}\n")
           
            self.x_dummy = original_x_dummy.copy()

            
            initial_spectra_list.append(self.x_dummy.flatten().copy())
            
            
            print("📋 Original activity b (total {} entries):".format(len(self.b)))
            for i, val in enumerate(self.b):
                print(f"  [{i+1}] {val.item():.4e}")

            perturbed_b = self.b + np.random.normal(loc=0.0, scale=self.b_error)


            x_variable, loss_history = self.run_one_training(loss_threshold, perturbed_b)

            self.plot_results(loss_history, x_variable.flatten())
            all_results.append(x_variable.flatten())
            print("Total Flux: {:.3e}".format(x_variable.sum()))
           

        
        self.export_all_spectra_to_csv(all_results, save_path)

    def export_all_spectra_to_csv(self, all_results, save_path):
        try:
            df = pd.DataFrame(all_results, columns=self.A_header)
            df.index = [f"Run_{i+1}" for i in range(len(all_results))]
            df.to_csv(save_path)
            print(f"All inversion results have been saved to：{save_path}")
        except Exception as e:
            print(f"Save failed: {e}")        
    
    def save_canvas_plot(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("PDF File", "*.pdf"), ("All Files", "*.*")],
            title="Select image save location"
        )
        if file_path:
            try:
                self.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                self.status_label.config(text=f"✅ Image successfully saved to:{file_path}")
            except Exception as e:
                self.status_label.config(text=f"❌ Failed to save image:{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeuralSolverApp(root)
    root.mainloop()

#%%


