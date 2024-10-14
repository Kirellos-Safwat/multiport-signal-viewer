import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5 import QtGui, QtWidgets
from utils import Utils
from pyqtgraph import PlotWidget, QtCore
from PyQt5.QtCore import Qt
from signal import Signal

class SignalPlotWidget():
    
    is_linked = False
    syncing = False
    user_interacting = False
    stopped_by_link = False
    graph_instances = []
    speed_mapping = {
            0: 200,  # x1/2 speed
            1: 100,  # Original speed
            2: 50,   # x2 speed
            3: 25    # x4 speed
        }

    def __init__(self, signals, is_playing=False, speed=1, window_range=(0, 30), timer=None, name='', preserve_zoom = False):
        super().__init__()
        self.signals = signals
        self.is_playing = is_playing
        self.speed = speed
        self.window_range = window_range
        self.timer = timer
        self.name = name
        self.window_start, self.window_end = window_range
        self.preserve_zoom = preserve_zoom  # Flag to preserve zoom level

        self.selected_signal = self.signals[0]
        self.max_length = len(max(self.signals).data)
        self.max_time_axis = np.linspace(0, 100, self.max_length)
        self.other = None

        self.yMin = min(min(signal.data) for signal in self.signals) if self.signals else self.yMin
        self.yMax = max(max(signal.data) for signal in self.signals) if self.signals else self.yMax

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
        
        # event listeners for mouse panning
        self.plot_widget.scene().sigMouseClicked.connect(self.on_user_interaction_start)
        self.plot_widget.sigRangeChanged.connect(self.on_user_interaction_start)

        # show/hide checkBox
        self.show_hide_checkbox = QtWidgets.QCheckBox("Show" + self.name)
        # Style the checkbox with white text and better appearance
        self.show_hide_checkbox.setStyleSheet(Utils.checkBox_style_sheet)
        # Keep the behavior intact
        self.show_hide_checkbox.setChecked(True)
        self.show_hide_checkbox.stateChanged.connect(self.toggle_signal)
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

                
        # Setting the Control buttons for Signal 2:
        # Creating "horizontal" layout for the buttons of signal 2:
        self.play_pause_button = Utils.create_button("", self.play_pause_signal, "play")

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.play_pause_button)

        self.stop_signal_button = Utils.create_button(f"", self.stop_signal, "rewind")
        self.button_layout.addWidget(self.stop_signal_button)

        # change color button
        self.button_layout.addWidget(Utils.create_button(f"", lambda:(self.selected_signal.change_color(), self.plot_signals()), "color"))

        self.zoom_in_button = Utils.create_button(f"", self.zoom_in, "zoom_in")
        self.button_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = Utils.create_button(f"", self.zoom_out, "zoom_out")
        self.button_layout.addWidget(self.zoom_out_button)

        self.button_layout.addWidget(Utils.create_button(f"", self.show_statistics, "statistics"))
        self.button_layout.addWidget(Utils.create_button("", lambda: (Utils.import_signal_file(self), self.update_graph()), "import"))

        self.button_layout.addStretch()  # Prevents the buttons from stretching

        self.graph_layout.addWidget(self.plot_widget)
        self.controls_layout.addWidget(self.title_input)
        self.controls_layout.addWidget(self.show_hide_checkbox)
        self.controls_layout.addLayout(self.speed_layout)
        self.graph_layout.addLayout(self.controls_layout)

        SignalPlotWidget.graph_instances.append(self)
        if len(SignalPlotWidget.graph_instances) == 2:
            self.other = SignalPlotWidget.graph_instances[0]
            self.other.other = self

    def update_graph(self):
        self.selected_signal = self.signals[-1]
        self.max_length = len(max(self.signals).data)
        self.max_time_axis = np.linspace(0, 100, self.max_length)
        self.yMin = min(min(self.signals[-1].data), self.yMin)
        self.yMax = max(max(self.signals[-1].data), self.yMin)
        self.plot_signals()

    def on_user_interaction_start(self):
        SignalPlotWidget.user_interacting = True  # Set the flag to true when the user starts interacting

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
            self.other.speed_slider.setValue(current_value)

    def sync_checkboxes(self):
        if SignalPlotWidget.is_linked:
            self.other.show_hide_checkbox.setChecked(self.show_hide_checkbox.isChecked())


    def toggle_signal(self, state):
        if state == Qt.Checked:
            # Plot signal only if it's checked
            self.plot_widget.clear()
            for signal in self.signals:
                self.plot_widget.plot(self.max_time_axis, signal.data, pen=signal.color)
            self.plot_widget.setYRange(-1, 1)
            self.plot_widget.setTitle(self.title_input.text())
        else:
            self.plot_widget.clear()  # Clear the plot if unchecked

    def update_plot(self, user_interacting):
        if self.is_playing and user_interacting:
            window_size = self.window_end - self.window_start # how much is visible at once
            self.window_start = (self.window_start + 1) % (len(self.selected_signal.data) - window_size) # ??
            self.window_end = self.window_start + window_size
            self.plot_signals()

    @staticmethod
    def link_viewports():
        # Sync the range and zoom between both graphs
        # The sigRangeChanged signal is part of the pyqtgraph library.
        SignalPlotWidget.graph_instances[0].plot_widget.sigRangeChanged.connect(SignalPlotWidget.graph_instances[0].sync_range)
        SignalPlotWidget.graph_instances[1].plot_widget.sigRangeChanged.connect(SignalPlotWidget.graph_instances[1].sync_range)
        # Sync the initial view range when linking
        SignalPlotWidget.sync_viewports()    

    def unlink_viewports(self):
        # Properly disconnect the range syncing behavior to stop linking
        SignalPlotWidget.graph_instances[0].plot_widget.sigRangeChanged.disconnect(SignalPlotWidget.graph_instances[0].sync_range)
        SignalPlotWidget.graph_instances[1].plot_widget.sigRangeChanged.disconnect(SignalPlotWidget.graph_instances[1].sync_range)

    @staticmethod
    def sync_viewports():
        # Ensure both graphs have the same zoom and pan when linked
        # returns a list containing two elements: the x-range and y-range
        range1 = SignalPlotWidget.graph_instances[0].plot_widget.viewRange()
        # Padding = 0 is used to prevent signal shrinking by preventing buffer space
        SignalPlotWidget.graph_instances[1].plot_widget.setXRange(*range1[0], padding=0)
        # The asterisk in here unpacks the tuple so that setXRange() receives two args: start&end of range
        SignalPlotWidget.graph_instances[1].plot_widget.setYRange(*range1[1], padding=0)

    def sync_range(self):
        if SignalPlotWidget.syncing:
            return  # Prevent recursive syncing
        SignalPlotWidget.syncing = True

        range_ = self.plot_widget.viewRange()
        self.other.plot_widget.setXRange(*range_[0], padding=0)
        self.other.plot_widget.setYRange(*range_[1], padding=0)

        SignalPlotWidget.syncing = False

    def show_statistics(self):
        self.statistics_window = StatisticsWindow(
            self.selected_signal.data, self.selected_signal.title, self.selected_signal.color)  # Generating the Statistics Window
        self.statistics_window.show()  # Showing the Statistics Window
    
    def play_pause_signal(self):
        if self.show_hide_checkbox.isChecked():
            if not self.is_playing:
                self.is_playing = True
                self.play_pause_button = Utils.update_button(
                    self.play_pause_button, "", "pause")
                if self.timer is None:
                    # Creates a timer where the plot would be updated with new data, allowing real-time visualization of signal.
                    self.timer = pg.QtCore.QTimer()
                    self.timer.timeout.connect(lambda: 
                    (self.update_plot(SignalPlotWidget.user_interacting)))
                    self.timer.start(100)  # Frequent updates every 100ms
                if SignalPlotWidget.is_linked and not self.other.is_playing:
                    self.other.play_pause_signal()

            else:
                self.is_playing = False
                self.play_pause_button = Utils.update_button(
                    self.play_pause_button, "", "play")
                if SignalPlotWidget.is_linked and self.other.is_playing:
                    self.other.play_pause_signal()


    # Generating the function of plotting the signals, giving them titles, and setting their Y-range from -1 to 1
    def plot_signals(self):
        # The clear method is used to clear the frame every time before making the new frame!
        self.plot_widget.clear()
        # The clear method is used to clear the frame every time before making the new frame!
        self.other.plot_widget.clear()

        # Store original x and y ranges after the first plot
        if not self.preserve_zoom:
            self.original_x_range = self.plot_widget.viewRange()[0]
            self.original_y_range = self.plot_widget.viewRange()[1]

        # # Enable panning
        # self.plot_widget.setMouseEnabled(x=True, y=True)

        # Store original x and y ranges after the first plot
        if not self.preserve_zoom:
            self.original_x_range2 = self.other.plot_widget.viewRange()[0]
            self.original_y_range2 = self.other.plot_widget.viewRange()[1]

        # # Enable panning
        # self.other.plot_widget.setMouseEnabled(x=True, y=True)

        # Synchronize the zoom and pan if linked
        if SignalPlotWidget.is_linked:
            SignalPlotWidget.sync_viewports()  # Initial sync on plotting

        if self.show_hide_checkbox.isChecked():
            for signal in self.signals:
                self.plot_widget.plot(signal.time_axis, signal.data, pen=signal.color)

            if SignalPlotWidget.user_interacting:
                current_time_window = self.max_time_axis[self.window_start:self.window_end]
                self.plot_widget.setXRange(
                    min(current_time_window), max(current_time_window), padding=0)

            # Keep Y-axis range fixed for signal1
            if not self.preserve_zoom:    
                self.plot_widget.setYRange(-1, 1)
            self.plot_widget.setTitle(self.title_input.text())

            # Allow panning but set limis
            self.plot_widget.setLimits(
                xMin=min(self.max_time_axis), xMax=max(self.max_time_axis),yMin=self.yMin,yMax=self.yMax)

        if self.other.show_hide_checkbox.isChecked():
            for signal in self.other.signals:
                self.other.plot_widget.plot(signal.time_axis, signal.data, pen=signal.color)

            # case of user interaction
            if SignalPlotWidget.user_interacting:
                current_time_window = self.other.max_time_axis[self.other.window_start:self.other.window_end]
                self.other.plot_widget.setXRange(
                    min(current_time_window), max(current_time_window), padding=0)

            # self.other.plot_widget.setYRange(-1, 1)
            self.other.plot_widget.setTitle(self.other.title_input.text())

            # Allow panning but set limis
            self.other.plot_widget.setLimits(
                xMin=min(self.other.max_time_axis), xMax=max(self.other.max_time_axis), yMin=self.other.yMin, yMax=self.other.yMax)

    def stop_signal(self):
        if self.show_hide_checkbox.isChecked():
            self.is_playing = not self.is_playing
            self.play_pause_signal()
            if SignalPlotWidget.is_linked and not SignalPlotWidget.stopped_by_link:
                SignalPlotWidget.stopped_by_link = True
                self.other.stop_signal()
            # Reset the signal and its position
            # Reset playback window to the beginning
        self.window_start = 0
        self.window_end = min(30, self.max_length)  # Ensure it does not exceed the signal length
        SignalPlotWidget.stopped_by_link = False
        self.plot_signals()

    def zoom_in(self):
        if isinstance(self.plot_widget, PlotWidget):
            x_range = self.plot_widget.viewRange()[0]
            y_range = self.plot_widget.viewRange()[1]

            # Use the same scale factor for both zoom in and out
            zoom_factor_x = 0.16  # Adjust this value if necessary
            zoom_factor_y = 0.105  # Adjust this value if necessary


            # Calculate the new ranges
            new_x_range = (x_range[0] + (x_range[1] - x_range[0]) * zoom_factor_x,
                        x_range[1] - (x_range[1] - x_range[0]) * zoom_factor_x)
            new_y_range = (y_range[0] + (y_range[1] - y_range[0]) * zoom_factor_y,
                        y_range[1] - (y_range[1] - y_range[0]) * zoom_factor_y)

            # Set new ranges
            self.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

            if SignalPlotWidget.is_linked:
                self.other.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
                self.other.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
            self.preserve_zoom = True

    def zoom_out(self):
        if isinstance(self.plot_widget, PlotWidget):
            x_range = self.plot_widget.viewRange()[0]
            y_range = self.plot_widget.viewRange()[1]

            # Use the same scale factor for both zoom in and out
            zoom_factor_x = 0.21 # Adjust this value if necessary
            zoom_factor_y = 0.42 # Adjust this value if necessary

            # Calculate the new ranges
            new_x_range = (x_range[0] - (x_range[1] - x_range[0]) * zoom_factor_x,
                        x_range[1] + (x_range[1] - x_range[0]) * zoom_factor_x)
            new_y_range = (y_range[0] - (y_range[1] - y_range[0]) * zoom_factor_y,
                        y_range[1] + (y_range[1] - y_range[0]) * zoom_factor_y)

            # Set new ranges
            self.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

            if SignalPlotWidget.is_linked:
                self.other.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
                self.other.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
            self.preserve_zoom = True
