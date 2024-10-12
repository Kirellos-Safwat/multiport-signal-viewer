from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.series_lat = QLineSeries()
        self.series_lon = QLineSeries()
        self.series_lat.setName("Latitude")
        self.series_lon.setName("Longitude")
        self.data = {'time': [], 'latitude': [], 'longitude': []}
        self.start_time = datetime.now()
        
        self.initUI()
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get('https://www.orbtrack.org/#/?satName=ISS%20(ZARYA)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(500)  # update every 500 ms

    def initUI(self):
        self.layout = QVBoxLayout()
        
        # Labels
        self.lat_label = QLabel('Latitude: ')
        self.lon_label = QLabel('Longitude: ')
        self.time_label = QLabel('Time: ')
        self.layout.addWidget(self.lat_label)
        self.layout.addWidget(self.lon_label)
        self.layout.addWidget(self.time_label)
        
        # Chart setup
        self.chart = QChart()
        self.chart.addSeries(self.series_lat)
        self.chart.addSeries(self.series_lon)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.setTitle("Real-time ISS Location")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)   # I added this

        # Axis setup
        self.axis_x = QDateTimeAxis()
        # self.axis_x.setTickCount(10)
        self.axis_x.setFormat("hh:mm:ss")
        self.axis_x.setTitleText("Time (HH:MM:SS)")
        
        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%f")
        self.axis_y.setTitleText("Value")
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.series_lat.attachAxis(self.axis_x)
        self.series_lat.attachAxis(self.axis_y)
        self.series_lon.attachAxis(self.axis_x)
        self.series_lon.attachAxis(self.axis_y)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart.axisY(self.series_lat).setRange(-180, 180)       # I added this
        self.chart.axisY(self.series_lon).setRange(-180, 180)       # I added this
        self.layout.addWidget(self.chart_view)
        
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        
        self.setWindowTitle('Real-time ISS Location')
        self.show()

    def update_data(self):
        try:
            latitude = self.driver.find_element(By.ID, 'satLat').text.replace('°', '').strip()
            longitude = self.driver.find_element(By.ID, 'satLon').text.replace('°', '').strip()
            time_str = self.driver.find_element(By.ID, 'satUTC').text.strip()

            self.lat_label.setText(f'Latitude: {latitude}')
            self.lon_label.setText(f'Longitude: {longitude}')
            self.time_label.setText(f'Time: {time_str}')

            # Clean and convert strings to floats
            if latitude == '.':
                latitude = 0.0
            else:
                latitude = float(latitude.replace(',', '.'))

            if longitude == '.':
                longitude = 0.0
            else:
                longitude = float(longitude.replace(',', '.'))
            
            
            # Calculate elapsed time
            current_time = datetime.now()
            self.data['time'].append(current_time)
            self.data['latitude'].append(latitude)
            self.data['longitude'].append(longitude)
            
            # Update series
            self.series_lat.append(int(current_time.timestamp() * 1000), latitude)
            self.series_lon.append(int(current_time.timestamp() * 1000), longitude)
            
            self.axis_x.setMin(QDateTime.fromMSecsSinceEpoch(int(self.data['time'][0].timestamp() * 1000)))
            self.axis_x.setMax(QDateTime.fromMSecsSinceEpoch(int(self.data['time'][-1].timestamp() * 1000)))

            # Force refresh the chart
            self.chart_view.update()
            self.chart_view.repaint()

        except ValueError as e:
            print(f"ValueError: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def closeEvent(self, event):
        self.driver.quit()
        event.accept()

