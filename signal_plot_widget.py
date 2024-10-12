import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5 import QtGui, QtWidgets
from utils import Utils
from pyqtgraph import PlotWidget, QtCore
from PyQt5.QtCore import Qt


class SignalPlotWidget():
    
    is_linked = False
    syncing = False
    graph_instances = []
    speed_mapping = {
            0: 200,  # x1/2 speed
            1: 100,  # Original speed
            2: 50,   # x2 speed
            3: 25    # x4 speed
        }

    def __init__(self, is_playing=False, speed=1, window_range=(0, 30), timer=None, name=''):
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


    def toggle_signal(self, state, signal):
        if state == Qt.Checked:
            # Plot signal only if it's checked
            self.plot_widget.clear()
            self.plot_widget.plot(signal.data, pen=signal.color)
            self.plot_widget.setYRange(-1, 1)
            self.plot_widget.setTitle(self.title_input.text())
        else:
            self.plot_widget.clear()  # Clear the plot if unchecked

    def update_plot(self, signal, user_interacting):
        if self.is_playing and user_interacting:
            window_size = self.window_end - self.window_start # how much is visible at once
            self.window_start = (self.window_start + 1) % (len(signal.data) - window_size)
            self.window_end = self.window_start + window_size

    @staticmethod
    def link_viewports():
        # Sync the range and zoom between both graphs
        # The sigRangeChanged signal is part of the pyqtgraph library.
        SignalPlotWidget.graph_instances[0].plot_widget.sigRangeChanged.connect(SignalPlotWidget.sync_range)
        SignalPlotWidget.graph_instances[1].plot_widget.sigRangeChanged.connect(SignalPlotWidget.sync_range)

        # Sync the initial view range when linking
        SignalPlotWidget.sync_viewports()    

    @staticmethod
    def unlink_viewports():
        # Properly disconnect the range syncing behavior to stop linking
        SignalPlotWidget.graph_instances[0].plot_widget.sigRangeChanged.disconnect(SignalPlotWidget.sync_range)
        SignalPlotWidget.graph_instances[1].plot_widget.sigRangeChanged.disconnect(SignalPlotWidget.sync_range)

    @staticmethod
    def sync_viewports():
        # Ensure both graphs have the same zoom and pan when linked
        # returns a list containing two elements: the x-range and y-range
        range1 = SignalPlotWidget.graph_instances[0].plot_widget.viewRange()
        # Padding = 0 is used to prevent signal shrinking by preventing buffer space
        SignalPlotWidget.graph_instances[1].plot_widget.setXRange(*range1[0], padding=0)
        # The asterisk in here unpacks the tuple so that setXRange() receives two args: start&end of range
        SignalPlotWidget.graph_instances[1].plot_widget.setYRange(*range1[1], padding=0)

    @staticmethod
    def sync_range():
        if SignalPlotWidget.syncing:
            return  # Prevent recursive syncing
        SignalPlotWidget.syncing = True

        range2 = SignalPlotWidget.graph_instances[1].plot_widget.viewRange()
        SignalPlotWidget.graph_instances[0].plot_widget.setXRange(*range2[0], padding=0)
        SignalPlotWidget.graph_instances[0].plot_widget.setYRange(*range2[1], padding=0)

        SignalPlotWidget.syncing = False


