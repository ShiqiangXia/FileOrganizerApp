# -*- coding: utf-8 -*-
# file_organizer/app.py

"""This module provides the file organizer application."""

import sys

from PyQt5.QtWidgets import QApplication

from .views import Window


def main():
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())