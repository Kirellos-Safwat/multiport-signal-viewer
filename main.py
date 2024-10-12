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
from signal import Signal
from signal_plot_widget import SignalPlotWidget


class SignalApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stopped_by_link = False  # For the linking feature

        # Initializing Signals' colors, ranges, types and titles
        self.signal1 = Signal(self.generate_square_wave(100), 'b')
        self.signal2 = Signal(self.generate_cosine_wave(100), 'r')
        self.type1 = 'square'
        self.type2 = 'cosine'

        self.initUI()
            # Initialize the original ranges after setting up the plot
        self.original_x_range = self.first_graph.plot_widget.viewRange()[0]  # Get the initial x range
        self.original_y_range = self.first_graph.plot_widget.viewRange()[1]  # Get the initial y range
                   # Initialize the original ranges after setting up the plot
        self.original_x_range = self.second_graph.plot_widget.viewRange()[0]  # Get the initial x range
        self.original_y_range = self.second_graph.plot_widget.viewRange()[1]  # Get the initial y range

        # Link state Flag
        SignalPlotWidget.is_linked = False
        # Sync Flag
        self.syncing = False

        self.second_graph.is_playing = False


        self.user_interacting = False  # Flag to allow mouse panning
        # Plotting Siganls with initialized properties
        self.plot_signals()

    def initUI(self):
        self.setWindowTitle("Multi-Channel Signal Viewer")  # Window Title
        self.setWindowIcon(QtGui.QIcon("assets\\Pulse.png"))  # Window Icon

        # Dark Grey Color for the Window Background
        self.setStyleSheet(Utils.window_style_sheet)

        # Setting the Main layout (Organizing Structure On Top Of Each Other)
        # Vertical Layout for the positioning of child widgets within a parent widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Creating signals plotting widgets
        self.first_graph = SignalPlotWidget(name='Graph One')
        self.second_graph = SignalPlotWidget(name='Graph Two')

        # Setting the Control buttons for Signal 1:
        # Creating "horizontal" layout for the buttons of signal 1:
        self.play_pause_button1 = Utils.create_button("", self.play_pause_signal1, "play")

        # Creating import signal button
        self.import_signal1_button = Utils.create_button("", lambda: Utils.import_signal_file(self.signal1), "import")

        button_layout1 = self.create_button_layout(
            self.play_pause_button1, 
            self.stop_signal1, 
            lambda: (self.signal1.change_color(), self.plot_signals()), 
            lambda: self.zoom_in(self.first_graph.plot_widget), 
            lambda: self.zoom_out(self.first_graph.plot_widget), 
            lambda: self.show_statistics(self.signal1.data, self.signal1.title, self.signal1.color),
            self.import_signal1_button
        )

        # Setting the Control buttons for Signal 2:
        # Creating "horizontal" layout for the buttons of signal 2:
        self.play_pause_button2 = Utils.create_button("", self.play_pause_signal2, "play")

        # Creating import signal button
        self.import_signal2_button = Utils.create_button("", lambda: Utils.import_signal_file(self.signal2), "import")

        button_layout2 = self.create_button_layout(
            self.play_pause_button2, 
            self.stop_signal2, 
            lambda: (self.signal2.change_color(), self.plot_signals()), 
            lambda: self.zoom_in(self.second_graph.plot_widget), 
            lambda: self.zoom_out(self.second_graph.plot_widget), 
            lambda: self.show_statistics(self.signal2.data, self.signal2.title, self.signal2.color),
            self.import_signal2_button
        )

        # Swap Signals Button
        self.swap_button = Utils.create_button("", self.swap_signals, "swap")

        self.glue_button = Utils.create_button("Glue Signals", self.glue_signals)

        # Link Button
        self.link_button = Utils.create_button("", self.toggle_link, "link")

        # event listeners for mouse panning
        self.first_graph.plot_widget.scene().sigMouseClicked.connect(self.on_user_interaction_start)
        self.first_graph.plot_widget.sigRangeChanged.connect(self.on_user_interaction_start)

        self.second_graph.plot_widget.scene().sigMouseClicked.connect(self.on_user_interaction_start)
        self.second_graph.plot_widget.sigRangeChanged.connect(self.on_user_interaction_start)
        self.main_layout.addLayout(self.first_graph.graph_layout)
        
        # Adding the "horizontal" button layout of signal 1 to the main "vertical" layout
        self.main_layout.addLayout(button_layout1)
        button_layout1.addStretch()  # Prevents the buttons from stretching
        button_layout1.addStretch()



        self.main_layout.addLayout(self.second_graph.graph_layout)
        # Adding the "horizontal" button layout of signal 2 to the main "vertical" layout
        self.main_layout.addLayout(button_layout2)
        button_layout2.addStretch()  # Prevents the buttons from stretching
        button_layout2.addStretch()



        # self.main_layout.addWidget(self.link_button)
        buttons_layout_3 = QtWidgets.QHBoxLayout()
        buttons_layout_3.addStretch()
        buttons_layout_3.addStretch()
        buttons_layout_3.addStretch()
        buttons_layout_3.addStretch()
        buttons_layout_3.addStretch()

        buttons_layout_3.addWidget(self.swap_button)
        buttons_layout_3.addWidget(self.link_button)
        buttons_layout_3.addWidget(self.glue_button)

        self.main_layout.addLayout(buttons_layout_3)  

        # connect methods to buttons
        self.first_graph.show_hide_checkbox.stateChanged.connect(lambda state: self.first_graph.toggle_signal(state, self.signal1))

        self.second_graph.show_hide_checkbox.stateChanged.connect(lambda state: self.second_graph.toggle_signal(state, self.signal2))
        
    def on_user_interaction_start(self):
        self.user_interacting = True  # Set the flag to true when the user starts interacting

    def on_user_interaction_end(self):
        self.user_interacting = False  # Reset the flag after interaction ends

    # Generating the function responsible for linking/unlinking graphs
    def toggle_link(self):
        SignalPlotWidget.is_linked = not SignalPlotWidget.is_linked
        # Sync play state if linked
        if SignalPlotWidget.is_linked:
            # Sync the visibility of the checkboxes
            self.second_graph.show_hide_checkbox.setChecked(
                self.first_graph.show_hide_checkbox.isChecked())
            self.link_button = Utils.update_button(
                self.link_button, "", "unlink")
        # This is dedicated to the case where one of the signals is already playing before linking the 2 graphs together
            if self.first_graph.is_playing:
                self.play_pause_signal2()
            elif self.second_graph.is_playing:
                self.play_pause_signal1()

            # Determine the lower speed and set both sliders
            lower_speed_index = min(
                self.first_graph.speed_slider.value(), self.second_graph.speed_slider.value())
            self.first_graph.speed_slider.setValue(lower_speed_index)
            self.second_graph.speed_slider.setValue(lower_speed_index)

            new_timer_interval = SignalPlotWidget.speed_mapping[lower_speed_index]
            if self.first_graph.timer is not None:
                self.first_graph.timer.setInterval(new_timer_interval)
            if self.second_graph.timer is not None:
                self.second_graph.timer.setInterval(new_timer_interval)
            SignalPlotWidget.link_viewports()
        else:
            self.link_button = Utils.update_button(
                self.link_button, "", "link")
            SignalPlotWidget.unlink_viewports()

        # Ensure consistent signal speeds
        if SignalPlotWidget.is_linked:
            # Check if both timers are running and have the same interval
            if self.first_graph.timer is not None and self.second_graph.timer is not None:
                if self.first_graph.timer.interval() != self.second_graph.timer.interval():
                    self.second_graph.timer.setInterval(
                        self.first_graph.timer.interval())  # Sync intervals


    # A method for Setting the horizontal layout of the buttons according to the signal_name

    def create_button_layout(self, play_pause_button, stop, color_change, zoom_in, zoom_out, statistics, import_signal_file):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(play_pause_button)
        button_layout.addWidget(Utils.create_button(f"", stop, "rewind"))
        button_layout.addWidget(Utils.create_button(
            
            f"", color_change, "color"))
        button_layout.addWidget(Utils.create_button(
            f"", zoom_in, "zoom_in"))
        button_layout.addWidget(Utils.create_button(
            f"", zoom_out, "zoom_out"))
        button_layout.addWidget(Utils.create_button(
            f"", statistics, "statistics"))
        button_layout.addWidget(import_signal_file)
        return button_layout

    # Generating the square wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=1 when t<0.5 and f=0 when t>0.5

    def generate_square_wave(self, points):
        t = np.linspace(0, 1, points)
        return (t < 0.5).astype(int)

    # Generating the cosine wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=cos(2*pi*F*t) for a periodic function of freq = 5Hz
    def generate_cosine_wave(self, points):
        t = np.linspace(0, 1, points)
        return (np.cos(2*np.pi*5*t))

    # Generating the function of plotting the signals, giving them titles, and setting their Y-range from -1 to 1
    def plot_signals(self):
        # The clear method is used to clear the frame every time before making the new frame!
        self.first_graph.plot_widget.clear()
        # The clear method is used to clear the frame every time before making the new frame!
        self.second_graph.plot_widget.clear()

        # Store original x and y ranges after the first plot
        self.original_x_range = self.first_graph.plot_widget.viewRange()[0]
        self.original_y_range = self.first_graph.plot_widget.viewRange()[1]

        # Enable panning
        self.first_graph.plot_widget.setMouseEnabled(x=True, y=True)

        # Store original x and y ranges after the first plot
        self.original_x_range2 = self.second_graph.plot_widget.viewRange()[0]
        self.original_y_range2 = self.second_graph.plot_widget.viewRange()[1]

        # Enable panning
        self.second_graph.plot_widget.setMouseEnabled(x=True, y=True)

        # Synchronize the zoom and pan if linked
        if SignalPlotWidget.is_linked:
            SignalPlotWidget.sync_viewports()  # Initial sync on plotting

        if self.first_graph.show_hide_checkbox.isChecked():
            self.first_graph.plot_widget.plot(self.signal1.time_axis, self.signal1.data, pen=self.signal1.color)

            if self.user_interacting:
                current_time_window = self.signal1.time_axis[self.first_graph.window_start:self.first_graph.window_end]
                self.first_graph.plot_widget.setXRange(
                    min(current_time_window), max(current_time_window), padding=0)

            # Keep Y-axis range fixed for signal1
            self.first_graph.plot_widget.setYRange(-1, 1)
            self.first_graph.plot_widget.setTitle(self.first_graph.title_input.text())

            # Allow panning but set limis
            self.first_graph.plot_widget.setLimits(
                xMin=min(self.signal1.time_axis), xMax=max(self.signal1.time_axis),yMin=min(self.signal1.data),yMax=max(self.signal1.data))

        if self.second_graph.show_hide_checkbox.isChecked():
            self.second_graph.plot_widget.plot(self.signal2.time_axis, self.signal2.data, pen=self.signal2.color)

            # case of user interaction
            if self.user_interacting:
                current_time_window = self.signal2.time_axis[self.second_graph.window_start:self.second_graph.window_end]
                self.second_graph.plot_widget.setXRange(
                    min(current_time_window), max(current_time_window), padding=0)

            self.second_graph.plot_widget.setYRange(-1, 1)
            self.second_graph.plot_widget.setTitle(self.second_graph.title_input.text())

            # Allow panning but set limis
            self.second_graph.plot_widget.setLimits(
                xMin=min(self.signal2.time_axis), xMax=max(self.signal2.time_axis),yMin=min(self.signal2.data),yMax=max(self.signal2.data))

    # Generating the function of playing signal 1
    def play_pause_signal1(self):
        if self.first_graph.show_hide_checkbox.isChecked():
            if not self.first_graph.is_playing:
                self.first_graph.is_playing = True
                self.play_pause_button1 = Utils.update_button(
                    self.play_pause_button1, "", "pause")
                if self.first_graph.timer is None:
                    # Creates a timer where the plot would be updated with new data, allowing real-time visualization of signal.
                    self.first_graph.timer = pg.QtCore.QTimer()
                    self.first_graph.timer.timeout.connect(lambda: 
                    (self.first_graph.update_plot(self.signal1, self.user_interacting), self.plot_signals()))
                    self.first_graph.timer.start(100)  # Frequent updates every 100ms
                if SignalPlotWidget.is_linked and not self.second_graph.is_playing:
                    self.play_pause_signal2()

            else:
                self.first_graph.is_playing = False
                self.play_pause_button1 = Utils.update_button(
                    self.play_pause_button1, "", "play")
                if SignalPlotWidget.is_linked and self.second_graph.is_playing:
                    self.play_pause_signal2()

    # Generating the function of stopping/resetting signal 1
    def stop_signal1(self):
        if self.first_graph.show_hide_checkbox.isChecked():
            if self.first_graph.timer is not None:
                self.first_graph.timer.stop()
                self.first_graph.timer = None
            self.first_graph.is_playing = False
            self.play_pause_button1 = Utils.update_button(
                self.play_pause_button1, "", "play")
            if SignalPlotWidget.is_linked and not self.stopped_by_link:
                self.stopped_by_link = True
                self.stop_signal2()
            self.plot_signals()
            self.stopped_by_link = False

    # Generating the function of playing signal 2
    def play_pause_signal2(self):
        if self.second_graph.show_hide_checkbox.isChecked():
            if not self.second_graph.is_playing:
                self.second_graph.is_playing = True
                self.play_pause_button2 = Utils.update_button(
                    self.play_pause_button2, "", "pause")
                if self.second_graph.timer is None:
                    self.second_graph.timer = pg.QtCore.QTimer()
                    self.second_graph.timer.timeout.connect(lambda: 
                    (self.second_graph.update_plot(self.signal2, self.user_interacting), self.plot_signals()))
                    self.second_graph.timer.start(100)
                if SignalPlotWidget.is_linked and not self.first_graph.is_playing:
                    self.play_pause_signal1()

            else:
                self.second_graph.is_playing = False
                self.play_pause_button2 = Utils.update_button(
                    self.play_pause_button2, "", "play")
                if SignalPlotWidget.is_linked and self.first_graph.is_playing:
                    self.play_pause_signal1()

    # Generating the function of stopping/resetting signal 2
    def stop_signal2(self):
        if self.second_graph.show_hide_checkbox.isChecked():
            if self.second_graph.timer is not None:
                self.second_graph.timer.stop()
                self.second_graph.timer = None
            self.second_graph.is_playing = False
            self.play_pause_button2 = Utils.update_button(
                self.play_pause_button2, "", "play")
            if SignalPlotWidget.is_linked and not self.stopped_by_link:
                self.stopped_by_link = True
                self.stop_signal1()
            self.plot_signals()
            self.stopped_by_link = False

    def zoom_in(self, plot_widget):
        if isinstance(plot_widget, PlotWidget):
            x_range = plot_widget.viewRange()[0]
            y_range = plot_widget.viewRange()[1]

            # Use the same scale factor for both zoom in and out
            zoom_factor_x = 0.16  # Adjust this value if necessary
            zoom_factor_y = 0.105  # Adjust this value if necessary


            # Calculate the new ranges
            new_x_range = (x_range[0] + (x_range[1] - x_range[0]) * zoom_factor_x,
                        x_range[1] - (x_range[1] - x_range[0]) * zoom_factor_x)
            new_y_range = (y_range[0] + (y_range[1] - y_range[0]) * zoom_factor_y,
                        y_range[1] - (y_range[1] - y_range[0]) * zoom_factor_y)

            # Set new ranges
            plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
            plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

            if SignalPlotWidget.is_linked:
                self.second_graph.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
                self.second_graph.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

    def zoom_out(self, plot_widget):
        if isinstance(plot_widget, PlotWidget):
            x_range = plot_widget.viewRange()[0]
            y_range = plot_widget.viewRange()[1]

            # Use the same scale factor for both zoom in and out
            zoom_factor_x = 0.21 # Adjust this value if necessary
            zoom_factor_y = 0.42 # Adjust this value if necessary

            # Calculate the new ranges
            new_x_range = (x_range[0] - (x_range[1] - x_range[0]) * zoom_factor_x,
                        x_range[1] + (x_range[1] - x_range[0]) * zoom_factor_x)
            new_y_range = (y_range[0] - (y_range[1] - y_range[0]) * zoom_factor_y,
                        y_range[1] + (y_range[1] - y_range[0]) * zoom_factor_y)

            # Set new ranges
            plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
            plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

            if SignalPlotWidget.is_linked:
                self.second_graph.plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
                self.second_graph.plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)

    # Generating the function of swapping both signals together (swapping signal,color,title,type)
    def swap_signals(self):
        self.signal1, self.signal2 = self.signal2, self.signal1

        # Swap the text of the title input boxes
        title_text_1 = self.first_graph.title_input.text()
        title_text_2 = self.second_graph.title_input.text()
        self.first_graph.title_input.setText(title_text_2)
        self.second_graph.title_input.setText(title_text_1)
        # self.first_graph, self.second_graph = self.second_graph, self.first_graph

        # Swap the state of the visibility checkboxes
        self.first_graph.show_hide_checkbox1_stat = self.first_graph.show_hide_checkbox.isChecked()
        self.second_graph.show_hide_checkbox2_stat = self.second_graph.show_hide_checkbox.isChecked()
        self.first_graph.show_hide_checkbox.setChecked(self.second_graph.show_hide_checkbox2_stat)
        self.second_graph.show_hide_checkbox.setChecked(self.first_graph.show_hide_checkbox1_stat)

        # Ensure visibility reflects the swapped states
        self.first_graph.toggle_signal(
            Qt.Checked if self.second_graph.show_hide_checkbox2_stat else Qt.Unchecked, self.signal1)
        self.second_graph.toggle_signal(
            Qt.Checked if self.first_graph.show_hide_checkbox1_stat else Qt.Unchecked, self.signal2)

        # Swap the labels of the visibility checkboxes
        self.first_graph.show_hide_checkbox1_labe = self.first_graph.show_hide_checkbox.text()
        self.second_graph.show_hide_checkbox2_labe = self.second_graph.show_hide_checkbox.text()
        self.first_graph.show_hide_checkbox.setText(self.second_graph.show_hide_checkbox2_labe)
        self.second_graph.show_hide_checkbox.setText(self.first_graph.show_hide_checkbox1_labe)

        # Swap the text between speed_label1 and speed_label2
        label1_text = self.first_graph.speed_label.text()
        label2_text = self.second_graph.speed_label.text()
        
        # Swap the text content
        self.first_graph.speed_label.setText(label2_text)
        self.second_graph.speed_label.setText(label1_text)        
        
        self.plot_signals()


    # Generating the function of interpolating(averaging)(gluing) both signals

    def glue_signals(self):
        # self.glued_signal = (self.signal1.data + self.signal2.data) / 2
        self.interpolation_window = InterpolationWindow(
            self.signal1.data, self.signal2.data)  # Generating the Intepolation Window
        self.interpolation_window.show()  # Showing the Interpolation Window

    def show_statistics(self, signal, title, color):
        self.statistics_window = StatisticsWindow(
            signal, title, color)  # Generating the Statistics Window
        self.statistics_window.show()  # Showing the Statistics Window


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = SignalApp()
    ex.resize(900, 700)
    ex.show()
    sys.exit(app.exec_())