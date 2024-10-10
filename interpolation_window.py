from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget
from interpolation_statistics_window import InterpolationStatisticsWindow
from fpdf import FPDF
import numpy as np
from pyqtgraph.exporters import ImageExporter
import pyqtgraph as pg
import os




class InterpolationWindow(QtWidgets.QWidget):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.color = 'g'
        self.snapshot_count = 0  # Initialize snapshot count here
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Interpolated Signal") # Window Title
        self.setWindowIcon(QtGui.QIcon("assets\\Pulse.png")) # Window Icon
        self.setStyleSheet("background-color: #042630;") # Window Background Color

        layout = QtWidgets.QVBoxLayout() # Setting a vertical layout for the window components

        # Setting the Plotting Widget the Interpolated Signal
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('#001414')
        self.plot_widget.plot(self.signal, pen=self.color)
        self.plot_widget.setTitle("Interpolated Signal")
        self.plot_widget.setYRange(-1, 1)
        # Adding the Plotting Widget to the Vertical Window Layout
        layout.addWidget(self.plot_widget)


        button_layout = self.create_button_layout(
            self.change_color, 
            self.zoom_in, 
            self.zoom_out, 
            self.show_statistics,
            self.take_snapshot,
            self.export_report
        )
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_button_layout(self, color_change, zoom_in, zoom_out, statistics, take_snapshot, export_report):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_button(
            
            f"", color_change, "color"))
        button_layout.addWidget(self.create_button(
            f"", zoom_in, "zoom_in"))
        button_layout.addWidget(self.create_button(
            f"", zoom_out, "zoom_out"))
        button_layout.addWidget(self.create_button(
            f"", statistics, "statistics"))
        button_layout.addWidget(self.create_button(
            f"", take_snapshot, "take_snapshot"))
        button_layout.addWidget(self.create_button(
            f"", export_report, "export_report"))
        return button_layout
    
    # A method for creating each button as a Pushbutton from QT and setting the method to be called when the button is pressed:

    def create_button(self, text, method, icon_name=''):
        button = QtWidgets.QPushButton(text)

        # Adjust the button to be a perfect circle
        button.setStyleSheet("""
            QPushButton {
                background-color: #adb4b4;
                color: white;
                font-size: 14px;
                padding: 10;
                border-radius: 25px;  /* Makes the button a perfect circle */
                width: 30px;  /* Set the width to 50px */
                height: 30px;  /* Set the height to 50px */
                border: 2px solid #012121;
            }
            QPushButton:hover {
                background-color: #4c7273;
                border: 2px solid white;
            }
            QPushButton:pressed {
                background-color: #86b9b0;
            }
        """)

        # Optional icon for the button
        if icon_name:
            icon = QtGui.QIcon('assets\\button_icons\\' + icon_name + '.png')
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(55,55 ))  # Enlarge the icon size

        
        # Connect the button to the method
        button.clicked.connect(method)
        
        return button


    def take_snapshot(self):
        self.snapshot_count += 1  # Increment the snapshot counter
        img_path = f'snapshot{self.snapshot_count}.png'  # Create a filename for the snapshot
        exporter = ImageExporter(self.plot_widget.getPlotItem())
        exporter.export(img_path)  # Save the current plot as an image
        QtWidgets.QMessageBox.information(self, "Snapshot Saved", f"Snapshot saved as '{img_path}'.")

    # Generating the function of color changing in general
    def change_color(self, signal_index):
        color = QtWidgets.QColorDialog.getColor()
        if signal_index == 1:
            self.color1 = color.name()
        else:
            self.color2 = color.name()
        self.plot_signals()

    # Generating zoom in/zoom out functions of both signals:
    def zoom_in(self, plot_widget):
        # Calculate the new ranges based on the original ranges
        x_range = plot_widget.viewRange()[0]
        y_range = plot_widget.viewRange()[1]
        new_x_range = (x_range[0] + (self.original_x_range[1] - self.original_x_range[0])
                       * 0.1, x_range[1] - (self.original_x_range[1] - self.original_x_range[0]) * 0.1)
        new_y_range = (y_range[0] + (self.original_y_range[1] - self.original_y_range[0])
                       * 0.1, y_range[1] - (self.original_y_range[1] - self.original_y_range[0]) * 0.1)
        plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
        plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
        # If linked, apply to second plot
        if self.linked:
            self.plot_widget2.setXRange(
                new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget2.setYRange(
                new_y_range[0], new_y_range[1], padding=0)

            # Update original ranges after zooming
        self.original_x_range = new_x_range
        self.original_y_range = new_y_range

    def zoom_out(self, plot_widget):
        # Calculate the new ranges based on the original ranges
        x_range = plot_widget.viewRange()[0]
        y_range = plot_widget.viewRange()[1]
        new_x_range = (x_range[0] - (self.original_x_range[1] - self.original_x_range[0])
                       * 0.1, x_range[1] + (self.original_x_range[1] - self.original_x_range[0]) * 0.1)
        new_y_range = (y_range[0] - (self.original_y_range[1] - self.original_y_range[0])
                       * 0.1, y_range[1] + (self.original_y_range[1] - self.original_y_range[0]) * 0.1)
        plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
        plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
        # If linked, apply to second plot
        if self.linked:
            self.plot_widget2.setXRange(
                new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget2.setYRange(
                new_y_range[0], new_y_range[1], padding=0)

        # Update original ranges after zooming
        self.original_x_range = new_x_range
        self.original_y_range = new_y_range


    def show_statistics(self):
        self.statistics_window = InterpolationStatisticsWindow(self.signal, self.color)
        self.statistics_window.show()

    def update_plot(self):
        self.plot_widget.clear()
        self.plot_widget.plot(self.signal, pen=self.color)
        self.plot_widget.setTitle("Interpolated Signal")
        self.plot_widget.setYRange(0, 1)


    def calculate_statistics(self):
        mean_val = np.mean(self.signal)
        std_val = np.std(self.signal)
        min_val = np.min(self.signal)
        max_val = np.max(self.signal)
        duration = len(self.signal)  # Assuming duration is the number of samples
        return mean_val, std_val, min_val, max_val, duration


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