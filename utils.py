from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5 import QtGui, QtWidgets
from pyqtgraph import PlotWidget, QtCore
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
    @staticmethod
    def create_button(text, method, icon_name='', stylesheet=button_style_sheet):
        button = QtWidgets.QPushButton(text)

        # Adjust the button to be a perfect circle
        button.setStyleSheet(stylesheet)
        # Set size policy to allow stretching
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # Optional icon for the button
        if icon_name:
            icon = QtGui.QIcon('assets\\button_icons\\' + icon_name + '.png')
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(55,55 ))  # Enlarge the icon size

        else:
            button.setText(text)
        # Connect the button to the method
        button.clicked.connect(method)
        
        return button

    @staticmethod
    def validate_input(value):
        return isinstance(value, str) and bool(value)

# Example usage within a PyQt application
