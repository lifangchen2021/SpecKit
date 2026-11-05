# -*- coding: utf-8 -*-
"""
SpecKit - Neutron spectrum unfolding using activation reactions.
Extended with unfolding methods from the bssunfold package.
"""

import inspect
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import chi2
import gc

# --- bssunfold solvers (Python >= 3.11) ---
from bssunfold.core.unfold_tsvd import solve_tsvd
from bssunfold.core.unfold_landweber import solve_landweber
from bssunfold.core.unfold_mlem import solve_mlem
from bssunfold.core.unfold_gravel import solve_gravel
from bssunfold.core.unfold_maxed import solve_maxed
from bssunfold.core.unfold_tikhonov_legendre import solve_tikhonov_legendre
from bssunfold.core.unfold_tikhonov_sobolev_dp import solve_tikhonov_sobolev_dp
from bssunfold.core.unfold_kaczmarz import solve_kaczmarz
from bssunfold.core.unfold_sart import solve_sart
from bssunfold.core.unfold_cgls import solve_cgls
from bssunfold.core.unfold_statreg import solve_statreg
from bssunfold.core.unfold_bayes import solve_bayes
from bssunfold.core.unfold_crystal_ball import solve_crystal_ball
from bssunfold.core.unfold_pgd import solve_pgd

METHODS = {
    "SpecKit (gradient + log-smoothness)": None,  # built-in
    "TSVD": solve_tsvd,
    "Landweber": solve_landweber,
    "MLEM": solve_mlem,
    "GRAVEL": solve_gravel,
    "MAXED (MaxEnt)": solve_maxed,
    "Tikhonov (Legendre)": solve_tikhonov_legendre,
    "Tikhonov (Sobolev)": solve_tikhonov_sobolev_dp,
    "Kaczmarz": solve_kaczmarz,
    "SART": solve_sart,
    "CGLS": solve_cgls,
    "StatReg": solve_statreg,
    "Bayes": solve_bayes,
    "Crystal Ball": solve_crystal_ball,
    "PGD": solve_pgd,
}


def call_solver(solve_func, A, b, x0, max_iterations, tolerance):
    """Call a bssunfold solve_* with best-effort parameter passing."""
    sig = inspect.signature(solve_func)
    kwargs = {}
    if "max_iterations" in sig.parameters:
        kwargs["max_iterations"] = max_iterations
    if "tolerance" in sig.parameters:
        kwargs["tolerance"] = tolerance
    result = solve_func(A, b, x0, **kwargs)
    if isinstance(result, tuple):
        return result[0]
    return result


