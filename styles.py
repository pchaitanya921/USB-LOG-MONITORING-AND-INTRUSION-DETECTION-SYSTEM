#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Styles Module
Provides stylesheets and themes for the application
"""

def get_dark_theme_stylesheet():
    """Get dark theme stylesheet with ethical hacking theme"""
    return """
    /* Global Styles */
    QWidget {
        background-color: #0a0f14;
        color: #00ff00;
        font-family: 'Courier New', monospace;
    }
    
    /* Main Window */
    QMainWindow {
        background-color: #0a0f14;
        border: 1px solid #1a2a3a;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #0a0f14;
        color: #00ff00;
        border-bottom: 1px solid #1a2a3a;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 5px 10px;
    }
    
    QMenuBar::item:selected {
        background-color: #1a2a3a;
    }
    
    QMenu {
        background-color: #0a0f14;
        border: 1px solid #1a2a3a;
    }
    
    QMenu::item {
        padding: 5px 20px;
    }
    
    QMenu::item:selected {
        background-color: #1a2a3a;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #0a0f14;
        color: #00ff00;
        border-top: 1px solid #1a2a3a;
    }
    
    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #1a2a3a;
        background-color: #0a0f14;
    }
    
    QTabBar::tab {
        background-color: #0a0f14;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        border-bottom: none;
        padding: 8px 15px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #1a2a3a;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #152535;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #1a2a3a;
        color: #00ff00;
        border: 1px solid #00ff00;
        border-radius: 3px;
        padding: 5px 15px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #2a3a4a;
        border: 1px solid #00ffaa;
    }
    
    QPushButton:pressed {
        background-color: #0a1a2a;
    }
    
    QPushButton:disabled {
        background-color: #1a1a1a;
        color: #555555;
        border: 1px solid #555555;
    }
    
    /* Text Inputs */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #0a1520;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        border-radius: 3px;
        padding: 5px;
        selection-background-color: #2a3a4a;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #00ff00;
    }
    
    /* Combo Box */
    QComboBox {
        background-color: #0a1520;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        border-radius: 3px;
        padding: 5px;
        min-width: 6em;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #1a2a3a;
    }
    
    QComboBox::down-arrow {
        image: url(assets/icons/dropdown_arrow.png);
    }
    
    QComboBox QAbstractItemView {
        background-color: #0a1520;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        selection-background-color: #2a3a4a;
    }
    
    /* Spin Box */
    QSpinBox, QDoubleSpinBox {
        background-color: #0a1520;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        border-radius: 3px;
        padding: 5px;
    }
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 16px;
        border-left: 1px solid #1a2a3a;
        border-bottom: 1px solid #1a2a3a;
    }
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 16px;
        border-left: 1px solid #1a2a3a;
        border-top: 1px solid #1a2a3a;
    }
    
    /* Check Box */
    QCheckBox {
        spacing: 10px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    
    QCheckBox::indicator:unchecked {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
    }
    
    QCheckBox::indicator:checked {
        border: 1px solid #00ff00;
        background-color: #0a1520;
        image: url(assets/icons/checkmark.png);
    }
    
    /* Radio Button */
    QRadioButton {
        spacing: 10px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 9px;
    }
    
    QRadioButton::indicator:unchecked {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
    }
    
    QRadioButton::indicator:checked {
        border: 1px solid #00ff00;
        background-color: #0a1520;
        image: url(assets/icons/radiobutton.png);
    }
    
    /* Slider */
    QSlider::groove:horizontal {
        height: 8px;
        background-color: #0a1520;
        border: 1px solid #1a2a3a;
        border-radius: 4px;
    }
    
    QSlider::handle:horizontal {
        background-color: #00ff00;
        border: 1px solid #00ff00;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    
    QSlider::add-page:horizontal {
        background-color: #0a1520;
    }
    
    QSlider::sub-page:horizontal {
        background-color: #1a2a3a;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #1a2a3a;
        border-radius: 3px;
        background-color: #0a1520;
        text-align: center;
        color: #00ff00;
    }
    
    QProgressBar::chunk {
        background-color: #00ff00;
        width: 10px;
    }
    
    /* Scroll Bar */
    QScrollBar:vertical {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        width: 15px;
        margin: 15px 0 15px 0;
    }
    
    QScrollBar::handle:vertical {
        background-color: #1a2a3a;
        min-height: 20px;
    }
    
    QScrollBar::add-line:vertical {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        height: 15px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    
    QScrollBar::sub-line:vertical {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        height: 15px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    
    QScrollBar:horizontal {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        height: 15px;
        margin: 0 15px 0 15px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #1a2a3a;
        min-width: 20px;
    }
    
    QScrollBar::add-line:horizontal {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        width: 15px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }
    
    QScrollBar::sub-line:horizontal {
        border: 1px solid #1a2a3a;
        background-color: #0a1520;
        width: 15px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }
    
    /* Group Box */
    QGroupBox {
        border: 1px solid #1a2a3a;
        border-radius: 5px;
        margin-top: 20px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 10px;
        color: #00ff00;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: #0a0f14;
        alternate-background-color: #0a1520;
        gridline-color: #1a2a3a;
        border: 1px solid #1a2a3a;
        color: #00ff00;
    }
    
    QTableWidget::item:selected {
        background-color: #2a3a4a;
    }
    
    QHeaderView::section {
        background-color: #1a2a3a;
        color: #00ff00;
        padding: 5px;
        border: 1px solid #0a0f14;
        font-weight: bold;
    }
    
    /* Tree Widget */
    QTreeWidget {
        background-color: #0a0f14;
        alternate-background-color: #0a1520;
        border: 1px solid #1a2a3a;
        color: #00ff00;
    }
    
    QTreeWidget::item:selected {
        background-color: #2a3a4a;
    }
    
    QTreeWidget::branch {
        background-color: transparent;
    }
    
    QTreeWidget::branch:has-siblings:!adjoins-item {
        border-image: url(assets/icons/vline.png) 0;
    }
    
    QTreeWidget::branch:has-siblings:adjoins-item {
        border-image: url(assets/icons/branch-more.png) 0;
    }
    
    QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
        border-image: url(assets/icons/branch-end.png) 0;
    }
    
    QTreeWidget::branch:has-children:!has-siblings:closed,
    QTreeWidget::branch:closed:has-children:has-siblings {
        border-image: none;
        image: url(assets/icons/branch-closed.png);
    }
    
    QTreeWidget::branch:open:has-children:!has-siblings,
    QTreeWidget::branch:open:has-children:has-siblings {
        border-image: none;
        image: url(assets/icons/branch-open.png);
    }
    
    /* List Widget */
    QListWidget {
        background-color: #0a0f14;
        alternate-background-color: #0a1520;
        border: 1px solid #1a2a3a;
        color: #00ff00;
    }
    
    QListWidget::item:selected {
        background-color: #2a3a4a;
    }
    
    /* Tool Tip */
    QToolTip {
        background-color: #0a1520;
        color: #00ff00;
        border: 1px solid #1a2a3a;
        padding: 5px;
    }
    
    /* Terminal-style text */
    .terminal-text {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a0f14;
        border: 1px solid #1a2a3a;
        padding: 10px;
    }
    
    /* Custom card styles */
    .card {
        background-color: #0a1520;
        border: 1px solid #1a2a3a;
        border-radius: 5px;
        padding: 10px;
    }
    
    .card-header {
        font-weight: bold;
        color: #00ffaa;
        border-bottom: 1px solid #1a2a3a;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    
    /* Custom status indicators */
    .status-secure {
        color: #00ff00;
    }
    
    .status-warning {
        color: #ffff00;
    }
    
    .status-danger {
        color: #ff0000;
    }
    
    /* Custom button styles */
    .primary-button {
        background-color: #00aa00;
        color: #000000;
        border: none;
        font-weight: bold;
    }
    
    .danger-button {
        background-color: #aa0000;
        color: #ffffff;
        border: none;
        font-weight: bold;
    }
    
    /* Frame styles */
    QFrame {
        border: 1px solid #1a2a3a;
        border-radius: 3px;
    }
    
    QFrame#line {
        background-color: #1a2a3a;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #1a2a3a;
    }
    
    QSplitter::handle:horizontal {
        width: 5px;
    }
    
    QSplitter::handle:vertical {
        height: 5px;
    }
    
    /* Dialog */
    QDialog {
        background-color: #0a0f14;
        border: 1px solid #1a2a3a;
    }
    
    QDialog QLabel {
        color: #00ff00;
    }
    
    /* Message Box */
    QMessageBox {
        background-color: #0a0f14;
        color: #00ff00;
    }
    
    QMessageBox QLabel {
        color: #00ff00;
    }
    
    /* Tool Bar */
    QToolBar {
        background-color: #0a0f14;
        border: 1px solid #1a2a3a;
        spacing: 3px;
    }
    
    QToolBar::handle {
        image: url(assets/icons/toolbar-handle.png);
    }
    
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 3px;
    }
    
    QToolButton:hover {
        background-color: #1a2a3a;
        border: 1px solid #00ff00;
    }
    
    QToolButton:pressed {
        background-color: #0a1a2a;
    }
    
    /* Dock Widget */
    QDockWidget {
        titlebar-close-icon: url(assets/icons/close.png);
        titlebar-normal-icon: url(assets/icons/undock.png);
    }
    
    QDockWidget::title {
        text-align: center;
        background-color: #1a2a3a;
        color: #00ff00;
        padding: 5px;
    }
    
    QDockWidget::close-button, QDockWidget::float-button {
        border: none;
        background: transparent;
        padding: 0px;
    }
    
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {
        background: #2a3a4a;
    }
    
    /* Calendar Widget */
    QCalendarWidget {
        background-color: #0a0f14;
        color: #00ff00;
    }
    
    QCalendarWidget QToolButton {
        color: #00ff00;
        background-color: #1a2a3a;
        border: 1px solid #1a2a3a;
    }
    
    QCalendarWidget QMenu {
        background-color: #0a0f14;
        color: #00ff00;
    }
    
    QCalendarWidget QSpinBox {
        background-color: #0a1520;
        color: #00ff00;
        selection-background-color: #2a3a4a;
    }
    
    QCalendarWidget QAbstractItemView:enabled {
        color: #00ff00;
        background-color: #0a1520;
        selection-background-color: #2a3a4a;
        selection-color: #00ff00;
    }
    
    QCalendarWidget QAbstractItemView:disabled {
        color: #555555;
    }
    
    /* Main Window specific styles */
    #centralWidget {
        background-color: #0a0f14;
    }
    
    #statusBar {
        background-color: #0a0f14;
        color: #00ff00;
    }
    
    /* Custom styles for specific widgets */
    #dashboardTitle, #devicesTitle, #scansTitle, #alertsTitle, #settingsTitle {
        font-size: 24px;
        font-weight: bold;
        color: #00ffaa;
    }
    
    /* Ethical hacking theme specific styles */
    .code-text {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a1520;
        border: 1px solid #1a2a3a;
        padding: 5px;
    }
    
    .binary-text {
        font-family: 'Courier New', monospace;
        color: #00aa00;
        font-size: 10px;
    }
    
    .scan-result {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a1520;
        border: 1px solid #1a2a3a;
        padding: 10px;
    }
    
    .scan-result-malicious {
        color: #ff0000;
    }
    
    .scan-result-suspicious {
        color: #ffff00;
    }
    
    .scan-result-clean {
        color: #00ff00;
    }
    """

def get_terminal_text_style():
    """Get terminal-style text formatting"""
    return """
    <style>
        .terminal {
            font-family: 'Courier New', monospace;
            color: #00ff00;
            background-color: #0a0f14;
            padding: 10px;
            border: 1px solid #1a2a3a;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        
        .terminal-header {
            color: #00ffaa;
            font-weight: bold;
            border-bottom: 1px solid #1a2a3a;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }
        
        .terminal-command {
            color: #00ffff;
        }
        
        .terminal-output {
            color: #00ff00;
        }
        
        .terminal-error {
            color: #ff0000;
        }
        
        .terminal-warning {
            color: #ffff00;
        }
        
        .terminal-success {
            color: #00ff00;
        }
    </style>
    """
