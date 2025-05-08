
import json
import socket
import sys
import random
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSlider, 
                            QTabWidget, QFrame, QGridLayout, QScrollArea,
                            QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

from Temperature import Temperature_Dashboard
from Humidity import Humidity_Dashboard
from Soil_moisture import Soil_moisture_Dashboard
from Water_pH import Water_pH_Dashboard
from Lighting import Lighting_Dashboard

from getaway import function_call
from get_data import read_sensor

from Warning import RoundedWarningDialog



class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setStyleSheet("background-color:white;")
        
class AgriculturalMonitoringSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agricultural Monitoring System")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #00c4a7;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00b89c;
            }
            QLabel {
                color: #4a4a4a;
            }
        """)
        
        self.auto_climate_temperature = False
        self.auto_climate_lighting = False
        self.auto_climate_humidity = False
        self.auto_climate_soil = False
        self.auto_climate_water = False

        # Initialize system states
        self.light_status = False
        self.watering_status = False
        self.heater_status = False
        self.humidifier_status = False
        self.pump_water_status = False
        self.auto_climate_active = False 

        self.target_heat = 15.0
        self.target_humidity = 60.0
        self.target_water_level = 60.0
        self.target_moisture = 60.0
        self.target_light = 60.0

        # Data history
        self.temp_history = [random.uniform(15, 35) for _ in range(24)]
        self.humidity_history = [random.uniform(20, 50) for _ in range(24)]
        self.moisture_history = [random.uniform(60, 95) for _ in range(24)]
        self.ph_history = [random.uniform(5.5, 7.0) for _ in range(24)]
        self.light_history = [random.uniform(65, 95) for _ in range(24)]
        
        # Set up main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.warning_dialog_open = False
        self.last_warning_time = 0
        

        # Create header
        self.setup_header()
        
        # Create dashboard cards
        self.setup_dashboard_cards()
        
        # Create charts section
        self.setup_charts_section()
        
        # Create control panel
        self.setup_control_panel()
        
        # Setup timer for sensor updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(500)
        
        # Initial sensor update
        self.update_sensor_data()

    def send_status_to_raspberry(self, device_states: dict):
        HOST = '192.168.16.54'
        PORT = 65432

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            message = json.dumps(device_states)
            s.sendall(message.encode('utf-8'))

    def open_dashboard(self, open_dashboard):
        self.dashboard_window = open_dashboard(back_to_main=self.show, main_system=self)
        self.dashboard_window.showFullScreen()
        self.hide() 

    def setup_header(self):
        header_layout = QHBoxLayout()
        
        title = QLabel("Agriculture Monitoring Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        
        current_date = QLabel(datetime.now().strftime("%A, %B %d, %Y"))
        current_date.setFont(QFont("Arial", 10))
        current_date.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(current_date)
        
        self.main_layout.addLayout(header_layout)
        
    def setup_dashboard_cards(self):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Soil Moisture Card
        moisture_card = QFrame()
        moisture_card.setFrameShape(QFrame.StyledPanel)
        moisture_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        moisture_layout = QVBoxLayout(moisture_card)
        
        self.moisture_value = QLabel("87.50")
        self.moisture_value.setFont(QFont("Arial", 28, QFont.Bold))
        
        moisture_icon = QLabel("〰️〰️")
        moisture_icon.setFont(QFont("Arial", 24))
        moisture_icon.setStyleSheet("color: #00c4a7;")
        moisture_title_button = QPushButton("Soil Moisture")
        moisture_title_button.setFont(QFont("Arial", 12))
        moisture_title_button.clicked.connect(lambda: self.open_dashboard(Soil_moisture_Dashboard))
        moisture_layout.addWidget(moisture_title_button)
        
        moisture_subtitle = QLabel("Soil Moisture Content")
        moisture_subtitle.setFont(QFont("Arial", 8))
        moisture_subtitle.setStyleSheet("color: #888;")
        
        moisture_header = QHBoxLayout()
        moisture_header.addWidget(self.moisture_value)
        moisture_header.addStretch()
        moisture_header.addWidget(moisture_icon)
        
        moisture_layout.addLayout(moisture_header)
        moisture_layout.addWidget(moisture_title_button)
        moisture_layout.addWidget(moisture_subtitle)
        
        # Temperature Card
        temp_card = QFrame()
        temp_card.setFrameShape(QFrame.StyledPanel)
        temp_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        temp_layout = QVBoxLayout(temp_card)
        
        self.temp_value = QLabel("32.50")
        self.temp_value.setFont(QFont("Arial", 28, QFont.Bold))
        
        temp_icon = QLabel("🌡️")
        temp_icon.setFont(QFont("Arial", 24))
        temp_icon.setStyleSheet("color: #00c4a7;")
        
        temp_title_button = QPushButton("Temperature")
        temp_title_button.setFont(QFont("Arial", 12))
        temp_title_button.clicked.connect(lambda: self.open_dashboard(Temperature_Dashboard))
        temp_layout.addWidget(temp_title_button)
        
        temp_subtitle = QLabel("Air Temperature")
        temp_subtitle.setFont(QFont("Arial", 8))
        temp_subtitle.setStyleSheet("color: #888;")
        
        temp_header = QHBoxLayout()
        temp_header.addWidget(self.temp_value)
        temp_header.addStretch()
        temp_header.addWidget(temp_icon)
        
        temp_layout.addLayout(temp_header)
        temp_layout.addWidget(temp_title_button)
        temp_layout.addWidget(temp_subtitle)
        
        # Humidity Card
        humidity_card = QFrame()
        humidity_card.setFrameShape(QFrame.StyledPanel)
        humidity_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        humidity_layout = QVBoxLayout(humidity_card)
        
        self.humidity_value = QLabel("20%")
        self.humidity_value.setFont(QFont("Arial", 28, QFont.Bold))
        
        humidity_icon = QLabel("💧")
        humidity_icon.setFont(QFont("Arial", 24))
        humidity_icon.setStyleSheet("color: #00c4a7;")
        
        humidity_title_button = QPushButton("Humidity")
        humidity_title_button.setFont(QFont("Arial", 12))
        humidity_title_button.clicked.connect(lambda: self.open_dashboard(Humidity_Dashboard))
        humidity_layout.addWidget(humidity_title_button)
        
        humidity_subtitle = QLabel("Amount of water present in air")
        humidity_subtitle.setFont(QFont("Arial", 8))
        humidity_subtitle.setStyleSheet("color: #888;")
        
        humidity_header = QHBoxLayout()
        humidity_header.addWidget(self.humidity_value)
        humidity_header.addStretch()
        humidity_header.addWidget(humidity_icon)
        
        humidity_layout.addLayout(humidity_header)
        humidity_layout.addWidget(humidity_title_button)
        humidity_layout.addWidget(humidity_subtitle)
        
        # pH Level Card
        ph_card = QFrame()
        ph_card.setFrameShape(QFrame.StyledPanel)
        ph_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        ph_layout = QVBoxLayout(ph_card)
        
        self.ph_value = QLabel("5.8")
        self.ph_value.setFont(QFont("Arial", 28, QFont.Bold))
        
        ph_icon = QLabel("🧪")
        ph_icon.setFont(QFont("Arial", 24))
        ph_icon.setStyleSheet("color: #00c4a7;")
        
        ph_title_button = QPushButton("Water and pH")
        ph_title_button.setFont(QFont("Arial", 12))
        ph_title_button.clicked.connect(lambda: self.open_dashboard(Water_pH_Dashboard))
        ph_layout.addWidget(ph_title_button)
        
        ph_subtitle = QLabel("Water pH level")
        ph_subtitle.setFont(QFont("Arial", 8))
        ph_subtitle.setStyleSheet("color: #888;")
        
        ph_header = QHBoxLayout()
        ph_header.addWidget(self.ph_value)
        ph_header.addStretch()
        ph_header.addWidget(ph_icon)
        
        ph_layout.addLayout(ph_header)
        ph_layout.addWidget(ph_title_button)
        ph_layout.addWidget(ph_subtitle)

        # Lighting Card
        lighting_card = QFrame()
        lighting_card.setFrameShape(QFrame.StyledPanel)
        lighting_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        lighting_layout = QVBoxLayout(lighting_card)

        self.lighting_value = QLabel("60.5%")
        self.lighting_value.setFont(QFont("Arial", 28, QFont.Bold))

        lighting_icon = QLabel("💡")
        lighting_icon.setFont(QFont("Arial", 24))
        lighting_icon.setStyleSheet("color: #f1c40f;")

        lighting_title_button = QPushButton("Lighting Control")
        lighting_title_button.setFont(QFont("Arial", 12))
        lighting_title_button.clicked.connect(lambda: self.open_dashboard(Lighting_Dashboard))

        lighting_subtitle = QLabel("Lighting Status")
        lighting_subtitle.setFont(QFont("Arial", 8))
        lighting_subtitle.setStyleSheet("color: #888;")

        lighting_header = QHBoxLayout()
        lighting_header.addWidget(self.lighting_value)
        lighting_header.addStretch()
        lighting_header.addWidget(lighting_icon)

        lighting_layout.addLayout(lighting_header)
        lighting_layout.addWidget(lighting_title_button)
        lighting_layout.addWidget(lighting_subtitle)

        # Control Card
        control_card = QFrame()
        control_card.setFrameShape(QFrame.StyledPanel)
        control_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        control_layout = QVBoxLayout(control_card)
        
        control_icon = QLabel("⏻")
        control_icon.setFont(QFont("Arial", 24))
        control_icon.setStyleSheet("color: #00c4a7;")
        control_icon.setAlignment(Qt.AlignCenter)
        
        quick_control_btn = QPushButton("Exit")
        quick_control_btn.clicked.connect(app.quit)

        control_layout.addWidget(control_icon)
        control_layout.addWidget(quick_control_btn)
        
        # Add all cards to the layout
        cards_layout.addWidget(moisture_card)
        cards_layout.addWidget(temp_card)
        cards_layout.addWidget(humidity_card)
        cards_layout.addWidget(ph_card)
        cards_layout.addWidget(lighting_card)
        cards_layout.addWidget(control_card)
        
        self.main_layout.addLayout(cards_layout)
        
    def setup_charts_section(self):
        charts_container = QFrame()
        charts_container.setFrameShape(QFrame.StyledPanel)
        charts_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        charts_layout = QVBoxLayout(charts_container)
    
        # Chart title
        chart_title = QLabel("Daily Summary")
        chart_title.setFont(QFont("Arial", 16, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        charts_layout.addWidget(chart_title)
    
        # Chart tabs
        chart_tabs = QTabWidget()
        chart_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #f5f7fa;
                border: 1px solid #e0e0e0;
                padding: 6px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
    
        # Temperature chart
        temp_chart_widget = QWidget()
        temp_chart_layout = QVBoxLayout(temp_chart_widget)
        self.temp_canvas = MplCanvas(width=12, height=5, dpi=100)
        temp_chart_layout.addWidget(self.temp_canvas)
    
        # Humidity chart
        humidity_chart_widget = QWidget()
        humidity_chart_layout = QVBoxLayout(humidity_chart_widget)
        self.humidity_canvas = MplCanvas(width=12, height=5, dpi=100)
        humidity_chart_layout.addWidget(self.humidity_canvas)
    
        # Soil moisture chart
        moisture_chart_widget = QWidget()
        moisture_chart_layout = QVBoxLayout(moisture_chart_widget)
        self.moisture_canvas = MplCanvas(width=12, height=5, dpi=100)
        moisture_chart_layout.addWidget(self.moisture_canvas)
    
        # Add tabs
        chart_tabs.addTab(temp_chart_widget, "Temperature")
        chart_tabs.addTab(humidity_chart_widget, "Humidity")
        chart_tabs.addTab(moisture_chart_widget, "Soil Moisture")
    
        # Center the tabs
        centered_tabs_layout = QHBoxLayout()
        centered_tabs_layout.addStretch()
        centered_tabs_layout.addWidget(chart_tabs)
        centered_tabs_layout.addStretch()
    
        # Add to charts layout
        charts_layout.addLayout(centered_tabs_layout)
    
        self.main_layout.addWidget(charts_container)
    
        # Initial chart drawing
        self.update_charts()
        
    def setup_control_panel(self):
        control_container = QFrame()
        control_container.setFrameShape(QFrame.StyledPanel)
        control_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        control_layout = QGridLayout(control_container)
        
        # Light control
        light_btn = QPushButton("Lighting: OFF")
        light_btn.clicked.connect(self.toggle_light)
        
        # Watering control
        water_btn = QPushButton("Watering: OFF")
        water_btn.clicked.connect(self.toggle_watering)
        
        # Humidifier control
        humidifier_btn = QPushButton("Humidifier: OFF")
        humidifier_btn.clicked.connect(self.toggle_humidifier)
        
        # Heater control
        heater_btn = QPushButton("Heating: OFF")
        heater_btn.clicked.connect(self.toggle_heater)               

        # Water Pump control
        water_pump_btn = QPushButton("Water Pump: OFF")
        water_pump_btn.clicked.connect(self.toggle_pump_water)    

        # Auto climate control
        climate_btn = QPushButton("Auto Climate: OFF")
        climate_btn.clicked.connect(self.toggle_auto_climate)
        
        # Add buttons to grid
        control_layout.addWidget(light_btn, 0, 0)
        control_layout.addWidget(water_btn, 0, 1)
        control_layout.addWidget(humidifier_btn, 0, 2)
        control_layout.addWidget(heater_btn, 1, 0)
        control_layout.addWidget(water_pump_btn, 1, 1)
        control_layout.addWidget(climate_btn,1, 2)
        
        self.light_btn = light_btn
        self.water_btn = water_btn
        self.humidifier_btn = humidifier_btn
        self.heater_btn = heater_btn
        self.water_pump_btn = water_pump_btn
        self.climate_btn = climate_btn
        
        self.main_layout.addWidget(control_container)

    def toggle_light(self):
        self.light_status = not self.light_status
        if self.light_status:
            self.light_btn.setText("Lighting: ON")
            self.light_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.light_btn.setText("Lighting: OFF")
            self.light_btn.setStyleSheet("background-color: #00c4a7; color: white;")
        
    def toggle_watering(self):
        self.watering_status = not self.watering_status
        if self.watering_status:
            self.water_btn.setText("Watering: ON")
            self.water_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.water_btn.setText("Watering: OFF")
            self.water_btn.setStyleSheet("background-color: #00c4a7; color: white;")
            
    def toggle_humidifier(self):
        self.humidifier_status = not self.humidifier_status
        if self.humidifier_status:
            self.humidifier_btn.setText("Humidifier: ON")
            self.humidifier_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.humidifier_btn.setText("Humidifier: OFF")
            self.humidifier_btn.setStyleSheet("background-color: #00c4a7; color: white;")
            
    def toggle_heater(self):
        self.heater_status = not self.heater_status
        if self.heater_status:
            self.heater_btn.setText("Heating: ON")
            self.heater_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.heater_btn.setText("Heating: OFF")
            self.heater_btn.setStyleSheet("background-color: #00c4a7; color: white;")

    def toggle_pump_water(self):
        self.pump_water_status = not self.pump_water_status
        if self.pump_water_status:
            self.water_pump_btn.setText("Water Pump: ON")
            self.water_pump_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.water_pump_btn.setText("Water Pump: OFF")
            self.water_pump_btn.setStyleSheet("background-color: #00c4a7; color: white;")

    def toggle_auto_climate(self):
        self.auto_climate_active = not getattr(self, 'auto_climate_active', False)
        if self.auto_climate_active:
            self.climate_btn.setText("Auto Climate: ON")
            self.climate_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.climate_btn.setText("Auto Climate: OFF")
            self.auto_climate_temperature = False
            self.auto_climate_lighting = False
            self.auto_climate_humidity = False
            self.auto_climate_soil = False
            self.auto_climate_water = False
            self.climate_btn.setStyleSheet("background-color: #00c4a7; color: white;")

    def update_sensor_data(self):
        temp_test_value, soil_moisture_value, humidity_test_value = read_sensor()
        self.moisture = soil_moisture_value
        self.moisture_value.setText(f"{self.moisture}")
        self.moisture_history.append(self.moisture)
        self.moisture_history = self.moisture_history[-24:]

        self.temperature = temp_test_value
        self.temp_value.setText(f"{self.temperature}")
        self.temp_history.append(self.temperature)
        self.temp_history = self.temp_history[-24:]
        self.set_warning(self.temperature, self.target_heat, "Temperature is too low! Please take action.", "red")

        self.humidity = humidity_test_value
        self.humidity_value.setText(f"{self.humidity}%")
        self.humidity_history.append(self.humidity)
        self.humidity_history = self.humidity_history[-24:]

        self.ph = round(random.uniform(5.5, 6.2), 1)
        self.ph_value.setText(f"{self.ph}")
        self.ph_history.append(self.ph)
        self.ph_history = self.ph_history[-24:]
        
        # # Water level update (range 0–100%)
        # self.water_level = round(random.uniform(30, 80), 1)
        # self.water_value.setText(f"{self.water_level}%")
        # self.water_history.append(self.water_level)
        # self.water_history = self.water_history[-24:]

        # Light level update (range 200–1000 lux)
        self.light_level = round(random.uniform(30, 50), 0)
        self.lighting_value.setText(f"{self.light_level}%")
        self.light_history.append(self.light_level)
        self.light_history = self.light_history[-24:]

        self.send_status_to_raspberry({
                "HEATING": self.heater_status,
                "WATERING": self.watering_status,
                "HUMIDIFIER": self.humidifier_status,
                "WATER_PUMP": self.pump_water_status,
                "LIGHTNING": self.light_status
            })
        # Update charts
        self.update_charts()
        dashboards = {
            "temperature": (Temperature_Dashboard, "manage_climate_control", "auto_climate_temperature"),
            "humidity": (Humidity_Dashboard, "manage_climate_control", "auto_climate_humidity"),
            "soil": (Soil_moisture_Dashboard, "manage_irrigation_control", "auto_climate_soil"),
            "water": (Water_pH_Dashboard, "manage_water_control", "auto_climate_water"),
            "lighting": (Lighting_Dashboard, "manage_light_control", "auto_climate_lighting")
        }
        instances = {}

        for key, (DashboardClass, _, _) in dashboards.items():
            instances[key] = DashboardClass(back_to_main=self.show, main_system=self)

        if self.auto_climate_active:
            for key, (_, method_name, _) in dashboards.items():
                getattr(instances[key], method_name)()

        for key, (_, method_name, flag_name) in dashboards.items():
            if getattr(self, flag_name, False):
                getattr(instances[key], method_name)()

    def update_charts(self):
        # Temperature chart
        self.temp_canvas.ax.clear()
        hours = range(24)
        self.temp_canvas.ax.plot(hours, self.temp_history, 'o-', color='#00c4a7')
        self.temp_canvas.ax.fill_between(hours, self.temp_history, color='#00c4a7', alpha=0.2)
        self.temp_canvas.ax.set_ylim(15, 40)
        self.temp_canvas.ax.grid(True, linestyle='--', alpha=0.7)
        self.temp_canvas.ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
        self.temp_canvas.ax.set_xticklabels(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00'])
        self.temp_canvas.draw()
        
        # Humidity chart
        self.humidity_canvas.ax.clear()
        self.humidity_canvas.ax.plot(hours, self.humidity_history, 'o-', color='#0087c4')
        self.humidity_canvas.ax.fill_between(hours, self.humidity_history, color='#0087c4', alpha=0.2)
        self.humidity_canvas.ax.set_ylim(30, 100)
        self.humidity_canvas.ax.grid(True, linestyle='--', alpha=0.7)
        self.humidity_canvas.ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
        self.humidity_canvas.ax.set_xticklabels(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00'])
        self.humidity_canvas.draw()
        
        # Soil moisture chart
        self.moisture_canvas.ax.clear()
        self.moisture_canvas.ax.plot(hours, self.moisture_history, 'o-', color='#8c00c4')
        self.moisture_canvas.ax.fill_between(hours, self.moisture_history, color='#8c00c4', alpha=0.2)
        self.moisture_canvas.ax.set_ylim(50, 100)
        self.moisture_canvas.ax.grid(True, linestyle='--', alpha=0.7)
        self.moisture_canvas.ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
        self.moisture_canvas.ax.set_xticklabels(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:00'])
        self.moisture_canvas.draw()
        


    def set_warning(self, sensor, value, message, color):
        current_time = time.time()
        if sensor < value and not self.warning_dialog_open and (current_time - self.last_warning_time) >= 15:
            self.show_yellow_warning(color, message)
            self.last_warning_time = current_time

    def warning_closed(self):
        self.warning_dialog_open = False
    
    def show_yellow_warning(self, color, message):
        self.warning_dialog = RoundedWarningDialog(self, color=color)
        self.warning_dialog.set_message(message)

        self.warning_dialog.setWindowModality(Qt.ApplicationModal)
        self.warning_dialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

        self.warning_dialog_open = True

        self.warning_dialog.finished.connect(self.warning_closed)
        self.warning_dialog.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgriculturalMonitoringSystem()
    window.showFullScreen()
    sys.exit(app.exec_())