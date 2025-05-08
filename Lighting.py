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


class Lighting_Dashboard(QMainWindow):
    def __init__(self, back_to_main, main_system=None):
        super().__init__()

        self.back_to_main = back_to_main
        self.main_system = main_system

        self.setWindowTitle("Agriculture Monitoring Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # Initialize data
        self.light_intensity = self.main_system.light_level
        self.target_light = self.main_system.target_light
        self.grow_lights_on = self.main_system.light_status
        self.auto_climate_active = self.main_system.auto_climate_active | self.main_system.auto_climate_lighting
        
        # Generate time points for last 24 hours
        self.time_points = [datetime.now() - timedelta(hours=24-i) for i in range(25)]
        self.time_axis = [t.strftime('%H:%M') for t in self.time_points]
        
        # Generate sample data
        self.light_data = self.generate_light_data()
        
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
        
        # Create light intensity control section
        self.create_light_control_section()
        
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

        # Light Intensity Card
        self.light_card = self.create_metric_card(
            "Light Intensity", 
            self.light_intensity, 
            "Current Light",
            "%", 
            "#FFD700"
        )
        metrics_layout.addWidget(self.light_card)
        
        # Target Light Card
        self.target_light_card = self.create_metric_card(
            "Target Light", 
            self.target_light, 
            "Set Light",
            "%", 
            "#FF8C00"
        )
        metrics_layout.addWidget(self.target_light_card)
        
        self.buntton_status()

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

    def buntton_status(self):
        # Power button
        if self.grow_lights_on :
            self.power_btn = QPushButton("💡 Grow Lights ON")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            self.power_btn.clicked.connect(self.toggle_grow_lights)
        # Power button
        else:
            self.power_btn = QPushButton("💡 Grow Lights OFF")
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
            self.power_btn.clicked.connect(self.toggle_grow_lights)

    def go_back(self):
        self.back_to_main()
        self.close()    

    def create_light_control_section(self):
        # Create light control frame
        light_control_frame = QFrame()
        light_control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        light_control_layout = QVBoxLayout(light_control_frame)
        
        # Light slider title
        light_slider_title = QLabel("Light Intensity Control")
        light_slider_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #444;")
        light_control_layout.addWidget(light_slider_title)
        
        # Light slider with value display
        slider_value_layout = QHBoxLayout()
        
        # Create the slider
        self.light_slider = QSlider(Qt.Horizontal)
        self.light_slider.setRange(100, 1000)
        self.light_slider.setValue(int(self.target_light * 10))
        self.light_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                border: 2px solid #FF8C00;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #FF8C00);
                border-radius: 4px;
            }
        """)
        self.light_slider.valueChanged.connect(self.update_target_light)
        slider_value_layout.addWidget(self.light_slider)
        
        # Display current slider value
        self.slider_value_label = QLabel(f"{self.target_light}%")
        self.slider_value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700; min-width: 60px;")
        slider_value_layout.addWidget(self.slider_value_label)
        
        light_control_layout.addLayout(slider_value_layout)
        
        # Add light presets
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        
        preset_lights = [("Low", 30.0), ("Medium", 60.0), ("High", 90.0)]
        
        for name, light in preset_lights:
            preset_btn = QPushButton(f"{name} ({light}%)")
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
            preset_btn.clicked.connect(lambda _, l=light: self.set_preset_light(l))
            presets_layout.addWidget(preset_btn)
        
        light_control_layout.addLayout(presets_layout)
        
        # Add to main layout
        self.main_layout.addWidget(light_control_frame, 2, 0, 1, 1)
        
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
        
        # Light Tab
        light_tab = QWidget()
        light_layout = QVBoxLayout(light_tab)
        self.light_graph = self.create_graph("Light Intensity (%)")
        self.update_graph(self.light_graph, self.light_data, '#FFD700')
        light_layout.addWidget(self.light_graph)
        
        # Add tabs to widget
        self.tab_widget.addTab(light_tab, "Light Intensity")
        
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
        
        self.summary_text = QLabel(f"Today's average light: 62.8%\nTarget light: {self.target_light}%\nGrow lights status: Normal\nSystem health: Optimal")
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
    
    def update_graph(self, graph, data, color):
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
        
        # Add target light line
        target_pen = pg.mkPen(color='#FF8C00', width=2, style=Qt.DashLine)
        target_line = pg.InfiniteLine(pos=self.target_light, angle=0, pen=target_pen, 
                                       label=f'Target: {self.target_light}%', 
                                       labelOpts={'color': '#FF8C00', 'position': 0.95})
        graph.addItem(target_line)
    
    def generate_light_data(self):
        # Generate light pattern: higher during day, lower at night
        base = np.sin(np.linspace(0, 2*np.pi, 25)) * 25 + 50
        # Add some randomness
        noise = np.random.normal(0, 3, 25)
        return base + noise
    
    def update_values(self):
        # Update light with slight changes
        if self.main_system:
            self.light_intensity = self.main_system.light_level
        else:
            self.light_intensity += random.uniform(-1.0, 1.0)

        self.light_intensity = round(max(min(self.light_intensity, 100), 10), 1)
        
        # Update cards
        self.update_cards()
        
        # Update graphs
        # Shift data and add new value
        self.light_data = np.roll(self.light_data, -1)
        self.light_data[-1] = self.light_intensity
        
        # Update graph displays
        self.update_graph(self.light_graph, self.light_data, '#FFD700')
        
        # Update summary text
        avg_light = round(np.mean(self.light_data), 1)
        self.summary_text.setText(f"Today's average light: {avg_light}%\nTarget light: {self.target_light}%\nGrow lights status: {'ON' if self.grow_lights_on else 'OFF'}\nSystem health: Optimal")
        
        # If auto climate is active, manage light control
        if self.auto_climate_active:
            self.manage_light_control()
        
    def update_cards(self):
        # Find the light card value label and update it
        for i in range(self.light_card.layout().count()):
            item = self.light_card.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() != "%":
                        widget.setText(str(self.light_intensity))
                        break
                        
        # Find the target light card value label and update it
        for i in range(self.target_light_card.layout().count()):
            item = self.target_light_card.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() != "%":
                        widget.setText(str(self.target_light))
                        break

    def setup_dashboard(self):
        dashboard = QGroupBox("Environment Monitoring")
        dashboard.setFont(QFont("Arial", 12))
        dashboard_layout = QGridLayout(dashboard)
        
        # Light indicator
        light_group = QGroupBox("Light Intensity")
        light_layout = QVBoxLayout(light_group)
        self.light_value = QLabel("65%")
        self.light_value.setFont(QFont("Arial", 24))
        self.light_value.setAlignment(Qt.AlignCenter)
        self.light_progress = QProgressBar()
        self.light_progress.setRange(0, 100)
        self.light_progress.setValue(65)
        light_layout.addWidget(self.light_value)
        light_layout.addWidget(self.light_progress)
        
        self.main_layout.addWidget(dashboard)

    def toggle_grow_lights(self):
        self.grow_lights_on = not self.grow_lights_on
        if self.grow_lights_on:
            self.power_btn.setText("💡 Grow Lights ON")
            self.power_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            self.main_system.light_status = False
            self.main_system.toggle_light()
        else:
            self.power_btn.setText("💡 Grow Lights OFF")
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
            self.main_system.light_status = True
            self.main_system.toggle_light()

    def toggle_auto_climate(self):
        self.auto_climate_active = not self.auto_climate_active
        if self.auto_climate_active:
            self.auto_climate_btn.setText("Auto Lighting: ON")
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
            self.main_system.auto_climate_lighting = True
        else:
            self.auto_climate_btn.setText("Auto Lighting: OFF")
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
            self.main_system.auto_climate_lighting = False


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


    def update_target_light(self):
        # Update target light from slider value (divide by 10 for decimal precision)
        self.target_light = round(self.light_slider.value() / 10, 1)
        self.slider_value_label.setText(f"{self.target_light}%")
        self.main_system.target_light = self.target_light
        
        # Update target light card
        self.update_cards()
        
        # Update graph to show new target line
        self.update_graph(self.light_graph, self.light_data, '#FFD700')
        
        # If auto climate is active, check if grow lights need adjustment
        if self.auto_climate_active:
            self.manage_light_control()

    def set_preset_light(self, light):
        self.light_slider.setValue(int(light * 10))

    def manage_light_control(self):
        # Auto-manage grow lights based on target light intensity
        if self.light_intensity < (self.target_light - 10.0) and not self.grow_lights_on:
            self.toggle_grow_lights()
        elif self.light_intensity > (self.target_light + 10.0) and self.grow_lights_on:
            self.toggle_grow_lights()
