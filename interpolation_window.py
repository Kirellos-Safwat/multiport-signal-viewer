import numpy as np
from scipy.interpolate import interp1d
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg
from PyQt5.QtCore import Qt

class InterpolationWindow(QWidget):
    def __init__(self, signal1, signal2):
        super().__init__()
        self.signal1 = signal1
        self.signal2 = signal2
        # Store sub-signals
        self.first_sub_signal = None
        self.second_sub_signal = None
        # To store the starting and ending points of selection
        self.start_pos = None
        self.end_pos = None
        # Track whether the signal is connected
        self.color = 'g'

        # Disable mouse panning when performing selection
        self.mouse_move_connected = False

        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #2e2e2e;") # Dark Grey Color for the Window Background
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.first_signal_plot = self.plot_widget.plot(self.signal1, pen='b')
        # Disable mouse panning when performing selection
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)

        # Create buttons for clearing and gluing
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_graph)
        layout.addWidget(self.reset_button)

        self.glue_button = QPushButton("Glue Signals")
        self.glue_button.clicked.connect(self.glue_signals)
        layout.addWidget(self.glue_button)

        # Create a region item to highlight selected area
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)  # Make sure it's on top of the plot
        self.region.hide()  # Hide until used
        self.plot_widget.addItem(self.region)


    def on_mouse_clicked(self, event):
    # Handle mouse click
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)

            if self.start_pos is None:  # First click
                self.start_pos = mouse_point.x()
                self.region.setRegion([self.start_pos, self.start_pos])  # Initialize region
                self.region.show()

                # Temporarily disable panning and zooming
                self.plot_widget.setMouseEnabled(x=False, y=False)

                # Connect to mouse move event if not already connected
                if not self.mouse_move_connected:
                    self.plot_widget.scene().sigMouseMoved.connect(self.on_mouse_moved)
                    self.mouse_move_connected = True

            else:  # Second click, finalize selection
                self.end_pos = mouse_point.x()
                self.region.setRegion([self.start_pos, self.end_pos])  # Finalize the region

                # Call create_sub_signal with the selected range
                selected_range = (self.start_pos, self.end_pos)
                self.create_sub_signal(selected_range)

                # Reset after selection
                # self.plot_widget.setMouseEnabled(x=True, y=True)
                self.start_pos = None  # Reset start_pos to allow for a new selection

    def on_mouse_moved(self, event):
        # Handle mouse movement
        pos = event
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)

        if self.start_pos is not None:
            self.end_pos = mouse_point.x()
            self.region.setRegion([self.start_pos, self.end_pos])  # Update the region to follow the mouse

    def create_sub_signal(self, selected_range):
        # Get the start and end positions from the selected range
        start, end = selected_range

        # Find the corresponding indices in the signal data (self.signal2)
        start_idx = int(start)
        end_idx = int(end)

        # Store the first or second sub-signal
        if self.first_sub_signal is None:
            # Ensure indices are within valid bounds
            start_idx = max(0, min(start_idx, len(self.signal1) - 1))
            end_idx = max(0, min(end_idx, len(self.signal1) - 1))

            if start_idx > end_idx:  # Ensure the order of the indices is correct
                start_idx, end_idx = end_idx, start_idx

            # Extract the sub-signal
            sub_signal = self.signal1[start_idx:end_idx + 1]
            self.first_sub_signal = sub_signal
            # self.plot_widget.clear()
            self.first_signal_plot = self.plot_widget.removeItem(self.first_signal_plot)
            self.plot_widget.plot(self.signal2, pen='b')
            print("First Sub-Signal Selected")
        else:
                # Ensure indices are within valid bounds
            start_idx = max(0, min(start_idx, len(self.signal2) - 1))
            end_idx = max(0, min(end_idx, len(self.signal2) - 1))

            if start_idx > end_idx:  # Ensure the order of the indices is correct
                start_idx, end_idx = end_idx, start_idx

            # Extract the sub-signal
            sub_signal = self.signal2[start_idx:end_idx + 1]
            self.second_sub_signal = sub_signal
            print("Second Sub-Signal Selected")

        # Hide the region after selection
        self.region.hide()

    def reset_graph(self):
        # Clear the plot for a new signal
        self.plot_widget.clear()
        self.first_sub_signal = None
        self.second_sub_signal = None
        self.start_pos = None
        self.end_pos = None
        self.region.hide()  # Hide the selection region
        print("Graph Cleared")
        self.first_signal_plot = self.plot_widget.plot(self.signal1, pen='b')
        # Re-enable region selection after clearing
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)  # Make sure it's on top of the plot
        self.region.hide()  # Hide until used
        self.plot_widget.addItem(self.region)

    def glue_signals(self):
        # Ensure both sub-signals are selected before gluing
        if self.first_sub_signal is None or self.second_sub_signal is None:
            print("Both signals need to be selected before gluing.")
            return

        # Glue the two sub-signals together by concatenating their x and y values
        sub_y1 = self.first_sub_signal
        sub_y2 = self.second_sub_signal

        # # Plot the glued signal
        gap = -20  # Positive for gap, negative for overlap (in samples)

        if gap > 0:
            glued_signal = np.concatenate([sub_y1, np.zeros(gap), sub_y2])
        else:
            overlap = abs(gap)
            interpolated_part = self.interpolate_signals(sub_y1[-overlap:], sub_y2[:overlap])
            glued_signal = np.concatenate([sub_y1[:-overlap], interpolated_part, sub_y2[overlap:]])

        self.plot_widget.clear()
        self.plot_widget.plot(glued_signal, pen='r')
        print(sub_y1.shape, sub_y2.shape)
        print("Signals Glued and Displayed")
    
    def interpolate_signals(self, signal1, signal2):
        x1 = np.linspace(0, 1, len(signal1))
        x2 = np.linspace(1, 2, len(signal2))
        
        # Combine time points and values for interpolation
        x = np.concatenate([x1, x2])
        y = np.concatenate([signal1, signal2])
        
        # Create the interpolating function (linear interpolation)
        f = interp1d(x, y, kind='nearest')
        
        # Generate new interpolated points
        new_x = np.linspace(0, 2, len(signal1) + len(signal2))
        interpolated_signal = f(new_x)
        
        return interpolated_signal