class NeuralSolverApp:
    def __init__(self, root):
        self.root = root
        if isinstance(root, tk.Tk):
            self.root.title("SpecKit - Neutron Spectrum Unfolding")
            self.root.geometry("900x1050")
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 13,
            'xtick.labelsize': 11,
            'ytick.labelsize': 11,
            'legend.fontsize': 11,
        })

        self.A = None
        self.b = None
        self.b_error = None
        self.x_dummy = None
        self.stop_training_flag = False
        self.developer_mode = tk.BooleanVar(value=False)
        self.enable_live_plot = tk.BooleanVar(value=False)
        self.x_perturbation_scale = tk.DoubleVar(value=0.0)
        self.loss_threshold = tk.DoubleVar(value=1.0)
        self.initial_learning_rate = tk.DoubleVar(value=1.0)
        self.max_epochs = tk.IntVar(value=500000)
        self.selected_method = tk.StringVar(value="SpecKit (gradient + log-smoothness)")

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, pady=10, anchor="center")

        tk.Checkbutton(
            self.top_frame,
            text="Real-time plotting (update chart during training)",
            variable=self.enable_live_plot,
        ).pack(pady=5)

        tk.Checkbutton(
            self.top_frame,
            text="Developer Mode",
            variable=self.developer_mode,
            command=self.toggle_developer_widgets,
        ).pack(pady=5)

        tk.Label(self.top_frame, text="Select unfolding method").pack(pady=5)
        method_combo = ttk.Combobox(
            self.top_frame,
            textvariable=self.selected_method,
            values=list(METHODS.keys()),
            state="readonly",
            width=40,
        )
        method_combo.pack(pady=5)

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

        for widget in self.dev_widgets:
            widget.pack_forget()

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_user_input(self):
        if hasattr(self, 'scaling_factor'):
            delattr(self, 'scaling_factor')

        filename = filedialog.askopenfilename(title="Select the file containing equation data", filetypes=[("Text files", "*.txt;*.csv")])
        if filename:
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(filename, header=None, skiprows=0)
                else:
                    df = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=0)

                if df.shape[1] < 2:
                    raise ValueError("CSV file must contain at least two columns of data")

                self.A_header = df.iloc[0, 1:-2].to_numpy(dtype=np.float32)
                data = df.iloc[1:, 1:].to_numpy(dtype=np.float32)
                self.A = data[:, :-2]
                self.b = data[:, -2].reshape(-1, 1)
                self.b_error = data[:, -1].reshape(-1, 1)

                dof = self.b.shape[0]
                confidence_level = 0.95
                computed_loss_threshold = chi2.ppf(confidence_level, dof)
                self.loss_threshold.set(computed_loss_threshold)

                self.status_label.config(text="Equation data loaded successfully")
                self.check_ready()
            except Exception as e:
                messagebox.showerror("Error", f"Error reading data: {str(e)}")

    def load_initial_guess(self):
        if hasattr(self, 'scaling_factor'):
            delattr(self, 'scaling_factor')

        filename = filedialog.askopenfilename(
            title="Select the file containing the initial neutron spectrum flux values",
            filetypes=[("Text files", "*.txt;*.csv")]
        )

        if filename:
            try:
                df = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=1)
                if df.shape[1] < 2:
                    raise ValueError("File format error. Each line must contain at least two numbers (energy & flux).")
                x_data = df.iloc[:, 1].to_numpy(dtype=np.float32)
                if self.A is not None and len(x_data) != self.A.shape[1]:
                    raise ValueError(f"Number of initial values ({len(x_data)}) does not match "
                                     f"the number of unknowns in A ({self.A.shape[1]}).")
                self.x_dummy = x_data.reshape(1, -1)
                self.original_x_dummy = self.x_dummy.copy()
                self.status_label.config(text="Initial spectrum loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read initial spectrum file: {str(e)}")
        else:
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
        self.root.after(0, lambda: self.status_label.config(text="Training... please wait"))
        Thread(target=self.train_model, args=(loss_threshold_value,)).start()

    def stop_training(self):
        self.stop_training_flag = True

    def plot_results(self, loss_history, x_values):
        self.ax1.clear()
        if loss_history:
            self.ax1.plot(loss_history[5:] if len(loss_history) > 5 else loss_history, label="Training Loss", color='blue', linewidth=2)
        self.ax1.set_xlabel("Epochs")
        self.ax1.set_ylabel("Loss Value")
        self.ax1.set_title("Loss Function vs Training Epochs")
        if loss_history:
            self.ax1.legend()
        self.ax1.grid(True)

        self.ax2.clear()
        x_labels = np.array(self.A_header, dtype=float)
        flux = np.array(x_values, dtype=float)

        self.ax2.step(x_labels, flux, where='mid', color='orange', label="Group Flux (Φᵢ)")
        self.ax2.fill_between(x_labels, flux, step='mid', color='orange', alpha=0.5)

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

        try:
            print("Energy(MeV)            dPhi/dlnE")
            for e, u in zip(x_labels[mask], phi_u[mask]):
                print(f"{e:12.5e}    {u:12.5e}")
        except UnicodeEncodeError:
            pass

    def run_builtin_gradient(self, loss_threshold, b_vector):
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

            lam = 0.01
            loss = np.mean(np.square(error)) + lam * smoothness_penalty

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

            if epoch == 0:
                scaling_values = Ax_pred / b_vector.T
                scaling_factor = np.mean(scaling_values)
                print("scaling factor=", scaling_factor)
                x_variable = np.maximum(x_variable / scaling_factor, 1e-6)

            if len(loss_history) >= 500:
                recent_losses = loss_history[-500:]
                max_loss = max(recent_losses)
                min_loss_r = min(recent_losses)
                if abs(max_loss - min_loss_r) / max_loss < 1e-5:
                    print("Loss changed very little in last 500 epochs, stopping early")
                    break

            if self.enable_live_plot.get() and ((epoch + 1) % 100 == 0):
                self.plot_results(loss_history, x_variable.flatten())

            if loss < loss_threshold:
                break

        print("Final Loss (single run):", loss_history[-1])
        return x_variable, loss_history

    def run_one_training(self, loss_threshold, b_vector):
        method_name = self.selected_method.get()
        solve_func = METHODS[method_name]

        x0 = self.x_dummy.flatten().astype(float)
        A = np.array(self.A, dtype=float)
        b = np.array(b_vector, dtype=float).flatten()

        if solve_func is None:
            x_variable, loss_history = self.run_builtin_gradient(loss_threshold, b_vector)
        else:
            max_iterations = min(self.max_epochs.get(), 2000)
            tolerance = 1e-6
            x_result = call_solver(solve_func, A, b, x0, max_iterations, tolerance)
            x_variable = np.array(x_result).reshape(1, -1)
            loss_history = []

        return x_variable, loss_history

    def run_multiple_trainings(self):
        plt.close('all')
        gc.collect()
        for child in self.plot_frame.winfo_children():
            child.destroy()

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save inversion result to CSV",
        )
        if not save_path:
            messagebox.showwarning("Cancel Save", "No save path selected, training stopped.")
            self.start_button.config(state=tk.NORMAL)
            return

        loss_threshold = self.loss_threshold.get()
        original_x_dummy = self.x_dummy.copy()

        self.x_dummy = original_x_dummy.copy()
        b_vector = self.b  # single run, no Monte Carlo perturbation

        x_variable, loss_history = self.run_one_training(loss_threshold, b_vector)

        self.plot_results(loss_history, x_variable.flatten())
        all_results = [x_variable.flatten()]
        print("Total Flux: {:.3e}".format(x_variable.sum()))

        self.export_all_spectra_to_csv(all_results, save_path)
        self.start_button.config(state=tk.NORMAL)

    def export_all_spectra_to_csv(self, all_results, save_path):
        try:
            df = pd.DataFrame(all_results, columns=self.A_header)
            df.index = [f"Run_{i+1}" for i in range(len(all_results))]
            df.to_csv(save_path)
            print(f"Inversion result saved to: {save_path}")
        except Exception as e:
            print(f"Save failed: {e}")

    def save_canvas_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("PDF File", "*.pdf"), ("All Files", "*.*")],
            title="Select image save location",
        )
        if file_path:
            try:
                self.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                self.status_label.config(text=f"Image saved to: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"Failed to save image: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeuralSolverApp(root)
    root.mainloop()