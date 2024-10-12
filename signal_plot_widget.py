import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5 import QtGui, QtWidgets
from utils import Utils
from pyqtgraph import PlotWidget, QtCore


class SignalPlotWidget():
    
    is_linked = False
    graph_instances = []
    speed_mapping = {
            0: 200,  # x1/2 speed
            1: 100,  # Original speed
            2: 50,   # x2 speed
            3: 25    # x4 speed
        }

    def __init__(self, is_playing=False, speed=1, window_range=(0, 30), timer=None, name='Graph'):
        super().__init__()
        self.is_playing = is_playing
        self.speed = speed
        self.window_range = window_range
        self.timer = timer
        self.name = name
        self.window_start, self.window_end = window_range

        # graph layout
        self.graph_layout = QtWidgets.QHBoxLayout()
        # buttons layout
        self.controls_layout = QtWidgets.QVBoxLayout()
        # Create a PlotWidget
        self.plot_widget = PlotWidget()
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.plot_widget.setBackground('#001414')
        # Fix the dimensions of the plot widgets (width, height)
        self.plot_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # show/hide checkBox
        self.show_hide_checkbox = QtWidgets.QCheckBox("Show" + self.name)
        # Style the checkbox with white text and better appearance
        self.show_hide_checkbox.setStyleSheet(Utils.checkBox_style_sheet)
        # Keep the behavior intact
        self.show_hide_checkbox.setChecked(True)
        # self.show_hide_checkbox.stateChanged.connect(lambda: print('test'))
        self.show_hide_checkbox.stateChanged.connect(self.sync_checkboxes)
        
        # Create title input for Signal 1
        self.title_input = QtWidgets.QLineEdit(self.name)
        self.title_input.setFixedWidth(150)  # Limit the width 
        self.title_input.setStyleSheet(Utils.lineEdit_style_sheet)
        self.title_input.setAlignment(QtCore.Qt.AlignCenter)  # Center align the text
        self.title_input.textChanged.connect(self.update_signal_titles)

        # speed slider
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setMinimum(0)  # x1/2
        self.speed_slider.setMaximum(3)  # x4
        self.speed_slider.setValue(speed)    # Start at original speed
        self.speed_slider.setTickInterval(1)  # Each tick represents one unit
        self.speed_slider.setFixedWidth(150)  # Set your desired fixed width

        # Create a label above the slider
        self.speed_label = QtWidgets.QLabel("Signal 1 speed control: ")
        self.speed_label.setStyleSheet(Utils.label_style_sheet)

        # Add the label and slider to a vertical layout
        self.speed_layout = QtWidgets.QVBoxLayout()
        self.speed_layout.addStretch()
        self.speed_layout.addWidget(self.speed_label)
        self.speed_layout.addWidget(self.speed_slider)
        # Apply a custom stylesheet for the QSlider
        self.speed_slider.setStyleSheet(Utils.slider_style_sheet)
        # Connect lambda: print('test')d
        self.speed_slider.valueChanged.connect(self.update_timer_speed)

        self.graph_layout.addWidget(self.plot_widget)
        self.controls_layout.addWidget(self.title_input)
        self.controls_layout.addWidget(self.show_hide_checkbox)
        self.controls_layout.addLayout(self.speed_layout)
        self.graph_layout.addLayout(self.controls_layout)

        SignalPlotWidget.graph_instances.append(self)
    # def show_hide_toggle(self, state):
    #     if state == Qt.Checked:
    #         # Plot signal1 only if it's checked
    #         self.first_graph.plot_widget.clear()
    #         self.first_graph.plot_widget.plot(self.signal1.data, pen=self.signal1.color)
    #         self.first_graph.plot_widget.setYRange(-1, 1)
    #         self.first_graph.plot_widget.setTitle(self.title_input1.text())
    #     else:
    #         self.first_graph.plot_widget.clear() 

    def update_signal_titles(self):
        """ Updates the plot titles dynamically as the user changes the title inputs. """
        self.plot_widget.setTitle(self.title_input.text())

    def update_timer_speed(self):
        # Get the current slider value for Signal 1
        current_value = self.speed_slider.value()

        # Update the timer interval based on the slider value
        new_timer_interval = SignalPlotWidget.speed_mapping[current_value]

        if self.timer is not None:
            self.timer.setInterval(new_timer_interval)

        # If signals are linked, update the other slider
        if SignalPlotWidget.is_linked:
            for other in SignalPlotWidget.graph_instances:
                if other is not self:
                    other.speed_slider.setValue(current_value)

    def sync_checkboxes(self):
        if SignalPlotWidget.is_linked:
            for other in SignalPlotWidget.graph_instances:
                if other is not self:
                    # Sync checkbox 1 with checkbox 2
                    other.show_hide_checkbox.setChecked(self.show_hide_checkbox.isChecked())


                    
