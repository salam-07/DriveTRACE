from Simulation.sounds import SplashScreenSound
import sys
import os
from Simulation import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt

BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Simulation/Assets/ui/bg1.jpg")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "Docs/Images/logo2.png")
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
        aspect_ratio = 1536 / 1024
        window_height = int(screen_height * 0.95)
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

        self.placeholder_label = QLabel("© 2025 DriveTRACE. Developed by: Abdus Salam", self)
        self.placeholder_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 20px; font-family: Arial, sans-serif; font-weight: 200;")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setFixedWidth(window_width)
        self.placeholder_label.move(0, window_height - 80)

        self.launch_btn = QPushButton("Launch Simulation", self)
        self.launch_btn.setGeometry(int((window_width-600)/2), 190, 600, 110)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,30,1.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(0,80,0,0.6);
            }
        """)
        self.launch_btn.clicked.connect(self.launch_simulation)

        # Quit Button just below the launch button
        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setGeometry(int((window_width-600)/2), 320, 600, 110)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,30,1.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 30px;
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
    


from PyQt5.QtCore import QTimer, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPainter, QColor, QFont

class FadeSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self._opacity = 0.0
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFont(QFont('Segoe UI', 64, QFont.Bold))
        self.dev_font = QFont('Segoe UI', 18, QFont.Normal)
        self.text_color = QColor(255, 255, 255)
        self.dev_color = QColor(255, 255, 255, 180)

    def setOpacity(self, opacity):
        self._opacity = opacity
        self.repaint()

    def getOpacity(self):
        return self._opacity

    opacity = pyqtProperty(float, fget=getOpacity, fset=setOpacity)

    def drawContents(self, painter):
        painter.setOpacity(self._opacity)
        # Draw logo in the center
        if os.path.exists(LOGO_PATH):
            logo_pixmap = QPixmap(LOGO_PATH)
            logo_ratio = 1069 / 214
            logo_width = int(self.width() * 0.6)
            logo_height = int(logo_width / logo_ratio)
            logo_pixmap = logo_pixmap.scaled(logo_width, logo_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - logo_width) // 2
            y = (self.height() - logo_height) // 2
            painter.drawPixmap(x, y, logo_pixmap)
        # Developer text at the bottom
        painter.setFont(self.dev_font)
        painter.setPen(self.dev_color)
        painter.drawText(0, self.height() - 80, self.width(), 40, Qt.AlignCenter, "Developed by: Abdus Salam")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap())
        self.drawContents(painter)
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Play splash sound effect (ignition)
    splash_sound = SplashScreenSound()
    splash_sound.play(loops=0)

    # Splash background: solid black
    splash_width, splash_height = 1536, 1024
    splash_pix = QPixmap(splash_width, splash_height)
    splash_pix.fill(QColor(0, 0, 0))
    splash = FadeSplashScreen(splash_pix)
    splash.setFixedSize(splash_width, splash_height)
    splash.show()

    # Fade in
    fade_in = QPropertyAnimation(splash, b"opacity")
    fade_in.setDuration(800)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)

    # Fade out
    fade_out = QPropertyAnimation(splash, b"opacity")
    fade_out.setDuration(800)
    fade_out.setStartValue(1.0)
    fade_out.setEndValue(0.0)

    def show_launcher():
        splash.finish(window)
        window.show()

    def start_fade_out():
        fade_out.start()
        fade_out.finished.connect(show_launcher)

    # Launcher window
    window = MainWindow()
    # Sequence: fade in, wait, fade out
    fade_in.start()
    QTimer.singleShot(1400, start_fade_out)  # 0.8s fade in + 0.6s hold
    sys.exit(app.exec_())