#!/usr/bin/env python3
"""Quick test to verify PySide6 works on your system"""

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt, qVersion
import sys

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("PySide6 Test on Plasma/Wayland")
window.setGeometry(100, 100, 400, 200)

label = QLabel("✅ PySide6 is working!\n\nQt Version: " + qVersion())
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
label.setStyleSheet("font-size: 18px; padding: 20px;")

window.setCentralWidget(label)
window.show()

print(f"Running Qt {qVersion()} with PySide6 on Wayland")
sys.exit(app.exec())
