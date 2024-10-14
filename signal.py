import numpy as np
import sys
from PyQt5 import QtWidgets


class Signal():

    def __init__(self, signal_data, color='b', title='signal', is_hidden=False, f_sample=100):
        self.data = signal_data
        self.color = color
        self.title = title
        self.is_hidden = is_hidden
        self.f_sample = f_sample
        self.time_axis = np.linspace(0, len(signal_data) / self.f_sample, len(signal_data))


    def change_color(self):
        # Open the color picker dialog
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            # print(self.color)

    def __lt__(self, other):
        return len(self.data) < len(other.data)
    
