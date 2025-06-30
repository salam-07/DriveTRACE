import sys
import os
from Simulation import config
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt

BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Simulation/Assets/ui/bg.jpg")
MAIN_PY_PATH = os.path.join(os.path.dirname(__file__), "Simulation/main.py")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Get screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        # Maintain aspect ratio (1248:936)
        aspect_ratio = 1248 / 936
        window_height = int(screen_height * 0.94)
        window_width = int(window_height * aspect_ratio)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(window_width, window_height)
        # Center the window on the screen
        qr = self.frameGeometry()
        cp = screen.geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Set background image
        if os.path.exists(BG_IMAGE_PATH):
            palette = QPalette()
            pixmap = QPixmap(BG_IMAGE_PATH).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)

        # Launch Simulation Button
        self.launch_btn = QPushButton("Launch Simulation", self)
        self.launch_btn.setGeometry(int((window_width-600)/2), 140, 600, 110)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,30,1.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 34px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(200,200,200,0.8);
                color = black;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_simulation)

        # Quit Button just below the launch button
        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setGeometry(int((window_width-600)/2), 270, 600, 110)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,30,1.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 34px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(200,0,0,0.8);
            }
        """)
        self.quit_btn.clicked.connect(self.close)

    def launch_simulation(self):
        # Run main.py as a subprocess (cross-platform, safe)
        import subprocess
        python_exe = sys.executable
        subprocess.Popen([python_exe, MAIN_PY_PATH], shell=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())