import sys
import os
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from utils import Utils
from statistics_window import StatisticsWindow
from interpolation_window import InterpolationWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from signal_plot_widget import SignalPlotWidget
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

import pandas as pd


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(12, 6))
        fig.patch.set_facecolor('#4D7B7E')
        self.ax_polar = fig.add_subplot(
            121, projection='polar')
        self.ax_3d = fig.add_subplot(
            122, projection='3d')
        self.ax_3d.set_facecolor((0, 0, 0, 0))
        super().__init__(fig)
        self.setParent(parent)


class PolarPlotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load the Excel file
        file_path = 'DAT.xlsx'
        df = pd.read_excel(file_path, header=None)

        # Extract phi and theta (angles)
        self.phi = df.iloc[1:, 1]  # Column B, skipping the header
        self.theta = df.iloc[1, 2:]  # Row 2, skipping the header

        # Remove any non-numeric values from phi and theta and convert them to numeric
        self.phi = pd.to_numeric(self.phi, errors='coerce').dropna().values
        self.theta = pd.to_numeric(self.theta, errors='coerce').dropna().values

        # Extract corresponding values (assuming they start from row 2, column C)
        self.values = df.iloc[2:, 2:].values

        # Convert angles to radians
        self.theta_radians = np.radians(self.theta)

        # Set up the canvas
        self.canvas = MplCanvas(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

        # Create and add a slider for phi values
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(37)
        self.slider.valueChanged.connect(
            self.slider_changed)  # Sync with user input
        layout.addWidget(self.slider)

        # Create the animation
        self.ani = FuncAnimation(
            self.canvas.figure, self.update_plot, frames=len(self.phi), interval=500)

        # Track whether the animation is playing
        self.is_paused = False
        self.current_frame = 0

        self.plot_3d()  # Plot the 3D data once

    def plot_3d(self):
        theta_mesh, phi_mesh = np.meshgrid(self.theta, self.phi)
        theta_rad = np.radians(theta_mesh)
        phi_rad = np.radians(phi_mesh)

        # Convert spherical coordinates to Cartesian coordinates
        x = self.values * np.sin(theta_rad) * np.cos(phi_rad)
        y = self.values * np.sin(theta_rad) * np.sin(phi_rad)
        z = self.values * np.cos(theta_rad)

        # Plot in 3D
        self.canvas.ax_3d.plot_surface(
            x, y, z, cmap='viridis', edgecolor='none')
        self.canvas.ax_3d.set_title('3D XYZ Plot of Spherical Data', pad=20)
        self.canvas.ax_3d.set_xlabel('X')
        self.canvas.ax_3d.set_ylabel('Y')
        self.canvas.ax_3d.set_zlabel('Z')

    def update_plot(self, phi_index):

        # Clear the previous polar plot
        self.canvas.ax_polar.clear()
        self.canvas.ax_polar.plot(
            self.theta_radians.T, self.values[phi_index, :], label=f'Phi {self.phi[phi_index]:.2f}')
        self.canvas.ax_polar.set_title(
            f'Polar Plot of Horn Antenna Propagation', pad=20)
        self.canvas.ax_polar.legend(
            title="Phi Angles", loc='upper right', bbox_to_anchor=(1.1, 1), borderaxespad=0.)
        self.slider.setValue(phi_index)
        self.canvas.draw()  # Refresh the canvas

    def slider_changed(self, value):
        self.slider.setValue(value)
        self.update_plot(value)
