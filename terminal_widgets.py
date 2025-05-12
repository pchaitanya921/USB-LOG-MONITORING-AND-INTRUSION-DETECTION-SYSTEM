#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Terminal Widgets Module
Provides Termux-style terminal UI components
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette

class TerminalCard(QFrame):
    """A Termux-style terminal card widget"""
    def __init__(self, title=None, parent=None):
        super().__init__(parent)

        # Set up frame style
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

        # Set up styling
        self.setStyleSheet("""
            TerminalCard {
                background-color: #0a1520;
                border: 1px solid #00aa00;
                border-radius: 0px;
                padding: 0px;
                opacity: 1.0;
            }

            QLabel {
                font-family: 'Courier New', monospace;
                color: #00ff00;
                background-color: transparent;
            }

            QLabel#title {
                background-color: #00aa00;
                color: #000000;
                font-weight: bold;
                padding: 2px 5px;
                border: none;
            }

            QWidget#content {
                background-color: #0a1520;
                opacity: 1.0;
            }
        """)

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Add title if provided
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("title")
            self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.layout.addWidget(self.title_label)

        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.content_widget)

    def add_widget(self, widget):
        """Add a widget to the card content"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the card content"""
        self.content_layout.addLayout(layout)

class TerminalBlock(QFrame):
    """A Termux-style terminal block widget"""
    def __init__(self, title=None, parent=None):
        super().__init__(parent)

        # Set up frame style
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

        # Set up styling
        self.setStyleSheet("""
            TerminalBlock {
                background-color: #0a1520;
                border: 1px solid #00aa00;
                border-radius: 0px;
                padding: 0px;
                opacity: 1.0;
            }

            QLabel {
                font-family: 'Courier New', monospace;
                color: #00ff00;
                background-color: transparent;
            }

            QLabel#block-title {
                color: #00ff00;
                font-weight: bold;
                padding: 2px 5px;
                border-bottom: 1px solid #00aa00;
            }

            QWidget#block-content {
                background-color: #0a1520;
                opacity: 1.0;
            }
        """)

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)

        # Add title if provided
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("block-title")
            self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.layout.addWidget(self.title_label)

        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("block-content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.content_widget)

    def add_widget(self, widget):
        """Add a widget to the block content"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the block content"""
        self.content_layout.addLayout(layout)

class TerminalStatusBlock(QFrame):
    """A Termux-style status block widget"""
    def __init__(self, title, value, icon=None, parent=None):
        super().__init__(parent)

        # Set up frame style
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

        # Set up styling
        self.setStyleSheet("""
            TerminalStatusBlock {
                background-color: #0a1520;
                border: 1px solid #00aa00;
                border-radius: 0px;
                opacity: 1.0;
            }

            QLabel#status-title {
                font-family: 'Courier New', monospace;
                color: #00ff00;
                font-weight: bold;
                font-size: 12px;
                background-color: transparent;
            }

            QLabel#status-value {
                font-family: 'Courier New', monospace;
                color: #00ffaa;
                font-weight: bold;
                font-size: 18px;
                background-color: transparent;
            }
        """)

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Add title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("status-title")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Add value
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("status-value")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.value_label)

        # Set minimum size
        self.setMinimumSize(QSize(150, 80))

    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))

class TerminalButton(QPushButton):
    """A Termux-style terminal button"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # Set up styling
        self.setStyleSheet("""
            TerminalButton {
                background-color: #0a1520;
                color: #00ff00;
                border: 1px solid #00aa00;
                border-radius: 0px;
                padding: 5px 10px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }

            TerminalButton:hover {
                background-color: #00aa00;
                color: #000000;
            }

            TerminalButton:pressed {
                background-color: #008800;
                color: #000000;
            }

            TerminalButton:disabled {
                background-color: #0a1520;
                color: #005500;
                border: 1px solid #005500;
            }
        """)

class TerminalLabel(QLabel):
    """A Termux-style terminal label"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # Set up font
        font = QFont("Courier New", 9)
        self.setFont(font)

        # Set up styling
        self.setStyleSheet("""
            TerminalLabel {
                color: #00ff00;
                background-color: transparent;
                font-family: 'Courier New', monospace;
            }
        """)

class TerminalHeader(QLabel):
    """A Termux-style terminal header"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # Set up font
        font = QFont("Courier New", 12)
        font.setBold(True)
        self.setFont(font)

        # Set up styling
        self.setStyleSheet("""
            TerminalHeader {
                color: #00ffaa;
                background-color: transparent;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 5px;
                border-bottom: 1px solid #00aa00;
            }
        """)

class TerminalCommandOutput(QLabel):
    """A Termux-style terminal command output display"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        # Set up font
        font = QFont("Courier New", 9)
        self.setFont(font)

        # Set up styling
        self.setStyleSheet("""
            TerminalCommandOutput {
                color: #00ff00;
                background-color: #0a0f14;
                font-family: 'Courier New', monospace;
                padding: 10px;
                border: 1px solid #00aa00;
            }
        """)

        # Enable text selection
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Set word wrap
        self.setWordWrap(True)
