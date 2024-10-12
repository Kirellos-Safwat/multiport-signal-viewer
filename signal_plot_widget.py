import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5 import QtGui, QtWidgets

class SignalPlotWidget():
    def __init__(self, is_playing=False, speed=1.0, window_range=(0, 30), linked=False, timer=None):
        super().__init__()
        self.is_playing = is_playing
        self.speed = speed
        self.window_range = window_range
        self.linked = linked
        self.timer = timer
        self.window_start, self.window_end = window_range

        # Create a PlotWidget
        self.plot_widget = PlotWidget()
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.plot_widget.setBackground('#001414')
        # Fix the dimensions of the plot widgets (width, height)
        self.plot_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
