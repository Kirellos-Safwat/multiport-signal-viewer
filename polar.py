import sys
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 6))
        fig.patch.set_facecolor((0, 0, 0, 0))
        self.ax_polar = fig.add_subplot(111, projection='polar')
        super().__init__(fig)
        self.setParent(parent)

class PolarPlotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        df = pd.read_csv('iss_location_data.csv')

        self.theta = np.radians(df['Longitude'].values)  # Convert longitude to radians
        self.radius = (df['Latitude'].values + 90) / 180  # Normalize latitude to [0, 1]

        
        self.canvas = MplCanvas(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.canvas.ax_polar.set_title("Sequential Polar Plot of ISS Latitude and Longitude", pad=10, color='white')
        self.canvas.ax_polar.tick_params(colors="#a6a4a1")  

        # Speed slider
        self.speed_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 20)  # Set range for speed factor (1 is slowest, 20 is fastest)
        self.speed_slider.setValue(10)  # Default speed factor
        self.speed_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.update_speed)
        layout.addWidget(self.speed_slider)

        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.update_speed()

    def update_plot(self):
        if self.current_index >= len(self.theta):
            self.timer.stop()
            return

        # Update the plot with the next data point
        angle = self.theta[:self.current_index + 1]
        radius = self.radius[:self.current_index + 1]

        self.canvas.ax_polar.clear()
        self.canvas.ax_polar.plot(angle, radius, marker='o', linestyle='-', color='blue')

        self.canvas.draw()
        self.current_index += 1

    def play_animation(self):
        self.timer.start() 

    def pause_animation(self):
        self.timer.stop()

    def update_speed(self):
        speed_factor = self.speed_slider.value()
        interval = int(2000 / speed_factor)
        self.timer.setInterval(interval)
