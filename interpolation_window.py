import numpy as np
from scipy.interpolate import interp1d
import sys
import os
from pyqtgraph.exporters import ImageExporter
from fpdf import FPDF
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel, QHBoxLayout
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from interpolation_statistics_window import InterpolationStatisticsWindow
from utils import Utils

class InterpolationWindow(QWidget):
    def __init__(self, signal1, signal2):
        super().__init__()
        self.signal1 = signal1
        self.signal2 = signal2
        # Initialize snapshot count here
        self.snapshot_count = 0 
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

        self.gap = 0
        self.glued_signal = None
        self.glued_signal_color = 'r'
        self.interpolation_order = 'linear'

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Glue Signals") # Window Title
        self.setWindowIcon(QtGui.QIcon("assets\\Pulse.png")) # Window Icon
        self.setStyleSheet("background-color: #042630;") # Window Background Color
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#001414')
        self.plot_widget.setTitle("First Signal")
        layout.addWidget(self.plot_widget)
        self.first_signal_plot = self.plot_widget.plot(self.signal1, pen='b')
        # Disable mouse panning when performing selection
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(Utils.create_button(f"Reset", self.reset_graph, "Reset"))

        self.change_color_button = Utils.create_button(f"", self.change_color, "color", set_enabled=False)
        button_layout.addWidget(self.change_color_button)

        self.show_statistics_button = Utils.create_button(f"", self.show_statistics, "statistics", set_enabled=False)
        button_layout.addWidget(self.show_statistics_button)

        button_layout.addWidget(Utils.create_button(f"", self.take_snapshot, "take_snapshot"))

        self.export_report_button =Utils.create_button(f"", self.export_report, "export_report", set_enabled=False)
        button_layout.addWidget(self.export_report_button)
        layout.addLayout(button_layout)
        # Slider for Signal 1
        self.gap_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.gap_slider.setMinimum(-80)  
        self.gap_slider.setMaximum(80)  
        self.gap_slider.setValue(0)    
        self.gap_slider.setTickInterval(5)  
        self.gap_slider.valueChanged.connect(self.update_gap)
        self.gap_slider.setStyleSheet(Utils.slider_style_sheet)
        self.gap_slider.setEnabled(False)


        # Create a QLabel to display the selected item
        order_layout = QHBoxLayout()
        self.order_label = QLabel("Select Interpolation Order: ", self)
        self.order_label.setStyleSheet(Utils.label_style_sheet)
        order_layout.addWidget(self.order_label)
        # Create a QComboBox (dropdown list)
        self.select_order_comboBox = QComboBox(self)
        # Add items to the combo box
        self.select_order_comboBox.addItems(["Linear", "Zero", "Quadratic", "Cubic"])
        # Connect the signal to the slot (function)
        self.select_order_comboBox.currentTextChanged.connect(self.on_select_order)
        self.select_order_comboBox.setStyleSheet(Utils.comboBox_style_sheet)
        # Add the combo box to the layout
        order_layout.addWidget(self.select_order_comboBox)
        layout.addLayout(order_layout)
        layout.addWidget(self.gap_slider)

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
                self.plot_widget.setMouseEnabled(x=True, y=True)
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
            self.plot_widget.setTitle("Second Signal")
            response = Utils.show_info_message("First Sub-Signal Selected", True)
            if response == "reset":
                self.reset_graph()
        else:
                # Ensure indices are within valid bounds
            start_idx = max(0, min(start_idx, len(self.signal2) - 1))
            end_idx = max(0, min(end_idx, len(self.signal2) - 1))

            if start_idx > end_idx:  # Ensure the order of the indices is correct
                start_idx, end_idx = end_idx, start_idx

            # Extract the sub-signal
            sub_signal = self.signal2[start_idx:end_idx + 1]
            self.second_sub_signal = sub_signal
            response = Utils.show_info_message("Second Sub-Signal Selected", True)
            if response == "continue":
                self.glue_signals()
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
        self.first_signal_plot = self.plot_widget.plot(self.signal1, pen='b')
        self.plot_widget.setTitle("First Signal")
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.gap_slider.setEnabled(False)
        self.change_color_button.setEnabled(False)
        self.show_statistics_button.setEnabled(False)
        self.export_report_button.setEnabled(False)
        # Re-enable region selection after clearing
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)  # Make sure it's on top of the plot
        self.region.hide()  # Hide until used
        self.plot_widget.addItem(self.region)

    def glue_signals(self, gap = 0):
        # Ensure both sub-signals are selected before gluing
        if self.first_sub_signal is None or self.second_sub_signal is None:
            Utils.show_warning_message("Both signals need to be selected before gluing.")
            return

        # Glue the two sub-signals together by concatenating their x and y values
        sub_y1 = self.first_sub_signal
        sub_y2 = self.second_sub_signal

        # Plot the glued signal
        # Positive for gap, negative for overlap (in samples)
        overlap = abs(gap)
        interpolated_part, new_x = self.interpolate_signals(sub_y1[-overlap:], sub_y2[:overlap], gap)
        self.glued_signal = np.concatenate([sub_y1[:-overlap], interpolated_part, sub_y2[overlap:]])

        self.plot_widget.clear()
        self.plot_widget.plot(self.glued_signal, pen=self.glued_signal_color)
        self.gap_slider.setEnabled(True)
        self.change_color_button.setEnabled(True)
        self.show_statistics_button.setEnabled(True)
        self.export_report_button.setEnabled(True)
        self.plot_widget.setTitle("Glued Signal")
    
    def interpolate_signals(self, sub_y1, sub_y2, gap, interpolation_order = 'linear'):
        interpolation_order = self.interpolation_order
        # Determine overlap or gap
        if gap < 0:  # Overlap case
            overlap = abs(gap)
            # Ensure overlap does not exceed the length of the shorter signal
            overlap = min(overlap, len(sub_y1), len(sub_y2))
            # Slice overlapping regions
            sub_y1_overlap = sub_y1[-overlap:]
            sub_y2_overlap = sub_y2[:overlap]
        else:  # Gap case (positive or zero)
            overlap = 0
            sub_y1_overlap = sub_y1
            sub_y2_overlap = sub_y2

        # Create a combined x-axis for the signals with a gap (if applicable)
        x1 = np.linspace(0, len(sub_y1_overlap) - 1, len(sub_y1_overlap))
        x2 = np.linspace(len(sub_y1_overlap) + gap, len(sub_y1_overlap) + gap + len(sub_y2_overlap) - 1, len(sub_y2_overlap))

        # Combine the x-axis
        x_combined = np.concatenate([x1, x2])
        y_combined = np.concatenate([sub_y1_overlap, sub_y2_overlap])

        # Define the interpolation function
        # f = interp1d(x_combined, y_combined, kind=interpolation_order, fill_value="extrapolate")
        f = interp1d(x_combined, y_combined, kind=interpolation_order, fill_value=0)

        # Create a new x-axis for interpolation (dense for smooth result)
        new_x = np.linspace(min(x_combined), max(x_combined), num=100)

        # Interpolate the signal
        interpolated_signal = f(new_x)

        return interpolated_signal, new_x

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.gap -= 5
            self.glue_signals(self.gap)
            # print("Gap: ", self.gap)
        elif event.key() == Qt.Key_Right:
            self.gap += 5
            self.glue_signals(self.gap)
            # print("Gap: ", self.gap)

    def update_gap(self):
        self.glue_signals(self.gap_slider.value())

    def on_select_order(self, text):
        self.interpolation_order = str(text).lower()

    def show_statistics(self):
        self.statistics_window = InterpolationStatisticsWindow(self.glued_signal, self.glued_signal_color)
        self.statistics_window.show()

    def update_plot(self):
        self.plot_widget.clear()
        self.plot_widget.plot(self.glued_signal, pen=self.color)
        self.plot_widget.setTitle("Interpolated Signal")
        self.plot_widget.setYRange(0, 1)


    def calculate_statistics(self):
        mean_val = np.mean(self.glued_signal)
        std_val = np.std(self.glued_signal)
        min_val = np.min(self.glued_signal)
        max_val = np.max(self.glued_signal)
        duration = len(self.glued_signal)  # Assuming duration is the number of samples
        return mean_val, std_val, min_val, max_val, duration

    def change_color(self, signal_index):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.glued_signal_color = color.name()
            self.plot_widget.clear()
            self.plot_widget.plot(self.glued_signal, pen=self.glued_signal_color)
            self.plot_widget.setTitle("Glued Signal")

    def take_snapshot(self):
        self.snapshot_count += 1  # Increment the snapshot counter
        img_path = f'snapshot{self.snapshot_count}.png'  # Create a filename for the snapshot
        exporter = ImageExporter(self.plot_widget.getPlotItem())
        exporter.export(img_path)  # Save the current plot as an image
        QtWidgets.QMessageBox.information(self, "Snapshot Saved", f"Snapshot saved as '{img_path}'.")

    def export_report(self):
        # Calculate statistics
        mean, std, min_val, max_val, duration = self.calculate_statistics()
        
        # Prepare PDF report
        pdf = FPDF()
        pdf.add_page()

        pdf.ln(5)  # Add space after title

        # Title
        pdf.set_font("Times", 'B', 28)
        pdf.set_text_color(0,0,0)  # Dark blue color
        pdf.cell(0, 10, 'Glued Signal Report', 0, 1, 'C')
        pdf.ln(10)  # Add space after title

        # Statistics title
        pdf.set_font("Times", 'B', 20)
        pdf.set_text_color(0, 51, 102)  # Dark blue color
        pdf.cell(0, 10, 'Statistical Summary', 0, 1, 'C')
        pdf.ln(5)  # Add space after section title

        # Center the table on the page
        pdf.set_x((pdf.w - 160) / 2)  # Center the table (80 + 80 = 160 total width)

        # Statistics table header
        pdf.set_font("Times", 'B', 16)
        pdf.set_fill_color(220, 220, 220)  # Light gray background for header
        pdf.cell(80, 10, 'Statistic', 1, 0, 'C', 1)
        pdf.cell(80, 10, 'Value', 1, 1, 'C', 1)  # Header

        pdf.set_font("Times", '', 14)
        pdf.set_text_color(0, 0, 0)  # Black color
        stats = [
            ('Mean', f'{mean:.2f}'),
            ('Standard Deviation', f'{std:.2f}'),
            ('Minimum Value', f'{min_val:.2f}'),
            ('Maximum Value', f'{max_val:.2f}'),
            ('Duration', str(duration))
        ]
        
        for label, value in stats:
            pdf.set_x((pdf.w - 160) / 2)  # Center the table
            pdf.cell(80, 10, label, 1, 0, 'C')  # Center the label
            pdf.cell(80, 10, value, 1, 1, 'C')  # Center the value



        # Add footer for the first page
        pdf.set_y(-35)  # Position at 3.5 cm from bottom
        pdf.set_font("Times", 'I', 10)
        pdf.set_text_color(128, 128, 128)  # Gray color for footer
        pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')  # Center the page number

        # Include all snapshots in the PDF, each on a new page
        for i in range(1, self.snapshot_count + 1):
            img_path = f'snapshot{i}.png'
            if os.path.exists(img_path):  # Check if the snapshot exists
                pdf.add_page()  # Add a new page for each snapshot

                # Title for the figure
                pdf.set_font("Times", 'B', 18)
                pdf.set_text_color(0, 51, 102)  # Dark blue color
                pdf.cell(0, 10, f'Snapshot {i}:', 0, 1, 'C')  # Title above the image
                pdf.ln(5)  # Add space between title and image

                # Add the image to the PDF
                pdf.image(img_path, x=(pdf.w - 150) / 2, y=20, w=150)  # Center the image
                pdf.ln(10)  # Add space after the image
                
                # Footer with page number
                pdf.set_y(-35)  # Position at 3.5 cm from bottom
                pdf.set_font("Times", 'I', 10)
                pdf.set_text_color(128, 128, 128)  # Gray color for footer
                pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')  # Center the page number

        # Save the PDF report
        pdf.output('glue_report.pdf')  # Save PDF report

        # Notify user
        QtWidgets.QMessageBox.information(self, "Report Exported", "The report has been successfully exported as 'glue_report.pdf'.")