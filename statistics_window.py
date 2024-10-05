import numpy as np
from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget

class StatisticsWindow(QtWidgets.QWidget):
    def __init__(self, signal, title, color):
        super().__init__()
        self.signal = signal
        self.title = title
        self.color = color
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")
        
        layout = QtWidgets.QVBoxLayout()
        
        # Plot for Signal
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('black')
        self.plot_widget.plot(self.signal, pen=self.color)
        self.plot_widget.setTitle(self.title)
        self.plot_widget.setYRange(0, 1)
        layout.addWidget(self.plot_widget)

        # Statistics buttons
        buttons = [
            ("Calculate Mean", self.calculate_mean),
            ("Calculate Std Dev", self.calculate_std),
            ("Calculate Duration", self.calculate_duration),
            ("Calculate Min", self.calculate_min),
            ("Calculate Max", self.calculate_max),
            ("Calculate Sampling Rate", self.calculate_sampling_rate)
        ]

        for text, slot in buttons:
            layout.addWidget(self.create_button(text, slot))

        self.result_label = QtWidgets.QLabel("")
        layout.addWidget(self.result_label)

        # Back button
        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.back_button.clicked.connect(self.close)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def create_button(self, text, slot):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        button.clicked.connect(slot)
        return button

    def calculate_mean(self):
        mean_value = np.mean(self.signal)
        self.result_label.setText(f"Mean: {mean_value:.2f}")

    def calculate_std(self):
        std_value = np.std(self.signal)
        self.result_label.setText(f"Standard Deviation: {std_value:.2f}")

    def calculate_duration(self):
        duration = len(self.signal)  # Assuming 1 sample = 1 unit time
        self.result_label.setText(f"Duration: {duration} units")

    def calculate_min(self):
        min_value = np.min(self.signal)
        self.result_label.setText(f"Min: {min_value:.2f}")

    def calculate_max(self):
        max_value = np.max(self.signal)
        self.result_label.setText(f"Max: {max_value:.2f}")

    def calculate_sampling_rate(self):
        sampling_rate = 100  # Assuming fixed sampling rate for this example
        self.result_label.setText(f"Sampling Rate: {sampling_rate} Hz")
