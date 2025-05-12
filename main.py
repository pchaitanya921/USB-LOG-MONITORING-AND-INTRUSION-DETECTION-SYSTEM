#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
USB Monitoring System - Desktop Application
Main entry point for the application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.utils.config import load_config

def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("USB Monitoring System")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "assets", "icons", "usb_monitor.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Load configuration
    config = load_config()

    # Create and show main window
    window = MainWindow(config)
    window.show()

    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
