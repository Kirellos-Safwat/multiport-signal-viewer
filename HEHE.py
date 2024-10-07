import sys, os
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from statistics_window import StatisticsWindow
from interpolation_window import InterpolationWindow

class SignalApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stopped_by_link = False  # For the linking feature
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
        
        # Link state Flag
        self.linked = False

        # Sync Flag
        self.syncing = False

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
        self.setWindowIcon(QtGui.QIcon("assets\\Pulse.png")) # Window Icon
        self.setStyleSheet("background-color: #2e2e2e;") # Dark Grey Color for the Window Background
        
        # Setting the Main layout (Organizing Structure On Top Of Each Other)
        self.main_layout = QtWidgets.QVBoxLayout() # Vertical Layout for the positioning of child widgets within a parent widget
        self.setLayout(self.main_layout)

        # Creating signals plotting widgets
        self.plot_widget1 = PlotWidget()
        self.plot_widget2 = PlotWidget()
        
        self.plot_widget1.setBackground('black')
        self.plot_widget2.setBackground('black')
        
        # Adding the plotting widgets of the first signal to the main "vertical" layout 
        self.main_layout.addWidget(self.plot_widget1)

        # Create title input for Signal 1
        self.title_input1 = QtWidgets.QLineEdit("Signal 1")
        self.title_input1.setStyleSheet("color: white; font-size: 16px;")
        self.title_input1.textChanged.connect(self.update_signal_titles)
        self.main_layout.addWidget(self.title_input1)

        # Checkbox for Signal 1 visibility
        self.show_hide_checkbox1 = QtWidgets.QCheckBox("Show Signal 1")
        self.show_hide_checkbox1.setChecked(True)
        self.show_hide_checkbox1.stateChanged.connect(self.toggle_signal1)
        self.show_hide_checkbox1.stateChanged.connect(self.sync_checkboxes)  # Sync checkboxes
        self.main_layout.addWidget(self.show_hide_checkbox1)


        # Setting the Control buttons for Signal 1:
        # Creating "horizontal" layout for the buttons of signal 1:
        self.play_pause_button1 = self.create_button("Play", self.play_pause_signal1, "play")
        button_layout1 = self.create_button_layout(
            self.play_pause_button1, self.stop_signal1, lambda: self.change_color(signal_index=1), 
            self.zoom_in1, self.zoom_out1, lambda: self.show_statistics(self.signal1, self.title1, self.color1)  
        )
        # Adding the "horizontal" button layout of signal 1 to the main "vertical" layout 
        self.main_layout.addLayout(button_layout1)

        # Creating import signal button
        self.import_signal1_button = self.create_button("Import", lambda: self.import_signal_file("graph1"), "import")
        self.main_layout.addWidget(self.import_signal1_button)

        # Adding the plotting widgets of the first signal to the main "vertical" layout 
        self.main_layout.addWidget(self.plot_widget2)

        # Create title input for Signal 2
        self.title_input2 = QtWidgets.QLineEdit("Signal 2")
        self.title_input2.setStyleSheet("color: white; font-size: 16px;")
        self.title_input2.textChanged.connect(self.update_signal_titles)
        self.main_layout.addWidget(self.title_input2)

        # Checkbox for Signal 2 visibility
        self.show_hide_checkbox2 = QtWidgets.QCheckBox("Show Signal 2")
        self.show_hide_checkbox2.setChecked(True)
        self.show_hide_checkbox2.stateChanged.connect(self.toggle_signal2)
        self.show_hide_checkbox2.stateChanged.connect(self.sync_checkboxes)  # Sync checkboxes
        self.main_layout.addWidget(self.show_hide_checkbox2)

        # Setting the Control buttons for Signal 2:
        # Creating "horizontal" layout for the buttons of signal 2:
        self.play_pause_button2 = self.create_button("Play", self.play_pause_signal2, "play")
        button_layout2 = self.create_button_layout(
            self.play_pause_button2, self.stop_signal2, lambda: self.change_color(signal_index=2), 
            self.zoom_in2, self.zoom_out2, lambda: self.show_statistics(self.signal2, self.title2, self.color2)
        )
        # Adding the "horizontal" button layout of signal 2 to the main "vertical" layout 
        self.main_layout.addLayout(button_layout2)

        # Creating import signal button
        self.import_signal2_button = self.create_button("Import", lambda: self.import_signal_file("graph2"), "import")
        self.main_layout.addWidget(self.import_signal2_button)
        # Swap Signals Button
        self.swap_button = self.create_button("Swap Signals", self.swap_signals, "swap")
        # glue Signals Button
        self.glue_button = self.create_button("glue Signals", self.glue_signals)

        # Link Button
        self.link_button = self.create_button("Link Graphs", self.toggle_link, "link")
        # self.main_layout.addWidget(self.link_button)
        buttons_layout_3 = QtWidgets.QHBoxLayout()
        buttons_layout_3.addWidget(self.swap_button)
        buttons_layout_3.addWidget(self.glue_button)
        buttons_layout_3.addWidget(self.link_button)
        self.main_layout.addLayout(buttons_layout_3)

    def sync_checkboxes(self):
        if self.linked:
            # Sync checkbox 1 with checkbox 2
            if self.sender() == self.show_hide_checkbox1:
                self.show_hide_checkbox2.setChecked(self.show_hide_checkbox1.isChecked())
            elif self.sender() == self.show_hide_checkbox2:
                self.show_hide_checkbox1.setChecked(self.show_hide_checkbox2.isChecked())

    def update_signal_titles(self):
        """ Updates the plot titles dynamically as the user changes the title inputs. """
        self.plot_widget1.setTitle(self.title_input1.text())
        self.plot_widget2.setTitle(self.title_input2.text())

    def toggle_signal1(self, state):
        if state == Qt.Checked:
            # Plot signal1 only if it's checked
            self.plot_widget1.clear()
            self.plot_widget1.plot(self.signal1, pen=self.color1)
            self.plot_widget1.setYRange(-1, 1)
            self.plot_widget1.setTitle(self.title_input1.text())
        else:
            self.plot_widget1.clear()  # Clear the plot if unchecked

    def toggle_signal2(self, state):
        if state == Qt.Checked:
            # Plot signal2 only if it's checked
            self.plot_widget2.clear()
            self.plot_widget2.plot(self.signal2, pen=self.color2)
            self.plot_widget2.setYRange(-1, 1)
            self.plot_widget2.setTitle(self.title_input2.text())
        else:
            self.plot_widget2.clear()  # Clear the plot if unchecked

    def sync_checkboxes(self):
        if self.linked:
            # Sync checkbox 1 with checkbox 2
            if self.sender() == self.show_hide_checkbox1:
                self.show_hide_checkbox2.setChecked(self.show_hide_checkbox1.isChecked())
            elif self.sender() == self.show_hide_checkbox2:
                self.show_hide_checkbox1.setChecked(self.show_hide_checkbox2.isChecked())

    def update_signal_titles(self):
        """ Updates the plot titles dynamically as the user changes the title inputs. """
        self.plot_widget1.setTitle(self.title_input1.text())
        self.plot_widget2.setTitle(self.title_input2.text())

    def toggle_signal1(self, state):
        if state == Qt.Checked:
            # Plot signal1 only if it's checked
            self.plot_widget1.clear()
            self.plot_widget1.plot(self.signal1, pen=self.color1)
            self.plot_widget1.setYRange(-1, 1)
            self.plot_widget1.setTitle(self.title_input1.text())
        else:
            self.plot_widget1.clear()  # Clear the plot if unchecked

    def toggle_signal2(self, state):
        if state == Qt.Checked:
            # Plot signal2 only if it's checked
            self.plot_widget2.clear()
            self.plot_widget2.plot(self.signal2, pen=self.color2)
            self.plot_widget2.setYRange(-1, 1)
            self.plot_widget2.setTitle(self.title_input2.text())
        else:
            self.plot_widget2.clear()  # Clear the plot if unchecked

    # Generating the function responsible for linking/unlinking graphs
    def toggle_link(self):
        self.linked = not self.linked
        # Sync play state if linked
        if self.linked:
            # Sync the visibility of the checkboxes
            self.show_hide_checkbox2.setChecked(self.show_hide_checkbox1.isChecked())
            self.link_button = self.update_button(self.link_button, "Unlink Graphs", "unlink")
        # This is dedicated to the case where one of the signals is already playing before linking the 2 graphs together
            if self.playing1:
                self.play_pause_signal2()
            elif self.playing2:
                self.play_pause_signal1()

            self.link_viewports()
        else: 
            self.link_button = self.update_button(self.link_button, "Link Graphs", "link")
            self.unlink_viewports()

        # Ensure consistent signal speeds
        if self.linked:
            # Check if both timers are running and have the same interval
            if self.timer1 is not None and self.timer2 is not None:
                if self.timer1.interval() != self.timer2.interval():
                    self.timer2.setInterval(self.timer1.interval())  # Sync intervals


    def link_viewports(self):
        # Sync the range and zoom between both graphs
        # The sigRangeChanged signal is part of the pyqtgraph library.
        self.plot_widget1.sigRangeChanged.connect(self.sync_range)
        self.plot_widget2.sigRangeChanged.connect(self.sync_range)
        
        # Sync the initial view range when linking
        self.sync_viewports()

    def unlink_viewports(self):
        # Properly disconnect the range syncing behavior to stop linking
        self.plot_widget1.sigRangeChanged.disconnect(self.sync_range)
        self.plot_widget2.sigRangeChanged.disconnect(self.sync_range)

    def sync_viewports(self):
        # Ensure both graphs have the same zoom and pan when linked
        range1 = self.plot_widget1.viewRange() # returns a list containing two elements: the x-range and y-range
        self.plot_widget2.setXRange(*range1[0], padding=0) # Padding = 0 is used to prevent signal shrinking by preventing buffer space
        self.plot_widget2.setYRange(*range1[1], padding=0) # The asterisk in here unpacks the tuple so that setXRange() receives two args: start&end of range

    def sync_range(self):
        if self.syncing:
            return  # Prevent recursive syncing

        self.syncing = True

        if self.sender() == self.plot_widget1:
            range1 = self.plot_widget1.viewRange()
            self.plot_widget2.setXRange(*range1[0], padding=0)
            self.plot_widget2.setYRange(*range1[1], padding=0)
        else:
            range2 = self.plot_widget2.viewRange()
            self.plot_widget1.setXRange(*range2[0], padding=0)
            self.plot_widget1.setYRange(*range2[1], padding=0)
    
        self.syncing = False


    # A method for Setting the horizontal layout of the buttons according to the signal_name
    def create_button_layout(self, play_pause_button, stop, color_change, zoom_in, zoom_out, statistics):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(play_pause_button)
        button_layout.addWidget(self.create_button(f"Stop", stop, "stop"))
        button_layout.addWidget(self.create_button(f"Color", color_change, "color"))
        button_layout.addWidget(self.create_button(f"Zoom In", zoom_in, "zoom_in"))
        button_layout.addWidget(self.create_button(f"Zoom Out", zoom_out, "zoom_out"))
        button_layout.addWidget(self.create_button(f"Statistics", statistics, "statistics"))
        return button_layout


    # A method for creating each button as a Pushbutton from QT and setting the method to be called when the button is pressed:
    def create_button(self, text, method, icon_name = ''):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet("background-color: #0078d7; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        icon = QtGui.QIcon('assets\\button_icons\\'+icon_name+'.png')
        button.setIcon(icon)
        button.clicked.connect(method)
        return button


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
        self.plot_widget1.clear()  #The clear method is used to clear the frame every time before making the new frame!
        self.plot_widget2.clear()  #The clear method is used to clear the frame every time before making the new frame!

        # Store original x and y ranges after the first plot
        self.original_x_range = self.plot_widget1.viewRange()[0]
        self.original_y_range = self.plot_widget1.viewRange()[1]

        # Enable panning
        self.plot_widget1.setMouseEnabled(x=True, y=True)

        # Store original x and y ranges after the first plot
        self.original_x_range2 = self.plot_widget2.viewRange()[0]
        self.original_y_range2 = self.plot_widget2.viewRange()[1]

        # Enable panning
        self.plot_widget2.setMouseEnabled(x=True, y=True)

        # Synchronize the zoom and pan if linked
        if self.linked:
            self.sync_viewports()  # Initial sync on plotting

        # Check the visibility states and plot accordingly
        if self.show_hide_checkbox1.isChecked():
            self.plot_widget1.plot(self.signal1, pen=self.color1)
            self.plot_widget1.setYRange(-1, 1)
            self.plot_widget1.setTitle(self.title_input1.text())
        # No need to explicitly hide the plot; just don't plot if the checkbox is unchecked.

        if self.show_hide_checkbox2.isChecked():
            self.plot_widget2.plot(self.signal2, pen=self.color2)
            self.plot_widget2.setYRange(-1, 1)
            self.plot_widget2.setTitle(self.title_input2.text())

    # Generating the function of playing signal 1
    def play_pause_signal1(self):
        if self.show_hide_checkbox1.isChecked(): 
            if not self.playing1:
                self.playing1 = True
                self.play_pause_button1 = self.update_button(self.play_pause_button1, "Pause", "pause")
                if self.timer1 is None:
                    self.timer1 = pg.QtCore.QTimer() # Creates a timer where the plot would be updated with new data, allowing real-time visualization of signal.
                    self.timer1.timeout.connect(self.update_plot1)
                    self.timer1.start(100) #Frequent updates every 100ms
                if self.linked and not self.playing2:
                    self.play_pause_signal2()

            else:
                self.playing1 = False
                self.play_pause_button1 = self.update_button(self.play_pause_button1, "Play", "play")        
                if self.linked and self.playing2:
                    self.play_pause_signal2()

    # Generating the function of stopping/resetting signal 1
    def stop_signal1(self):
        if self.show_hide_checkbox1.isChecked(): 
            if self.timer1 is not None:
                self.timer1.stop()
                self.timer1 = None
            self.playing1 = False
            self.play_pause_button1 = self.update_button(self.play_pause_button1, "Play", "play")
            if self.linked and not self.stopped_by_link:
                self.stopped_by_link = True
                self.stop_signal2()
            self.reset_signal1()
            self.stopped_by_link = False

    # Generating the function of playing signal 2
    def play_pause_signal2(self):
        if self.show_hide_checkbox2.isChecked(): 
            if not self.playing2:
                self.playing2 = True
                self.play_pause_button2 = self.update_button(self.play_pause_button2, "Pause", "pause")
                if self.timer2 is None:
                    self.timer2 = pg.QtCore.QTimer()
                    self.timer2.timeout.connect(self.update_plot2)
                    self.timer2.start(100)
                if self.linked and not self.playing1:
                    self.play_pause_signal1()

            else:
                self.playing2 = False
                self.play_pause_button2 = self.update_button(self.play_pause_button2, "Play", "play")
                if self.linked and self.playing1:
                    self.play_pause_signal1()

    # Generating the function of stopping/resetting signal 2
    def stop_signal2(self):
        if self.show_hide_checkbox2.isChecked(): 
            if self.timer2 is not None:
                self.timer2.stop()
                self.timer2 = None
            self.playing2 = False
            self.play_pause_button2 = self.update_button(self.play_pause_button2, "Play", "play")
            if self.linked and not self.stopped_by_link:
                self.stopped_by_link = True
                self.stop_signal1()
            self.reset_signal2()
            self.stopped_by_link = False

    def update_button(self, button, text, icon_name):
        button.setText(text)
        icon = QtGui.QIcon('assets\\button_icons\\'+str(icon_name)+'.png')
        button.setIcon(icon)
        return button

    def reset_signal1(self):
        if self.type1 == 'cosine':
            self.signal1 = self.generate_cosine_wave(100)
        else:
            self.signal1 = self.generate_square_wave(100)
        self.plot_signals()

    def reset_signal2(self):
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
        # Calculate the new ranges based on the original ranges
        x_range = plot_widget.viewRange()[0]
        y_range = plot_widget.viewRange()[1]
        new_x_range = (x_range[0] + (self.original_x_range[1] - self.original_x_range[0]) * 0.1, x_range[1] - (self.original_x_range[1] - self.original_x_range[0]) * 0.1)
        new_y_range = (y_range[0] + (self.original_y_range[1] - self.original_y_range[0]) * 0.1, y_range[1] - (self.original_y_range[1] - self.original_y_range[0]) * 0.1)
        plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
        plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
        # If linked, apply to second plot
        if self.linked:
            self.plot_widget2.setXRange(new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget2.setYRange(new_y_range[0], new_y_range[1], padding=0)

                # Update original ranges after zooming
        self.original_x_range = new_x_range
        self.original_y_range = new_y_range

    def zoom_out(self, plot_widget):
        # Calculate the new ranges based on the original ranges
        x_range = plot_widget.viewRange()[0]
        y_range = plot_widget.viewRange()[1]
        new_x_range = (x_range[0] - (self.original_x_range[1] - self.original_x_range[0]) * 0.1, x_range[1] + (self.original_x_range[1] - self.original_x_range[0]) * 0.1)
        new_y_range = (y_range[0] - (self.original_y_range[1] - self.original_y_range[0]) * 0.1, y_range[1] + (self.original_y_range[1] - self.original_y_range[0]) * 0.1)
        plot_widget.setXRange(new_x_range[0], new_x_range[1], padding=0)
        plot_widget.setYRange(new_y_range[0], new_y_range[1], padding=0)
        # If linked, apply to second plot
        if self.linked:
            self.plot_widget2.setXRange(new_x_range[0], new_x_range[1], padding=0)
            self.plot_widget2.setYRange(new_y_range[0], new_y_range[1], padding=0)

        # Update original ranges after zooming
        self.original_x_range = new_x_range
        self.original_y_range = new_y_range
        
    # Generating the function of swapping both signals together (swapping signal,color,title,type)
    def swap_signals(self):
        self.signal1, self.signal2 = self.signal2, self.signal1
        self.color1, self.color2 = self.color2, self.color1

        # Swap the text of the title input boxes
        title_text_1 = self.title_input1.text()
        title_text_2 = self.title_input2.text()
        self.title_input1.setText(title_text_2)
        self.title_input2.setText(title_text_1)

        # Swap the state of the visibility checkboxes
        show_hide_checkbox1_state = self.show_hide_checkbox1.isChecked()
        show_hide_checkbox2_state = self.show_hide_checkbox2.isChecked()
        self.show_hide_checkbox1.setChecked(show_hide_checkbox2_state)
        self.show_hide_checkbox2.setChecked(show_hide_checkbox1_state)

        # Ensure visibility reflects the swapped states
        self.toggle_signal1(Qt.Checked if show_hide_checkbox2_state else Qt.Unchecked)
        self.toggle_signal2(Qt.Checked if show_hide_checkbox1_state else Qt.Unchecked)

        # Swap the labels of the visibility checkboxes
        show_hide_checkbox1_label = self.show_hide_checkbox1.text()
        show_hide_checkbox2_label = self.show_hide_checkbox2.text()
        self.show_hide_checkbox1.setText(show_hide_checkbox2_label)
        self.show_hide_checkbox2.setText(show_hide_checkbox1_label)

        self.plot_signals()

    # browsing local signal files, returning signal data as np array
    def import_signal_file(self, graph):
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name:
            extension = os.path.splitext(file_name)[1].lower()
            if extension == '.csv':
                signal_data = np.genfromtxt(file_name, delimiter=',') # Assuming each row in the CSV represents signal data
            elif extension == '.txt':
                signal_data = np.loadtxt(file_name) # Assuming space-separated signal data in TXT file
            elif extension == '.bin':
                with open(file_name, 'rb') as f:
                    # Load binary data assuming it's float32 by default
                    signal_data = np.fromfile(f, dtype=np.dtype)
            else:
                self.show_error_message("Unsupported file format.")
                return

        if signal_data.ndim == 1:
            if graph == 'graph1':
                self.signal1 = signal_data
                self.title1 = os.path.splitext(os.path.basename(file_name))[0]
            elif graph == 'graph2':
                self.signal2 = signal_data
                self.title2 = os.path.splitext(os.path.basename(file_name))[0]
            
        else:
            self.show_error_message("Unsupported signal dimension." + str(signal_data.ndim))
            
    
    def show_error_message(self, message):
        # Create a QMessageBox for error
        self.msg_box = QMessageBox()
        self.msg_box.setIcon(QMessageBox.Critical)
        self.msg_box.setText(message)
        self.msg_box.setWindowTitle("Error")
        self.msg_box.exec_()


    # Generating the function of interpolating(averaging)(gluing) both signals
    def glue_signals(self):
        self.glued_signal = (self.signal1 + self.signal2) / 2
        self.interpolation_window = InterpolationWindow(self.glued_signal) # Generating the Intepolation Window
        self.interpolation_window.show() # Showing the Interpolation Window

    def show_statistics(self, signal, title, color):
        self.statistics_window = StatisticsWindow(signal, title, color) # Generating the Statistics Window
        self.statistics_window.show() # Showing the Statistics Window   

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = SignalApp()
    ex.resize(900, 700)
    ex.show()
    sys.exit(app.exec_())