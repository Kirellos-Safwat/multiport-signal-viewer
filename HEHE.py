import sys
import numpy as np
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget

class SignalApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Initializing Signals' colors, ranges, types and titles
        self.color1 = 'b'
        self.color2 = 'r'
        self.signal1 = self.generate_square_wave(100)
        self.signal2 = self.generate_cosine_wave(100)
        self.type1 = 'square'
        self.type2 = 'cosine'
        self.title1 = "Square Wave Signal"
        self.title2 = "Cosine Wave Signal"
        
        # Plotting Siganls with initialized properties
        self.plot_signals()

        # Initializing Timers to refresh the visuals of the signals based on them for a dynamic view
        self.timer1 = None
        self.timer2 = None

        # Boolean Flags to tell whether the signal is playing or not
        self.playing1 = False
        self.playing2 = False

    def initUI(self):
        self.setWindowTitle("Multi-Channel Signal Viewer") # Window Title
        self.setWindowIcon(QtGui.QIcon("C:\\Users\\LOQ\\Downloads\\Pulse.png")) # Window Icon
        self.setStyleSheet("background-color: #2e2e2e;") # Dark Grey Color for the Window Background
        
        # Setting the Main layout (Organizing Structure On Top Of Each Other)
        self.main_layout = QtWidgets.QVBoxLayout() # Vertical Layout for the positioning of child widgets within a parent widget
        self.setLayout(self.main_layout)

        # Creating signals plotting widgets
        self.plot_widget1 = PlotWidget()
        self.plot_widget2 = PlotWidget()
        
        self.plot_widget1.setBackground('black')
        self.plot_widget2.setBackground('black')
        
        # Adding the two plotting widgets to the main "vertical" layout 
        self.main_layout.addWidget(self.plot_widget1)
        self.main_layout.addWidget(self.plot_widget2)


        # Setting the Control buttons for Signal 1:
        # Creating "horizontal" layout for the buttons of signal 1:
        button_layout1 = self.create_button_layout(
            "Signal 1", self.play_signal1, self.pause_signal1, self.stop_signal1,
            self.change_color1, self.zoom_in1, self.zoom_out1, self.show_signal1_statistics  
        )
        # Adding the "horizontal" button layout of signal 1 to the main "vertical" layout 
        self.main_layout.addLayout(button_layout1)

        # Setting the Control buttons for Signal 2:
        # Creating "horizontal" layout for the buttons of signal 2:
        button_layout2 = self.create_button_layout(
            "Signal 2", self.play_signal2, self.pause_signal2, self.stop_signal2,
            self.change_color2, self.zoom_in2, self.zoom_out2, self.show_signal2_statistics 
        )
        # Adding the "horizontal" button layout of signal 2 to the main "vertical" layout 
        self.main_layout.addLayout(button_layout2)

        # Swap Signals Button
        self.swap_button = QtWidgets.QPushButton("Swap Signals")
        self.swap_button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.swap_button.clicked.connect(self.swap_signals)
        self.main_layout.addWidget(self.swap_button)

        # Interpolate Signals Button
        self.interpolate_button = QtWidgets.QPushButton("Interpolate Signals")
        self.interpolate_button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.interpolate_button.clicked.connect(self.interpolate_signals)
        self.main_layout.addWidget(self.interpolate_button)


    # A method for Setting the horizontal layout of the buttons according to the signal_name
    def create_button_layout(self, signal_name, play, pause, stop, color_change, zoom_in, zoom_out, statistics):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_button(f"Play {signal_name}", play))
        button_layout.addWidget(self.create_button(f"Pause {signal_name}", pause))
        button_layout.addWidget(self.create_button(f"Stop {signal_name}", stop))
        button_layout.addWidget(self.create_button(f"Change Color {signal_name}", color_change))
        button_layout.addWidget(self.create_button(f"Zoom In {signal_name}", zoom_in))
        button_layout.addWidget(self.create_button(f"Zoom Out {signal_name}", zoom_out))
        button_layout.addWidget(self.create_button(f"Statistics {signal_name}", statistics))
        return button_layout


    # A method for creating each button as a Pushbutton from QT and setting the method to be called when the button is pressed:
    def create_button(self, text, method):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        button.clicked.connect(method)
        return button


    # Generating the square wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=1 when t<0.5 and f=0 when t>0.5
    def generate_square_wave(self, points):
        t = np.linspace(0, 1, points)
        return np.where(t < 0.5, 1, 0)
    
    # Generating the cosine wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=cos(2*pi*F*t) for a periodic function of freq = 5Hz
    def generate_cosine_wave(self, points):
        t = np.linspace(0, 1, points)
        return (np.cos(2 * np.pi * 5 * t))  

    # Generating the function of plotting the signals, giving them titles, and setting their Y-range from -1 to 1
    def plot_signals(self):
        self.plot_widget1.clear()  #The clear method is used to clear the frame each time before making the new frame!
        self.plot_widget1.plot(self.signal1, pen=self.color1)
        self.plot_widget1.setTitle(self.title1)
        self.plot_widget1.setYRange(-1, 1)

        self.plot_widget2.clear() #The clear method is used to clear the frame each time before making the new frame!
        self.plot_widget2.plot(self.signal2, pen=self.color2)
        self.plot_widget2.setTitle(self.title2)
        self.plot_widget2.setYRange(-1, 1)

    # Generating the function of playing signal 1
    def play_signal1(self):
        if not self.playing1:
            self.playing1 = True
            if self.timer1 is None:
                self.timer1 = pg.QtCore.QTimer() # Creates a timer where the plot would be updated with new data, allowing real-time visualization of signal.
                self.timer1.timeout.connect(self.update_plot1)
                self.timer1.start(100) #Frequent updates every 100ms

    # Generating the function of pausing signal 1
    def pause_signal1(self):
        if self.playing1:
            self.playing1 = False

    # Generating the function of stopping/resetting signal 1
    def stop_signal1(self):
        if self.timer1 is not None:
            self.timer1.stop()
            self.timer1 = None
        self.playing1 = False
        #To solve the problem of stopping after swapping:
        if self.type1 == 'cosine':
            self.signal1 = self.generate_cosine_wave(100)
        else:
            self.signal1 = self.generate_square_wave(100)
        self.plot_signals()

    # Generating the function of playing signal 2
    def play_signal2(self):
        if not self.playing2:
            self.playing2 = True
            if self.timer2 is None:
                self.timer2 = pg.QtCore.QTimer()
                self.timer2.timeout.connect(self.update_plot2)
                self.timer2.start(100)

    # Generating the function of pausing signal 2
    def pause_signal2(self):
        if self.playing2:
            self.playing2 = False

    # Generating the function of stopping/resetting signal 2
    def stop_signal2(self):
        if self.timer2 is not None:
            self.timer2.stop()
            self.timer2 = None
        self.playing2 = False
        #To solve the problem of stopping after swapping:
        if self.type2 == 'cosine':
            self.signal2 = self.generate_cosine_wave(100) 
        else:
            self.signal2 = self.generate_square_wave(100)
        self.plot_signals()

    # Generating the function of updating the plotting of signal 1
    def update_plot1(self):
        if self.playing1:
            self.signal1 = np.roll(self.signal1, -1) # This shifts "signal 1" one position to the left simulating the effect of a moving signal
            self.plot_signals()

    # Generating the function of updating the plotting of signal 2
    def update_plot2(self):
        if self.playing2:
            self.signal2 = np.roll(self.signal2, -1) # This shifts "signal 2" one position to the left simulating the effect of a moving signal
            self.plot_signals()

    # Generating the function of changing the color of signal 1
    def change_color1(self):
        self.change_color(signal_index=1)

    # Generating the function of changing the color of signal 2
    def change_color2(self):
        self.change_color(signal_index=2)

    # Generating the function of color changing in general
    def change_color(self, signal_index):
        color = QtWidgets.QColorDialog.getColor()
        if signal_index == 1:
            self.color1 = color.name()
        else:
            self.color2 = color.name()
        self.plot_signals()

    # Generating zoom in/zoom out functions of both signals:
    def zoom_in1(self):
        self.zoom_in(plot_widget=self.plot_widget1)

    def zoom_out1(self):
        self.zoom_out(plot_widget=self.plot_widget1)

    def zoom_in2(self):
        self.zoom_in(plot_widget=self.plot_widget2)

    def zoom_out2(self):
        self.zoom_out(plot_widget=self.plot_widget2)

    def zoom_in(self, plot_widget):
        x_range = plot_widget.viewRange()[0] # Gets the current x-axis range
        plot_widget.setXRange(x_range[0] * 0.8, x_range[1] * 0.8) # Sets a new x-axis range, reducing the range by 20%

    def zoom_out(self, plot_widget):
        x_range = plot_widget.viewRange()[0] # Gets the current x-axis range
        plot_widget.setXRange(x_range[0] * 1.2, x_range[1] * 1.2) # Sets a new x-axis range, increasing the range by 20%

    # Generating the function of swapping both signals together (swapping signal,color,title,type)
    def swap_signals(self):
        self.signal1, self.signal2 = self.signal2, self.signal1
        self.color1, self.color2 = self.color2, self.color1
        self.title1, self.title2 = self.title2, self.title1
        self.type1, self.type2 = self.type2,self.type1
        self.plot_signals()

    # Generating the function of interpolating(averaging)(gluing) both signals
    def interpolate_signals(self):
        self.interpolated_signal = (self.signal1 + self.signal2) / 2
        self.interpolation_window = InterpolationWindow(self.interpolated_signal) # Generating the Intepolation Window
        self.interpolation_window.show() # Showing the Interpolation Window

    def show_statistics(self, signal, title, color):
        self.statistics_window = StatisticsWindow(signal, title, color) # Generating the Statistics Window
        self.statistics_window.show() # Showing the Statistics Window

    # Showing Statistics window of signal 1
    def show_signal1_statistics(self):
        self.show_statistics(self.signal1, self.title1, self.color1)    
    
    # Showing Statistics window of signal 2
    def show_signal2_statistics(self):
        self.show_statistics(self.signal2, self.title2, self.color2)    



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

class InterpolationStatisticsWindow(QtWidgets.QWidget):
    def __init__(self, signal, color):
        super().__init__()
        self.signal = signal
        self.color = color  # Store the color
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Interpolated Signal Statistics")
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        layout = QtWidgets.QVBoxLayout()

        # Plot for Interpolated Signal
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('black')
        self.plot_widget.plot(self.signal, pen=self.color)
        self.plot_widget.setTitle("Interpolated Signal")
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = SignalApp()
    ex.resize(900, 700)
    ex.show()
    sys.exit(app.exec_())