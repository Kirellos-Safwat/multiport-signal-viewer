from PyQt5 import QtGui, QtWidgets
from pyqtgraph import PlotWidget
from interpolation_statistics_window import InterpolationStatisticsWindow

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

