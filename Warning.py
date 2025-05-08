from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QHBoxLayout)
from PyQt5.QtGui import QFont, QColor, QPainterPath, QPainter, QBrush
from PyQt5.QtCore import Qt, QRectF
import sys

class RoundedWarningDialog(QDialog):
    def __init__(self, back_to_main, color="yellow"):
        super().__init__()
        self.back_to_main = back_to_main
        # Set window properties
        self.setWindowTitle("")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 280)
        
        # Set the main color
        if color.lower() == "yellow":
            self.main_color = "#FFBE0B"
            self.button_color = "#FF3A5E"
            self.icon_color = "#FF3A5E"
        else:
            self.main_color = "#FF3A5E"
            self.button_color = "#FFBE0B"
            self.icon_color = "#FFBE0B"
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the content widget with rounded corners and shadow
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setStyleSheet(f"""
            QWidget#contentWidget {{
                background-color: {self.main_color};
                border-radius: 20px;
            }}
        """)
        
        # Content layout
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 80, 20, 20)
        
        # Warning header
        warning_header = QLabel("Warning!")
        warning_header.setStyleSheet(f"""
            color: #1D3557;
            font-size: 28px;
            font-weight: bold;
            margin-top: 10px;
        """)
        warning_header.setAlignment(Qt.AlignCenter)
        
        # Message box (white rounded area)
        message_widget = QWidget()
        message_widget.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 10px;
        """)
        message_layout = QVBoxLayout(message_widget)
        
        # Message text
        self.message_label = QLabel("Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt")
        self.message_label.setStyleSheet("""
            color: #333;
            font-size: 14px;
            padding: 15px;
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        
        # OK button container (for centering)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(80, 40)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.button_color};
                color: white;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.button_color}DD;
            }}
            QPushButton:pressed {{
                background-color: {self.button_color}AA;
            }}
        """)
        ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(ok_button, 0, Qt.AlignCenter)
        
        # Add message and button to message box
        message_layout.addWidget(self.message_label)
        message_layout.addWidget(button_container)
        
        # Close button (X in circle)
        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1D3557;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2A4A6A;
            }
        """)
        close_button.clicked.connect(self.accept)
        
        # Position close button at top right
        close_button_container = QWidget(self)
        close_button_container.setFixedSize(self.width(), self.height())
        close_button_container.move(0, 0)
        
        close_layout = QHBoxLayout(close_button_container)
        close_layout.setContentsMargins(0, 15, 30, 0)
        close_layout.addStretch()
        close_layout.addWidget(close_button, 0, Qt.AlignTop | Qt.AlignRight)
        
        # Warning icon
        icon_widget = QWidget(self)
        icon_widget.setFixedSize(self.width(), 80)
        icon_widget.move(0, 0)
        
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom warning icon (circle with exclamation)
        warning_icon = QLabel()
        warning_icon.setFixedSize(80, 80)
        warning_icon.setStyleSheet(f"""
            background-color: {self.icon_color};
            border-radius: 40px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 40px;
            border: 4px solid white;
        """)
        warning_icon.setAlignment(Qt.AlignCenter)
        warning_icon.setText("!")
        
        icon_layout.addWidget(warning_icon, 0, Qt.AlignHCenter)
        
        # Add everything to main content
        content_layout.addWidget(warning_header)
        content_layout.addWidget(message_widget)
        
        # Add content to main layout
        main_layout.addWidget(self.content_widget)
        
    def set_message(self, message):
        self.message_label.setText(message)
        
    def paintEvent(self, event):
        # Add shadow effect
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(QRectF(5, 5, self.width()-10, self.height()-10), 20, 20)
        
        painter.fillPath(shadow_path, QColor(0, 0, 0, 30))
