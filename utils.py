from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
from PyQt5 import QtGui, QtWidgets
from pyqtgraph import PlotWidget, QtCore
import os
import numpy as np
import random
from signal import Signal


class Utils:
    button_style_sheet = """
            QPushButton {
                background-color: #adb4b4; 
                color: black;
                font-size: 14px;
                padding: 10;
                font-weight: bold; 
                border-radius: 25px;  /* Makes the button a perfect circle */
                width: 30px;  /* Set the width to 50px */
                height: 30px;  /* Set the height to 50px */
                border: 2px solid #4c7273;
            }
            QPushButton:hover {
                background-color: #4c7273; 
                border-radius: 15px;  
                border: 2px solid white;                       
            }
            QPushButton:pressed {
                background-color: #86b9b0;
            }
        """

    slider_style_sheet = """
            QSlider {
                background-color: #042630;
                padding: 0px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #4c7273;
                height: 8px;
                background: #1e1e1e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #86b9b0;
                border: 2px solid #4c7273;
                width: 16px;
                height: 16px;
                margin: -5px 0; /* Centers the handle with the groove */
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #083838;
                border: 2px solid #4c7273;
            }
            QSlider::sub-page:horizontal {
                background: #86b9b0;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #1e1e1e;
                border-radius: 4px;
            }
        """

    window_style_sheet = "background-color: #042630;"

    checkBox_style_sheet = """
            QCheckBox {
                color: #d0d6d6;           
                font-size: 14px;          
                padding: 5px;             
            }
            QCheckBox::indicator {
                width: 18px;              
                height: 18px;
                border-radius: 5px;       
                border: 2px solid #4c7273;
                background-color: #4c7273; 
            }
            QCheckBox::indicator:checked {
                background-color: #86b9b0; 
                border: 2px solid #4c7273; 
            }
            QCheckBox::indicator:hover {
                border: 2px solid #86b9b0; 
            }
        """

    lineEdit_style_sheet = """
            QLineEdit {
                color: white;
                font-size: 16px;
                padding: 5px;
                margin-top: 10px;
                margin-bottom: 10px;
                border: 2px solid #4c7273;
                border-radius: 10px;
                background-color: #1e1e1e;
            }
        """

    label_style_sheet = """
            QLabel {
                color: white;
                font-size: 14px;
                padding-bottom: 5px;
            }
        """

    comboBox_style_sheet = """
            QComboBox {
                color: white; /* Color of the text */
                font-size: 16px;
                padding: 5px;
                margin-top: 10px;
                margin-bottom: 10px;
                border: 2px solid #4c7273;
                border-radius: 10px;
                background-color: #1e1e1e; /* Background color */
            }

            QComboBox::drop-down {
                border: none; /* Remove border from the dropdown */
            }

            QComboBox QAbstractItemView {
                background-color: #1e1e1e; /* Background color for the dropdown */
                color: white; /* Text color for unselected items */
            }

            QComboBox QAbstractItemView::item {
                background-color: #1e1e1e; /* Background color for items */
                color: white; /* Text color for items */
            }

            QComboBox::item:selected {
                background-color: #4c7273; /* Background color for selected item */
                color: white; /* Text color for selected item */
            }
        """
    # A method for creating each button as a Pushbutton from QT and setting the method to be called when the button is pressed:
    # Generating the square wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=1 when t<0.5 and f=0 when t>0.5

    @staticmethod
    def generate_square_wave(points):
        t = np.linspace(0, points/100, points)
        return (t < 0.5).astype(int)

    # Generating the cosine wave by creating an array of "points" number of evenly spaced values over interval[0,1] then setting f=cos(2*pi*F*t) for a periodic function of freq = 5Hz
    @staticmethod
    def generate_cosine_wave(points):
        t = np.linspace(0, points/100, points)
        return (np.cos(2*np.pi*5*t))

    @staticmethod
    def generate_sine_wave(points):
        t = np.linspace(0, points/100, points)
        return (np.sin(2*np.pi*5*t))

    @staticmethod
    def create_button(text, method, icon_name='', stylesheet=button_style_sheet, set_enabled=True):
        button = QtWidgets.QPushButton(text)

        # Adjust the button to be a perfect circle
        button.setStyleSheet(stylesheet)
        # Set size policy to allow stretching
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Fixed)

        # Optional icon for the button
        if icon_name:
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(
                base_path, 'assets', 'button_icons', icon_name + '.png')
            icon = QtGui.QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(55, 55))  # Enlarge the icon size

        else:
            button.setText(text)
        # Connect the button to the method
        button.clicked.connect(method)
        button.setEnabled(set_enabled)

        return button

    @staticmethod
    def update_button(button, text, icon_name):
        button.setText(text)
        icon = QtGui.QIcon('assets\\button_icons\\'+str(icon_name)+'.png')
        button.setIcon(icon)
        return button

    @staticmethod
    def show_error_message(message):
        # Create a QMessageBox for error
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setWindowIcon(QtGui.QIcon("assets\\Pulse.png"))
        msg_box.exec_()

    @staticmethod
    def show_info_message(message, glue=False):
        # Create a QMessageBox for information with two options
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Information")
        msg_box.setWindowIcon(QtGui.QIcon("assets\\Pulse.png"))
        if glue:
            # Add custom buttons for glue
            reset_button = msg_box.addButton("Reset", QMessageBox.ActionRole)
            continue_button = msg_box.addButton(
                "Continue", QMessageBox.AcceptRole)
            # Execute the message box
            msg_box.exec_()
            # Determine which button was clicked
            if msg_box.clickedButton() == reset_button:
                return "reset"
            else:
                return "continue"

    @staticmethod
    def show_warning_message(message):
        # Create a QMessageBox for warning
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle("Warning")
        msg_box.setWindowIcon(QtGui.QIcon("assets\\Pulse.png"))
        msg_box.exec_()

    @staticmethod
    # browsing local signal files, returning signal data as np array
    def import_signal_file(plot):
        file_name, _ = QFileDialog.getOpenFileName()
        sampling_rate = 1
        if file_name:
            extension = os.path.splitext(file_name)[1].lower()
            if extension == '.csv':
                with open(file_name, mode='r') as file:
                    # Read the sampling rate from the first line
                    sampling_rate = float(file.readline().strip())

                    # Load the remaining data into a NumPy array
                    signal_data = np.genfromtxt(file, delimiter=',')

                # Optionally, you can return or use the sampling rate as needed
                print("Sampling Rate:", sampling_rate)
            elif extension == '.txt':
                # Assuming space-separated signal data in TXT file
                signal_data = np.loadtxt(file_name)
            elif extension == '.bin':
                with open(file_name, 'rb') as f:
                    # Load binary data assuming it's float32 by default
                    signal_data = np.fromfile(f, dtype=np.dtype)
            else:
                Utils.show_error_message("Unsupported file format.")
                return
        else:
            return

        if signal_data.ndim == 1:
            new_signal = Signal(
                signal_data=signal_data,
                color=Utils.generate_random_light_color(),
                title=os.path.splitext(os.path.basename(file_name))[0],
                f_sample=sampling_rate
            )
            
            # Append the newly created Signal instance to the signals list
            plot.signals.append(new_signal)
            plot.max_length = max(plot.max_length, len(signal_data))
            plot.update_max_time(np.linspace(0, plot.max_length / sampling_rate, plot.max_length))
            plot.plot_signals()

        else:
            Utils.show_error_message(
                "Unsupported signal dimension." + str(signal_data.ndim))

    @staticmethod
    def generate_random_light_color():
        # Generate RGB values that are in a range that avoids dark colors
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        return (r, g, b)
