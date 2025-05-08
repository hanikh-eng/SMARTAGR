import os
import sys
import random
from datetime import datetime, timedelta
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, 
                             QGridLayout, QTabWidget, QGroupBox, QProgressBar,
                             QSlider, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (QFont, QPixmap)
import pyqtgraph as pg


class Water_pH_Dashboard(QMainWindow):
    def __init__(self, back_to_main, main_system=None):
        super().__init__()

        self.back_to_main = back_to_main
        self.main_system = main_system

        self.setWindowTitle("Agriculture Monitoring Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # Initialize data
        self.water_level = 65.4
        self.target_water_level = self.main_system.target_water_level
        self.pump_on = self.main_system.pump_water_status
        self.auto_climate_active = self.main_system.auto_climate_active | self.main_system.auto_climate_water
        self.ph_level = self.main_system.ph
        
        # Generate time points for last 24 hours
        self.time_points = [datetime.now() - timedelta(hours=24-i) for i in range(25)]
        self.time_axis = [t.strftime('%H:%M') for t in self.time_points]
        
        # Generate sample data
        self.water_level_data = self.generate_water_level_data()
        self.ph_level_data = self.generate_ph_level_data()
        
        # Setup UI
        self.initUI()
        
        # Start timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(1000)
        
    def initUI(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QGridLayout(central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Dashboard title
        title_label = QLabel("Agriculture Monitoring Dashboard")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #444;")
        self.main_layout.addWidget(title_label, 0, 0, 1, 1)
        
        # Show current date
        self.current_date = datetime.now().strftime("Thursday, April 17, 2025")
        self.date_label = QLabel(self.current_date)
        self.date_label.setAlignment(Qt.AlignRight)
        self.date_label.setStyleSheet("font-size: 14px; color: #555;")
        self.main_layout.addWidget(self.date_label, 0, 1, 1, 1, Qt.AlignRight)
        
        # Create metrics cards
        self.create_metrics_section()
        
        # Create water level control section
        self.create_water_level_control_section()
        
        # Create daily summary section
        self.create_summary_section()
        
        # Create graph section
        self.create_graph_section()
        
        # Create users section
        # self.create_users_section()
        
    def create_metrics_section(self):
        # Create metrics grid
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("background-color: transparent;")
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setSpacing(15)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "logo.png")
        pixmap = QPixmap(image_path)
        Project_icon = QLabel()
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        Project_icon.setPixmap(pixmap)
        Project_icon.setAlignment(Qt.AlignCenter)
        metrics_layout.addWidget(Project_icon)

        # Water Level Card
        self.water_level_card = self.create_metric_card(
            "Water Level", 
            self.water_level, 
            "Water Level",
            "%", 
            "#4ECDC4"
        )
        metrics_layout.addWidget(self.water_level_card)
        
        # Target Water Level Card
        self.target_water_level_card = self.create_metric_card(
            "Target Water Level", 
            self.target_water_level, 
            "Set Water Level",
            "%", 
            "#3498db"
        )
        metrics_layout.addWidget(self.target_water_level_card)
        
        # pH Level Card
        self.ph_level_card = self.create_metric_card(
            "pH Level", 
            self.ph_level, 
            "Water pH",
            "pH", 
            "#8E44AD"
        )
        metrics_layout.addWidget(self.ph_level_card)
        
        # Quick Controls Card
        controls_card = QFrame()
        controls_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        controls_layout = QVBoxLayout(controls_card)

        self.buntton_status()

        controls_layout.addWidget(QLabel("Quick Controls"))
        controls_layout.addWidget(self.power_btn)

        self.buntton_auto_status()
        
        controls_layout.addWidget(self.auto_climate_btn)

        home_icon = QLabel("⏻")
        home_icon.setFont(QFont("Arial", 24))
        home_icon.setStyleSheet("color: #00c4a7;")
        home_icon.setAlignment(Qt.AlignCenter)
        
        self.quick_home_btn = QPushButton("Home")
        self.quick_home_btn.setStyleSheet("""
            QPushButton {
                background-color: #00c4a7;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b39f;
            }
        """)
        self.quick_home_btn.clicked.connect(self.go_back)
        
        controls_layout.addWidget(home_icon)
        controls_layout.addWidget(self.quick_home_btn)
        
        controls_layout.addStretch()
        metrics_layout.addWidget(controls_card)
        
        self.main_layout.addWidget(metrics_frame, 1, 0, 1, 2)

    def go_back(self):
        self.back_to_main()
        self.close()    

    def create_water_level_control_section(self):
        # Create water level control frame
        water_level_control_frame = QFrame()
        water_level_control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        water_level_control_layout = QVBoxLayout(water_level_control_frame)
        
        # Water level slider title
        water_level_slider_title = QLabel("Water Level Control")
        water_level_slider_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #444;")
        water_level_control_layout.addWidget(water_level_slider_title)
        
        # Water level slider with value display
        slider_value_layout = QHBoxLayout()
        
        # Create the slider
        self.water_level_slider = QSlider(Qt.Horizontal)
        self.water_level_slider.setRange(300, 900)
        self.water_level_slider.setValue(int(self.target_water_level * 10))
        self.water_level_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4ECDC4;
                border: 2px solid #2c7873;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4ECDC4, stop:1 #2c7873);
                border-radius: 4px;
            }
        """)
        self.water_level_slider.valueChanged.connect(self.update_target_water_level)
        slider_value_layout.addWidget(self.water_level_slider)
        
        # Display current slider value
        self.slider_value_label = QLabel(f"{self.target_water_level}%")
        self.slider_value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ECDC4; min-width: 60px;")
        slider_value_layout.addWidget(self.slider_value_label)
        
        water_level_control_layout.addLayout(slider_value_layout)
        
        # Add water level presets
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        
        preset_water_levels = [("Low", 40.0), ("Medium", 60.0), ("High", 80.0)]
        
        for name, water_level in preset_water_levels:
            preset_btn = QPushButton(f"{name} ({water_level}%)")
            preset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            preset_btn.clicked.connect(lambda _, h=water_level: self.set_preset_water_level(h))
            presets_layout.addWidget(preset_btn)
        
        water_level_control_layout.addLayout(presets_layout)
        
        # Add to main layout
        self.main_layout.addWidget(water_level_control_frame, 2, 0, 1, 1)
        
    def create_graph_section(self):
        # Create Tab Widget for graphs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """)
        
        # Water Level Tab
        water_level_tab = QWidget()
        water_level_layout = QVBoxLayout(water_level_tab)
        self.water_level_graph = self.create_graph("Water Level (%)")
        self.update_water_level_graph(self.water_level_graph, self.water_level_data, '#4ECDC4')
        water_level_layout.addWidget(self.water_level_graph)
        
        # pH Level Tab
        ph_level_tab = QWidget()
        ph_level_layout = QVBoxLayout(ph_level_tab)
        self.ph_level_graph = self.create_graph("pH Level")
        self.update_ph_level_graph(self.ph_level_graph, self.ph_level_data, '#e74c3c')
        ph_level_layout.addWidget(self.ph_level_graph)
        
        # Add tabs to widget
        self.tab_widget.addTab(water_level_tab, "Water Level")
        self.tab_widget.addTab(ph_level_tab, "pH Level")
        
        # Add graph section to main layout
        self.main_layout.addWidget(self.tab_widget, 3, 0, 1, 2)
        
    def create_summary_section(self):
        # Daily summary label
        summary_label = QLabel("Daily Summary")
        summary_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #444; margin-top: 10px;")
        
        # Add actual summary content
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        self.summary_text = QLabel(f"Today's average water level: 62.8%\nTarget water level: {self.target_water_level}%\nPump status: Normal\nAverage pH level: {self.ph_level}\nSystem health: Optimal")
        self.summary_text.setStyleSheet("font-size: 14px; color: #555;")
        summary_layout.addWidget(self.summary_text)
        
        self.main_layout.addWidget(summary_label, 2, 1, 1, 1)
        self.main_layout.addWidget(summary_frame, 2, 1, 1, 1)
        
    def create_users_section(self):
        users_frame = QFrame()
        users_frame.setMaximumWidth(280)
        users_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        users_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                padding: 10px;
            }
        """)

        users_layout = QVBoxLayout(users_frame)
        users_layout.setContentsMargins(0, 0, 0, 0)
        users_layout.setSpacing(10)

        # Add a title with better styling
        users_title = QLabel("Active Users")
        users_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 5px 0;
                border-bottom: 1px solid #eee;
            }
        """)
        users_title.setAlignment(Qt.AlignCenter)
        users_layout.addWidget(users_title)

        # Sample user data
        users = [
            {"name": "Harold", "last_active": "6 hours ago", "joined": "September 7, 2019"},
            {"name": "Hanzo Miguel", "last_active": "7 hours ago", "joined": "September 7, 2019"},
            {"name": "Hendrix Michael", "last_active": "12 hours ago", "joined": "September 7, 2019"}
        ]

        for user in users:
            user_card = QFrame()
            user_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    padding: 12px;
                    border: 1px solid #e0e0e0;
                }
                QFrame:hover {
                    border: 1px solid #c0c0c0;
                    background-color: #f9f9f9;
                }
            """)

            user_layout = QHBoxLayout(user_card)
            user_layout.setContentsMargins(5, 5, 5, 5)
            user_layout.setSpacing(12)

            # Avatar with better styling
            avatar = QLabel("👤")
            avatar.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    padding: 5px;
                }
            """)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setFixedSize(40, 40)
            user_layout.addWidget(avatar)

            # User info with better organization
            info_layout = QVBoxLayout()
            info_layout.setSpacing(4)

            name_label = QLabel(user["name"])
            name_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #333;
                }
            """)

            last_active = QLabel(f"Last active: {user['last_active']}")
            last_active.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 11px;
                }
            """)

            joined = QLabel(f"Joined: {user['joined']}")
            joined.setStyleSheet("""
                QLabel {
                    color: #888;
                    font-size: 11px;
                    font-style: italic;
                }
            """)

            info_layout.addWidget(name_label)
            info_layout.addWidget(last_active)
            info_layout.addWidget(joined)
            user_layout.addLayout(info_layout)

            users_layout.addWidget(user_card)

        users_layout.addStretch()
        self.main_layout.addWidget(users_frame, 2, 2, 2, 1)
    
    def create_metric_card(self, title, value, subtitle, icon, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        # Value and icon in horizontal layout
        value_layout = QHBoxLayout()
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        value_layout.addWidget(value_label)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        value_layout.addWidget(icon_label, alignment=Qt.AlignRight)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; color: #888;")
        
        layout.addLayout(value_layout)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_graph(self, title):
        graph = pg.PlotWidget()
        graph.setBackground('w')
        graph.showGrid(x=True, y=True, alpha=0.3)
        graph.setTitle(title)
        graph.setLabel('left', 'Value')
        graph.setLabel('bottom', 'Time')

        # Disable all mouse interactions
        graph.setMouseEnabled(x=False, y=False)
        graph.setMenuEnabled(False)

        # Set the x-axis to display time values
        axis = graph.getAxis('bottom')
        axis.setTicks([[(i, self.time_axis[i]) for i in range(0, len(self.time_axis), 4)]])
        
        return graph
    
    def update_water_level_graph(self, graph, data, color):
        # Clear the graph
        graph.clear()
        
        # Plot data line
        pen = pg.mkPen(color=color, width=3)
        graph.plot(list(range(len(data))), data, pen=pen)
        
        # Add fill under the line
        fill = pg.FillBetweenItem(
            pg.PlotCurveItem(list(range(len(data))), data, pen=pen),
            pg.PlotCurveItem(list(range(len(data))), [0] * len(data)),
            brush=pg.mkBrush(color + '50')
        )
        graph.addItem(fill)
        
        # Add target water level line
        target_pen = pg.mkPen(color='#2980b9', width=2, style=Qt.DashLine)
        target_line = pg.InfiniteLine(pos=self.target_water_level, angle=0, pen=target_pen, 
                                       label=f'Target: {self.target_water_level}%', 
                                       labelOpts={'color': '#2980b9', 'position': 0.95})
        graph.addItem(target_line)
        
    def update_ph_level_graph(self, graph, data, color):
        # Clear the graph
        graph.clear()
        
        # Plot data line
        pen = pg.mkPen(color=color, width=3)
        graph.plot(list(range(len(data))), data, pen=pen)
        
        # Add fill under the line
        fill = pg.FillBetweenItem(
            pg.PlotCurveItem(list(range(len(data))), data, pen=pen),
            pg.PlotCurveItem(list(range(len(data))), [0] * len(data)),
            brush=pg.mkBrush(color + '50')
        )
        graph.addItem(fill)
        
        # Add optimal pH range lines
        optimal_min_pen = pg.mkPen(color='#27ae60', width=2, style=Qt.DashLine)
        optimal_min_line = pg.InfiniteLine(pos=6.5, angle=0, pen=optimal_min_pen, 
                                           label='Min Optimal: 6.5', 
                                           labelOpts={'color': '#27ae60', 'position': 0.95})
        graph.addItem(optimal_min_line)
        
        optimal_max_pen = pg.mkPen(color='#27ae60', width=2, style=Qt.DashLine)
        optimal_max_line = pg.InfiniteLine(pos=7.5, angle=0, pen=optimal_max_pen, 
                                           label='Max Optimal: 7.5', 
                                           labelOpts={'color': '#27ae60', 'position': 0.95})
        graph.addItem(optimal_max_line)
    
    def generate_water_level_data(self, main_system=None):
        # Generate water level pattern: fluctuating throughout the day
        base = np.sin(np.linspace(0, 2*np.pi, 25)) * 15 + 60
        # Add some randomness
        noise = np.random.normal(0, 3, 25)
        return base + noise
    
    def generate_ph_level_data(self):
        # Generate pH pattern: fluctuating around neutral (7.0)
        base = np.sin(np.linspace(0, 2*np.pi, 25)) * 0.5 + 7.0  
        # Add some randomness
        noise = np.random.normal(0, 0.2, 25)
        return base + noise
    
    def update_values(self):
        # Update water level with slight changes
        self.water_level += random.uniform(-1.0, 1.0)
        self.water_level = round(max(min(self.water_level, 90), 30), 1)
        
        # Update pH level with slight changes
        if self.main_system:
            self.ph_level = self.main_system.ph
        else:
            self.ph_level += random.uniform(-0.1, 0.1)
        self.ph_level = round(max(min(self.ph_level, 9.0), 5.0), 1)
        
        # Update cards
        self.update_cards()
        
        # Update graphs
        # Shift data and add new values
        self.water_level_data = np.roll(self.water_level_data, -1)
        self.water_level_data[-1] = self.water_level
        
        self.ph_level_data = np.roll(self.ph_level_data, -1)
        self.ph_level_data[-1] = self.ph_level
        
        # Update graph displays
        self.update_water_level_graph(self.water_level_graph, self.water_level_data, '#4ECDC4')
        self.update_ph_level_graph(self.ph_level_graph, self.ph_level_data, '#8E44AD')
        
        # Update summary text
        avg_water_level = round(np.mean(self.water_level_data), 1)
        avg_ph_level = round(np.mean(self.ph_level_data), 1)
        self.summary_text.setText(f"Today's average water level: {avg_water_level}%\n"
                                f"Target water level: {self.target_water_level}%\n"
                                f"Pump status: {'ON' if self.pump_on else 'OFF'}\n"
                                f"Average pH level: {avg_ph_level}\n"
                                f"System health: Optimal")
        
        # If auto climate is active, manage water control
        if self.auto_climate_active:
            self.manage_water_control()
        
    def update_cards(self):
        # Find the water level card value label and update it
        for i in range(self.water_level_card.layout().count()):
            item = self.water_level_card.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() != "%":
                        widget.setText(str(self.water_level))
                        break
                        
        # Find the target water level card value label and update it
        for i in range(self.target_water_level_card.layout().count()):
            item = self.target_water_level_card.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() != "%":
                        widget.setText(str(self.target_water_level))
                        break
                        
        # Find the pH level card value label and update it
        for i in range(self.ph_level_card.layout().count()):
            item = self.ph_level_card.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() != "pH":
                        widget.setText(str(self.ph_level))
                        break

    def buntton_status(self):
        # Power button
        if self.pump_on:
            self.power_btn = QPushButton("💧 Water Pump ON")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.power_btn.clicked.connect(self.toggle_pump)
        # Power button
        else:
            self.power_btn = QPushButton("💧 Water Pump OFF")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #16a085;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1abc9c;
                }
            """)
            self.power_btn.clicked.connect(self.toggle_pump)


    def toggle_pump(self):
        self.pump_on = not self.pump_on
        if self.pump_on:
            self.power_btn.setText("💧 Pump Water ON")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.main_system.pump_water_status = False
            self.main_system.toggle_pump_water()
        else:
            self.power_btn.setText("💧 Pump Water OFF")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #16a085;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1abc9c;
                }
            """)
            self.main_system.pump_water_status = True
            self.main_system.toggle_pump_water()

    def toggle_auto_climate(self):
        self.auto_climate_active = not self.auto_climate_active
        if self.auto_climate_active:
            self.auto_climate_btn.setText("Auto Climate: ON")
            self.auto_climate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.main_system.auto_climate_water = True
        else:
            self.auto_climate_btn.setText("Auto Climate: OFF")
            self.auto_climate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
            self.main_system.auto_climate_water = False


    def buntton_auto_status(self):
        # Power button
        if self.auto_climate_active :
        # Auto Climate button
            self.auto_climate_btn = QPushButton("Auto Climate: ON")
            self.auto_climate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.auto_climate_btn.clicked.connect(self.toggle_auto_climate)
        # Power button
        else:
            self.auto_climate_btn = QPushButton("Auto Climate: OFF")
            self.auto_climate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
            self.auto_climate_btn.clicked.connect(self.toggle_auto_climate)

    def update_target_water_level(self):
        self.target_water_level = round(self.water_level_slider.value() / 10, 1)
        self.slider_value_label.setText(f"{self.target_water_level}%")
        self.main_system.target_water_level = self.target_water_level
        
        # Update target water level card
        self.update_cards()
        
        # Update graph to show new target line
        self.update_water_level_graph(self.water_level_graph, self.water_level_data, '#4ECDC4')
        
        # If auto climate is active, check if pump needs adjustment
        if self.auto_climate_active:
            self.manage_water_control()

    def set_preset_water_level(self, water_level):
        self.water_level_slider.setValue(int(water_level * 10))

    def manage_water_control(self):
        # Auto-manage pump based on target water level
        if self.water_level < (self.target_water_level - 5.0) and not self.pump_on:
            self.toggle_pump()
        elif self.water_level > (self.target_water_level + 5.0) and self.pump_on:
            self.toggle_pump()
