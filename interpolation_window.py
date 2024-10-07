from PyQt5 import QtGui, QtWidgets
from pyqtgraph import PlotWidget
from interpolation_statistics_window import InterpolationStatisticsWindow
from fpdf import FPDF
import numpy as np
from pyqtgraph.exporters import ImageExporter
import pyqtgraph as pg



class InterpolationWindow(QtWidgets.QWidget):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.color = 'g'
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Interpolated Signal") # Window Title
        self.setWindowIcon(QtGui.QIcon("C:\\Users\\LOQ\\Downloads\\Pulse.png")) # Window Icon
        self.setStyleSheet("background-color: #2e2e2e;") # Window Background Color

        layout = QtWidgets.QVBoxLayout() # Setting a vertical layout for the window components

        # Setting the Plotting Widget the Interpolated Signal
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('black')
        self.plot_widget.plot(self.signal, pen=self.color)
        self.plot_widget.setTitle("Interpolated Signal")
        self.plot_widget.setYRange(-1, 1)
        # Adding the Plotting Widget to the Vertical Window Layout
        layout.addWidget(self.plot_widget)

        # Generating Control buttons for the Interpolated Signal
        button_layout = QtWidgets.QHBoxLayout() # Setting buttons in a Horizontal Layout next to each other
        button_layout.addWidget(self.create_button("Change Color", self.change_color))
        button_layout.addWidget(self.create_button("Zoom In", self.zoom_in))
        button_layout.addWidget(self.create_button("Zoom Out", self.zoom_out))
        button_layout.addWidget(self.create_button("Statistics", self.show_statistics))
        button_layout.addWidget(self.create_button("Export Report", self.export_report))  # New export button
        # Adding the Horizontal buttons layout to the Vertical Window Layout
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_button(self, text, slot):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        button.clicked.connect(slot)
        return button

    def change_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.update_plot()

    def zoom_in(self):
        x_range = self.plot_widget.viewRange()[0]
        self.plot_widget.setXRange(x_range[0] * 0.8, x_range[1] * 0.8)

    def zoom_out(self):
        x_range = self.plot_widget.viewRange()[0]
        self.plot_widget.setXRange(x_range[0] * 1.2, x_range[1] * 1.2)

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
        
        # Title
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 10, 'Glue Operation Report', 0, 1, 'C')
        pdf.ln(7)  # Add space after title

        # Statistics title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'Statistical Summary', 0, 1, 'C')
        pdf.ln(4)  # Add space after section title

        # Center the table on the page
        pdf.set_x((pdf.w - 160) / 2)  # Center the table (80 + 80 = 160 total width)

        # Statistics table header
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(80, 10, 'Statistic', 1, 0, 'C')
        pdf.cell(80, 10, 'Value', 1, 1, 'C')  # Header

        pdf.set_font("Arial", '', 12)
        stats = [
            ('Mean', f'{mean:.2f}'),
            ('Standard Deviation', f'{std:.2f}'),
            ('Minimum Value', f'{min_val:.2f}'),
            ('Maximum Value', f'{max_val:.2f}'),
            ('Duration', str(duration))
        ]
        
        # Center the table on the page
        for label, value in stats:
            pdf.set_x((pdf.w - 160) / 2)  # Center the table (80 + 80 = 160 total width)
            pdf.cell(80, 10, label, 1, 0, 'C')  # Center the label
            pdf.cell(80, 10, value, 1, 1, 'C')  # Center the value

        pdf.ln(10)  # Add space before the caption for the image

        # Save the plot as an image
        img_path = 'interpolated_signal_snapshot.png'
        exporter = ImageExporter(self.plot_widget.getPlotItem())
        exporter.export(img_path)  # Export the plot widget to an image file

        # Center the image on the page and reduce its size
        pdf.image(img_path, x=(pdf.w - 150) / 2, y=pdf.get_y(), w=150)  # Center the image
        pdf.ln(115)  # Add space after caption


        # Caption for the image
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, 'Figure 1: Interpolated Signal Snapshot', 0, 1, 'C')  # Center the caption below the image
        pdf.ln(3)  # Add space after caption

        # Footer
        pdf.set_y(-35)  # Position at 1.5 cm from bottom
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')

        # Save the PDF report
        pdf.output('glue_report.pdf')  # Save PDF report

        # Notify user
        QtWidgets.QMessageBox.information(self, "Report Exported", "The report has been successfully exported as 'glue_report.pdf'.")