#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cloud Settings Dialog
Dialog for configuring cloud storage settings
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QFormLayout, QComboBox,
    QTabWidget, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSettings

from src.utils.cloud_sync import CloudSync

class CloudSettingsDialog(QDialog):
    """Dialog for configuring cloud storage settings"""
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        
        # Store config
        self.config = config or {}
        
        # Set up dialog
        self.setWindowTitle("Cloud Storage Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add title
        title_label = QLabel("Cloud Storage Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create tabs
        self.general_tab = QWidget()
        self.aws_tab = QWidget()
        self.azure_tab = QWidget()
        self.gcp_tab = QWidget()
        self.dropbox_tab = QWidget()
        self.custom_tab = QWidget()
        
        # Add tabs to tab widget
        tab_widget.addTab(self.general_tab, "General")
        tab_widget.addTab(self.aws_tab, "AWS S3")
        tab_widget.addTab(self.azure_tab, "Azure")
        tab_widget.addTab(self.gcp_tab, "Google Cloud")
        tab_widget.addTab(self.dropbox_tab, "Dropbox")
        tab_widget.addTab(self.custom_tab, "Custom API")
        
        # Set up tabs
        self._setup_general_tab()
        self._setup_aws_tab()
        self._setup_azure_tab()
        self._setup_gcp_tab()
        self._setup_dropbox_tab()
        self._setup_custom_tab()
        
        layout.addWidget(tab_widget)
        
        # Add sync status
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Not synced")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        # Sync now button
        self.sync_button = QPushButton("Sync Now")
        self.sync_button.clicked.connect(self.sync_now)
        buttons_layout.addWidget(self.sync_button)
        
        # Add spacer
        buttons_layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        # Initialize cloud sync
        self.cloud_sync = CloudSync(self.config)
        
        # Connect signals
        self.cloud_sync.sync_started.connect(self.on_sync_started)
        self.cloud_sync.sync_progress.connect(self.on_sync_progress)
        self.cloud_sync.sync_completed.connect(self.on_sync_completed)
        
        # Update status
        self._update_status()
    
    def _setup_general_tab(self):
        """Set up general tab"""
        layout = QVBoxLayout(self.general_tab)
        
        # Enable cloud sync
        enable_group = QGroupBox("Cloud Sync")
        enable_layout = QVBoxLayout(enable_group)
        
        self.enable_cloud_sync = QCheckBox("Enable cloud synchronization")
        self.enable_cloud_sync.setChecked(self.config.get("enable_cloud_sync", False))
        enable_layout.addWidget(self.enable_cloud_sync)
        
        # Cloud provider
        provider_form = QFormLayout()
        
        self.cloud_provider = QComboBox()
        self.cloud_provider.addItems(["AWS S3", "Azure Blob Storage", "Google Cloud Storage", "Dropbox", "Custom API"])
        
        # Set current provider
        provider = self.config.get("cloud_provider", "custom")
        if provider == "aws":
            self.cloud_provider.setCurrentText("AWS S3")
        elif provider == "azure":
            self.cloud_provider.setCurrentText("Azure Blob Storage")
        elif provider == "gcp":
            self.cloud_provider.setCurrentText("Google Cloud Storage")
        elif provider == "dropbox":
            self.cloud_provider.setCurrentText("Dropbox")
        else:
            self.cloud_provider.setCurrentText("Custom API")
        
        provider_form.addRow("Cloud Provider:", self.cloud_provider)
        
        enable_layout.addLayout(provider_form)
        
        layout.addWidget(enable_group)
        
        # Sync settings
        sync_group = QGroupBox("Sync Settings")
        sync_layout = QVBoxLayout(sync_group)
        
        self.sync_device_history = QCheckBox("Sync device history")
        self.sync_device_history.setChecked(self.config.get("sync_device_history", True))
        sync_layout.addWidget(self.sync_device_history)
        
        self.sync_scan_results = QCheckBox("Sync scan results")
        self.sync_scan_results.setChecked(self.config.get("sync_scan_results", True))
        sync_layout.addWidget(self.sync_scan_results)
        
        self.sync_alerts = QCheckBox("Sync alerts")
        self.sync_alerts.setChecked(self.config.get("sync_alerts", True))
        sync_layout.addWidget(self.sync_alerts)
        
        self.sync_settings = QCheckBox("Sync settings")
        self.sync_settings.setChecked(self.config.get("sync_settings", False))
        sync_layout.addWidget(self.sync_settings)
        
        # Auto sync interval
        auto_sync_form = QFormLayout()
        
        self.auto_sync_interval = QComboBox()
        self.auto_sync_interval.addItems(["Never", "Every 15 minutes", "Every hour", "Every 6 hours", "Every day"])
        
        # Set current interval
        interval = self.config.get("auto_sync_interval", "never")
        if interval == "15min":
            self.auto_sync_interval.setCurrentText("Every 15 minutes")
        elif interval == "1hour":
            self.auto_sync_interval.setCurrentText("Every hour")
        elif interval == "6hours":
            self.auto_sync_interval.setCurrentText("Every 6 hours")
        elif interval == "1day":
            self.auto_sync_interval.setCurrentText("Every day")
        else:
            self.auto_sync_interval.setCurrentText("Never")
        
        auto_sync_form.addRow("Auto Sync:", self.auto_sync_interval)
        
        sync_layout.addLayout(auto_sync_form)
        
        layout.addWidget(sync_group)
        
        # Add spacer
        layout.addStretch()
    
    def _setup_aws_tab(self):
        """Set up AWS S3 tab"""
        layout = QVBoxLayout(self.aws_tab)
        
        # AWS S3 settings
        aws_group = QGroupBox("AWS S3 Settings")
        aws_form = QFormLayout(aws_group)
        
        self.aws_access_key = QLineEdit(self.config.get("aws_access_key", ""))
        aws_form.addRow("Access Key:", self.aws_access_key)
        
        self.aws_secret_key = QLineEdit(self.config.get("aws_secret_key", ""))
        self.aws_secret_key.setEchoMode(QLineEdit.Password)
        aws_form.addRow("Secret Key:", self.aws_secret_key)
        
        self.aws_region = QLineEdit(self.config.get("aws_region", "us-east-1"))
        aws_form.addRow("Region:", self.aws_region)
        
        self.aws_s3_bucket = QLineEdit(self.config.get("aws_s3_bucket", ""))
        aws_form.addRow("S3 Bucket:", self.aws_s3_bucket)
        
        layout.addWidget(aws_group)
        
        # Add spacer
        layout.addStretch()
    
    def _setup_azure_tab(self):
        """Set up Azure tab"""
        layout = QVBoxLayout(self.azure_tab)
        
        # Azure Blob Storage settings
        azure_group = QGroupBox("Azure Blob Storage Settings")
        azure_form = QFormLayout(azure_group)
        
        self.azure_account = QLineEdit(self.config.get("azure_account", ""))
        azure_form.addRow("Storage Account:", self.azure_account)
        
        self.azure_key = QLineEdit(self.config.get("azure_key", ""))
        self.azure_key.setEchoMode(QLineEdit.Password)
        azure_form.addRow("Access Key:", self.azure_key)
        
        self.azure_container = QLineEdit(self.config.get("azure_container", ""))
        azure_form.addRow("Container:", self.azure_container)
        
        layout.addWidget(azure_group)
        
        # Add spacer
        layout.addStretch()
    
    def _setup_gcp_tab(self):
        """Set up Google Cloud tab"""
        layout = QVBoxLayout(self.gcp_tab)
        
        # Google Cloud Storage settings
        gcp_group = QGroupBox("Google Cloud Storage Settings")
        gcp_form = QFormLayout(gcp_group)
        
        self.gcp_bucket = QLineEdit(self.config.get("gcp_bucket", ""))
        gcp_form.addRow("Bucket Name:", self.gcp_bucket)
        
        self.gcp_credentials_file = QLineEdit(self.config.get("gcp_credentials_file", ""))
        gcp_form.addRow("Credentials File:", self.gcp_credentials_file)
        
        # Browse button
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_gcp_credentials)
        gcp_form.addRow("", browse_button)
        
        layout.addWidget(gcp_group)
        
        # Add spacer
        layout.addStretch()
    
    def _setup_dropbox_tab(self):
        """Set up Dropbox tab"""
        layout = QVBoxLayout(self.dropbox_tab)
        
        # Dropbox settings
        dropbox_group = QGroupBox("Dropbox Settings")
        dropbox_form = QFormLayout(dropbox_group)
        
        self.dropbox_token = QLineEdit(self.config.get("dropbox_token", ""))
        self.dropbox_token.setEchoMode(QLineEdit.Password)
        dropbox_form.addRow("Access Token:", self.dropbox_token)
        
        # Get token button
        get_token_button = QPushButton("Get Access Token...")
        get_token_button.clicked.connect(self.get_dropbox_token)
        dropbox_form.addRow("", get_token_button)
        
        layout.addWidget(dropbox_group)
        
        # Add spacer
        layout.addStretch()
    
    def _setup_custom_tab(self):
        """Set up Custom API tab"""
        layout = QVBoxLayout(self.custom_tab)
        
        # Custom API settings
        custom_group = QGroupBox("Custom API Settings")
        custom_form = QFormLayout(custom_group)
        
        self.api_endpoint = QLineEdit(self.config.get("cloud_api_endpoint", "https://api.example.com/usbmonitor"))
        custom_form.addRow("API Endpoint:", self.api_endpoint)
        
        self.api_key = QLineEdit(self.config.get("cloud_api_key", ""))
        self.api_key.setEchoMode(QLineEdit.Password)
        custom_form.addRow("API Key:", self.api_key)
        
        layout.addWidget(custom_group)
        
        # Add spacer
        layout.addStretch()
    
    def browse_gcp_credentials(self):
        """Browse for GCP credentials file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select GCP Credentials File", "", "JSON Files (*.json)"
        )
        
        if file_path:
            self.gcp_credentials_file.setText(file_path)
    
    def get_dropbox_token(self):
        """Get Dropbox access token"""
        # In a real implementation, this would open a browser to the Dropbox OAuth flow
        # For demo purposes, we'll just show a message
        QMessageBox.information(
            self,
            "Dropbox Authentication",
            "To get a Dropbox access token:\n\n"
            "1. Go to https://www.dropbox.com/developers/apps\n"
            "2. Create a new app or use an existing one\n"
            "3. Generate an access token\n"
            "4. Copy and paste the token here"
        )
    
    def _update_status(self):
        """Update sync status"""
        status = self.cloud_sync.get_sync_status()
        
        if status["is_syncing"]:
            self.status_label.setText("Syncing...")
            self.sync_button.setEnabled(False)
        else:
            self.status_label.setText(status["status"])
            self.sync_button.setEnabled(True)
    
    def sync_now(self):
        """Sync data now"""
        # Check if cloud sync is enabled
        if not self.enable_cloud_sync.isChecked():
            QMessageBox.warning(self, "Cloud Sync Disabled", "Cloud synchronization is disabled. Please enable it first.")
            return
        
        # Determine what to sync
        data_types = []
        
        if self.sync_device_history.isChecked():
            data_types.append("device_history")
        
        if self.sync_scan_results.isChecked():
            data_types.append("scan_results")
        
        if self.sync_alerts.isChecked():
            data_types.append("alerts")
        
        if self.sync_settings.isChecked():
            data_types.append("settings")
        
        if not data_types:
            QMessageBox.warning(self, "No Data Selected", "Please select at least one data type to sync.")
            return
        
        # Start sync
        success, message = self.cloud_sync.sync_data("all")
        
        if not success:
            QMessageBox.warning(self, "Sync Error", message)
    
    def on_sync_started(self):
        """Handle sync started signal"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Syncing...")
        self.sync_button.setEnabled(False)
    
    def on_sync_progress(self, current, total):
        """Handle sync progress signal"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Syncing... ({current}/{total})")
    
    def on_sync_completed(self, success, message):
        """Handle sync completed signal"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(message)
        else:
            self.status_label.setText(f"Sync failed: {message}")
            QMessageBox.warning(self, "Sync Error", message)
        
        self.sync_button.setEnabled(True)
    
    def save_settings(self):
        """Save cloud settings"""
        # Update config
        self.config["enable_cloud_sync"] = self.enable_cloud_sync.isChecked()
        
        # Set cloud provider
        provider_text = self.cloud_provider.currentText()
        if provider_text == "AWS S3":
            self.config["cloud_provider"] = "aws"
        elif provider_text == "Azure Blob Storage":
            self.config["cloud_provider"] = "azure"
        elif provider_text == "Google Cloud Storage":
            self.config["cloud_provider"] = "gcp"
        elif provider_text == "Dropbox":
            self.config["cloud_provider"] = "dropbox"
        else:
            self.config["cloud_provider"] = "custom"
        
        # Set sync settings
        self.config["sync_device_history"] = self.sync_device_history.isChecked()
        self.config["sync_scan_results"] = self.sync_scan_results.isChecked()
        self.config["sync_alerts"] = self.sync_alerts.isChecked()
        self.config["sync_settings"] = self.sync_settings.isChecked()
        
        # Set auto sync interval
        interval_text = self.auto_sync_interval.currentText()
        if interval_text == "Every 15 minutes":
            self.config["auto_sync_interval"] = "15min"
        elif interval_text == "Every hour":
            self.config["auto_sync_interval"] = "1hour"
        elif interval_text == "Every 6 hours":
            self.config["auto_sync_interval"] = "6hours"
        elif interval_text == "Every day":
            self.config["auto_sync_interval"] = "1day"
        else:
            self.config["auto_sync_interval"] = "never"
        
        # AWS S3 settings
        self.config["aws_access_key"] = self.aws_access_key.text()
        self.config["aws_secret_key"] = self.aws_secret_key.text()
        self.config["aws_region"] = self.aws_region.text()
        self.config["aws_s3_bucket"] = self.aws_s3_bucket.text()
        
        # Azure Blob Storage settings
        self.config["azure_account"] = self.azure_account.text()
        self.config["azure_key"] = self.azure_key.text()
        self.config["azure_container"] = self.azure_container.text()
        
        # Google Cloud Storage settings
        self.config["gcp_bucket"] = self.gcp_bucket.text()
        self.config["gcp_credentials_file"] = self.gcp_credentials_file.text()
        
        # Dropbox settings
        self.config["dropbox_token"] = self.dropbox_token.text()
        
        # Custom API settings
        self.config["cloud_api_endpoint"] = self.api_endpoint.text()
        self.config["cloud_api_key"] = self.api_key.text()
        
        # Reinitialize cloud sync with new settings
        self.cloud_sync = CloudSync(self.config)
        
        # Connect signals
        self.cloud_sync.sync_started.connect(self.on_sync_started)
        self.cloud_sync.sync_progress.connect(self.on_sync_progress)
        self.cloud_sync.sync_completed.connect(self.on_sync_completed)
        
        # Update status
        self._update_status()
        
        # Accept dialog
        self.accept()
