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
        fig.patch.set_facecolor((0,0,0,0))
        self.ax_polar = fig.add_subplot(111, projection='polar')
        super().__init__(fig)
        self.setParent(parent)

class PolarPlotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        df = pd.read_csv('iss_location_data.csv')

        self.theta = np.radians(df['Longitude'].values)  # Convert longtitude to radians   0° longitude (the Prime Meridian).
        self.radius = (df['Latitude'].values + 90) / 180  # map to 0-->1 0 close to south pole 1 close to north pole

        self.canvas = MplCanvas(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
    

    def update_plot(self):
        # Stop the timer if we've reached the end of the data
        if self.current_index >= len(self.theta):
            self.timer.stop()
            return

        # move to next data point
        angle = self.theta[:self.current_index + 1]
        radius = self.radius[:self.current_index + 1]

        self.canvas.ax_polar.clear()
        self.canvas.ax_polar.plot(angle, radius, marker='o', linestyle='-', color='blue')
        self.canvas.ax_polar.set_title("Sequential Polar Plot of ISS Latitude and Longitude", pad=10)

        self.canvas.draw()
        self.current_index += 1

    def play_animation(self):
        self.timer.start(100)  # speed control

    def pause_animation(self):
        self.timer.stop()
