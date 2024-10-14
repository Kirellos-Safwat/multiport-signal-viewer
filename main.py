import sys
import os
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from utils import Utils
from statistics_window import StatisticsWindow
from interpolation_window import InterpolationWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from signal import Signal
from signal_plot_widget import SignalPlotWidget
from polar import PolarPlotWidget
# from realtime_plot import RealTimePlot
import pandas as pd


class SignalApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_signal = None
        # Initialize the original ranges after setting up the plot
        self.original_x_range = self.first_graph.plot_widget.viewRange()[0]  # Get the initial x range
        self.original_y_range = self.first_graph.plot_widget.viewRange()[1]  # Get the initial y range
        # Initialize the original ranges after setting up the plot
        self.original_x_range = self.second_graph.plot_widget.viewRange()[0]  # Get the initial x range
        self.original_y_range = self.second_graph.plot_widget.viewRange()[1]  # Get the initial y range

        SignalPlotWidget.user_interacting = False  # Flag to allow mouse panning
        # Plotting Siganls with initialized properties
        self.first_graph.plot_signals()

    def initUI(self):
        self.setWindowTitle("Multi-Channel Signal Viewer")  # Window Title
        self.setWindowIcon(QtGui.QIcon("assets\\Pulse.png"))  # Window Icon
        self.setStyleSheet(Utils.window_style_sheet)

        self.tab_widget = QtWidgets.QTabWidget()

        # Add the tabs
        self.tab_widget.addTab(self.main_tab(), "Main")
        self.tab_widget.addTab(self.Polar_tab(), "Polar")
        self.tab_widget.addTab(self.real_time_tab(), "Real-Time")

        # Set the layout of the main window to hold the tab widget
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

             # Connect mouse events for selecting and moving signals
        self.first_graph.plot_widget.scene().sigMouseClicked.connect(self.on_signal_clicked_first_graph)
        self.second_graph.plot_widget.scene().sigMouseClicked.connect(self.on_signal_clicked_second_graph)

    def main_tab(self):
        main_tab = QtWidgets.QWidget()

        # Setting the Main layout (Organizing Structure On Top Of Each Other)
        # Vertical Layout for the positioning of child widgets within a parent widget
        main_layout = QtWidgets.QVBoxLayout(main_tab)

        # Creating signals plotting widgets
        self.first_graph = SignalPlotWidget(name='Graph One', signals=[
            Signal(Utils.generate_square_wave(100), 'b'),
            Signal(Utils.generate_sine_wave(100), 'r')])
        self.second_graph = SignalPlotWidget(name='Graph Two', signals=[Signal(Utils.generate_cosine_wave(100), 'r')])

        # Swap Signals Button
        self.swap_button = Utils.create_button("", self.swap_signals, "swap")

        self.glue_button = Utils.create_button("Glue Signals", self.glue_signals)
        # Link Button
        self.link_button = Utils.create_button("", self.toggle_link, "link")

        main_layout.addLayout(self.first_graph.graph_layout)
        
        # Adding the "horizontal" button layout of signal 1 to the main "vertical" layout
        main_layout.addLayout(self.first_graph.button_layout)
        # button_layout1.addStretch()  # Prevents the buttons from stretching

        main_layout.addLayout(self.second_graph.graph_layout)
        # Adding the "horizontal" button layout of signal 2 to the main "vertical" layout
        main_layout.addLayout(self.second_graph.button_layout)

        # self.main_layout.addWidget(self.link_button)
        buttons_layout_3 = QtWidgets.QHBoxLayout()
        buttons_layout_3.addWidget(self.swap_button)
        buttons_layout_3.addWidget(self.link_button)
        buttons_layout_3.addWidget(self.glue_button)
        main_layout.addLayout(buttons_layout_3)

        # Return the main tab widget
        return main_tab

    def Polar_tab(self):
        polar_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(polar_tab)

        # Create an instance of PolarPlotWidget for the Matplotlib graph
        self.polar_plot_widget = PolarPlotWidget()
        layout.addWidget(self.polar_plot_widget)

        button_layout = QtWidgets.QHBoxLayout()

        self.polar_play_button = Utils.create_button(
            "", self.polar_plot_widget.play_animation, "play")
        button_layout.addWidget(self.polar_play_button)

        self.polar_pause_button = Utils.create_button(
            "", self.polar_plot_widget.pause_animation, "pause")

        button_layout.addWidget(self.polar_pause_button)

        layout.addLayout(button_layout)

        return polar_tab

    def real_time_tab(self):
        # Create an instance of RealTimePlot for the real-time graph
        # self.real_time_plot = RealTimePlot()
        # return self.real_time_plot
        pass


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
                self.second_graph.play_pause_signal()
            elif self.second_graph.is_playing:
                self.first_graph.play_pause_signal()

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
            self.first_graph.link_viewports()
        else:
            self.link_button = Utils.update_button(
                self.link_button, "", "link")
            self.first_graph.unlink_viewports()

        # Ensure consistent signal speeds
        if SignalPlotWidget.is_linked:
            # Check if both timers are running and have the same interval
            if self.first_graph.timer is not None and self.second_graph.timer is not None:
                if self.first_graph.timer.interval() != self.second_graph.timer.interval():
                    self.second_graph.timer.setInterval(
                        self.first_graph.timer.interval())  # Sync intervals


    # Generating the function of swapping both signals together (swapping signal,color,title,type)
    def swap_signals(self):
        
        self.first_graph.signals, self.second_graph.signals = self.second_graph.signals, self.first_graph.signals

        # Swap the text of the title input boxes
        title_text_1 = self.first_graph.title_input.text()
        title_text_2 = self.second_graph.title_input.text()
        self.first_graph.title_input.setText(title_text_2)
        self.second_graph.title_input.setText(title_text_1)
        # self.first_graph, self.second_graph = self.second_graph, self.first_graph

        # Swap the state of the visibility checkboxes
        self.first_graph.show_hide_checkbox1_stat = self.first_graph.show_hide_checkbox.isChecked()
        self.second_graph.show_hide_checkbox2_stat = self.second_graph.show_hide_checkbox.isChecked()
        self.first_graph.show_hide_checkbox.setChecked(
            self.second_graph.show_hide_checkbox2_stat)
        self.second_graph.show_hide_checkbox.setChecked(
            self.first_graph.show_hide_checkbox1_stat)

        # Ensure visibility reflects the swapped states
        self.first_graph.toggle_signal(
            Qt.Checked if self.second_graph.show_hide_checkbox2_stat else Qt.Unchecked)
        self.second_graph.toggle_signal(
            Qt.Checked if self.first_graph.show_hide_checkbox1_stat else Qt.Unchecked)

        # Swap the labels of the visibility checkboxes
        self.first_graph.show_hide_checkbox1_labe = self.first_graph.show_hide_checkbox.text()
        self.second_graph.show_hide_checkbox2_labe = self.second_graph.show_hide_checkbox.text()
        self.first_graph.show_hide_checkbox.setText(
            self.second_graph.show_hide_checkbox2_labe)
        self.second_graph.show_hide_checkbox.setText(
            self.first_graph.show_hide_checkbox1_labe)

        # Swap the text between speed_label1 and speed_label2
        label1_text = self.first_graph.speed_label.text()
        label2_text = self.second_graph.speed_label.text()

        # Swap the text content
        self.first_graph.speed_label.setText(label2_text)
        self.second_graph.speed_label.setText(label1_text)        
        self.first_graph.selected_signal, self.second_graph.selected_signal = self.second_graph.selected_signal, self.first_graph.selected_signal
        self.first_graph.plot_signals()

    # Generating the function of interpolating(averaging)(gluing) both signals
    def glue_signals(self):
        # self.glued_signal = (self.signal1.data + self.second_graph.signal.data) / 2
        if self.first_graph.selected_signal and self.second_graph.selected_signal:
            self.interpolation_window = InterpolationWindow(
                self.first_graph.selected_signal, self.second_graph.selected_signal)  # Generating the Intepolation Window
            self.interpolation_window.show()  # Showing the Interpolation Window
        else:
            Utils.show_error_message("Each graph must have a selected signal")
    def on_signal_clicked_first_graph(self, event):
        self.on_signal_clicked(event, self.first_graph, self.second_graph)

    def on_signal_clicked_second_graph(self, event):
        self.on_signal_clicked(event, self.second_graph, self.first_graph)

    def on_signal_clicked(self, event, source_graph, target_graph):
        pos = event.scenePos()  # Get the mouse position in scene coordinates
        mouse_point = source_graph.plot_widget.plotItem.vb.mapSceneToView(pos)

        x_mouse = mouse_point.x()
        y_mouse = mouse_point.y()

        closest_signal = None
        min_distance = float('inf')  # Initialize with infinity for comparison

        # Loop through signals to find the one closest to the click
        for signal in source_graph.signals:
            x_data = np.arange(len(signal.data))
            y_data = signal.data

            index = (np.abs(x_data - x_mouse)).argmin()  # Find closest x index
            distance = np.sqrt((x_mouse - x_data[index])**2 + (y_mouse - y_data[index])**2)

            if distance < min_distance:
                min_distance = distance
                closest_signal = signal

        if closest_signal:
            # Store the selected signal and source graph
            self.selected_signal = closest_signal
            # self.source_graph.selected_signal = self.selected_signal
            self.source_graph = source_graph

        self.grabMouse()  # Grab the mouse to track where the release happens

    def mouseReleaseEvent(self, event):
        # Check if the mouse release occurred on a different graph
        if self.selected_signal and self.source_graph:
            release_pos = event.pos()  # Get the release position in the widget
            target_graph = None

            # Determine if the mouse release is on the second graph
            if self.second_graph.plot_widget.geometry().contains(release_pos):
                target_graph = self.second_graph
            elif self.first_graph.plot_widget.geometry().contains(release_pos):
                target_graph = self.first_graph

            # Move the signal from the source graph to the target graph
            if target_graph and target_graph != self.source_graph:
                if len(self.source_graph.signals) > 1:
                    self.source_graph.signals.remove(self.selected_signal)
                    target_graph.signals.append(self.selected_signal)
                    # target_graph.selected_signal = self.selected_signal
                    target_graph.update_graph()
                    # Re-plot both graphs after moving the signal
                    self.source_graph.update_graph()
                    # target_graph.plot_signals()
                else:
                    print("Empty graph")
            # Clear the selected signal and source graph
            self.selected_signal = None
            self.source_graph = None

        self.releaseMouse()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = SignalApp()
    ex.resize(900, 700)
    ex.show()
    sys.exit(app.exec_())
