#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cloud Sync Module
Handles synchronization of data with cloud storage services
"""

import os
import json
import time
import datetime
import threading
import requests
from PyQt5.QtCore import QObject, pyqtSignal

class CloudSync(QObject):
    """Class for cloud synchronization"""
    # Define signals
    sync_started = pyqtSignal()
    sync_progress = pyqtSignal(int, int)  # current, total
    sync_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.sync_thread = None
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_status = "Not synced"
        
        # Load API keys and endpoints from config
        self.api_key = self.config.get("cloud_api_key", "")
        self.api_endpoint = self.config.get("cloud_api_endpoint", "https://api.example.com/usbmonitor")
        self.cloud_provider = self.config.get("cloud_provider", "custom")
        
        # Set up cloud provider-specific settings
        self._setup_cloud_provider()
    
    def _setup_cloud_provider(self):
        """Set up cloud provider-specific settings"""
        if self.cloud_provider == "aws":
            # AWS S3 settings
            self.s3_bucket = self.config.get("aws_s3_bucket", "")
            self.aws_region = self.config.get("aws_region", "us-east-1")
            self.aws_access_key = self.config.get("aws_access_key", "")
            self.aws_secret_key = self.config.get("aws_secret_key", "")
            
            # Import boto3 if available
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.aws_region,
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key
                )
            except ImportError:
                print("boto3 not installed. AWS S3 sync will not be available.")
                self.s3_client = None
        
        elif self.cloud_provider == "azure":
            # Azure Blob Storage settings
            self.azure_account = self.config.get("azure_account", "")
            self.azure_key = self.config.get("azure_key", "")
            self.azure_container = self.config.get("azure_container", "")
            
            # Import Azure SDK if available
            try:
                from azure.storage.blob import BlobServiceClient
                self.blob_service = BlobServiceClient(
                    account_url=f"https://{self.azure_account}.blob.core.windows.net",
                    credential=self.azure_key
                )
            except ImportError:
                print("Azure SDK not installed. Azure Blob Storage sync will not be available.")
                self.blob_service = None
        
        elif self.cloud_provider == "gcp":
            # Google Cloud Storage settings
            self.gcp_bucket = self.config.get("gcp_bucket", "")
            self.gcp_credentials_file = self.config.get("gcp_credentials_file", "")
            
            # Import Google Cloud Storage SDK if available
            try:
                from google.cloud import storage
                self.gcs_client = storage.Client.from_service_account_json(self.gcp_credentials_file)
            except ImportError:
                print("Google Cloud Storage SDK not installed. GCP sync will not be available.")
                self.gcs_client = None
        
        elif self.cloud_provider == "dropbox":
            # Dropbox settings
            self.dropbox_token = self.config.get("dropbox_token", "")
            
            # Import Dropbox SDK if available
            try:
                import dropbox
                self.dbx_client = dropbox.Dropbox(self.dropbox_token)
            except ImportError:
                print("Dropbox SDK not installed. Dropbox sync will not be available.")
                self.dbx_client = None
    
    def sync_data(self, data_type="all"):
        """Synchronize data with cloud storage"""
        if self.is_syncing:
            return False, "Sync already in progress"
        
        if not self._check_cloud_config():
            return False, "Cloud storage not configured"
        
        # Start sync in a separate thread
        self.sync_thread = threading.Thread(target=self._sync_thread, args=(data_type,))
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        return True, "Sync started"
    
    def _check_cloud_config(self):
        """Check if cloud storage is properly configured"""
        if self.cloud_provider == "aws":
            return self.s3_client is not None and self.s3_bucket
        elif self.cloud_provider == "azure":
            return self.blob_service is not None and self.azure_container
        elif self.cloud_provider == "gcp":
            return self.gcs_client is not None and self.gcp_bucket
        elif self.cloud_provider == "dropbox":
            return self.dbx_client is not None
        elif self.cloud_provider == "custom":
            return self.api_key and self.api_endpoint
        else:
            return False
    
    def _sync_thread(self, data_type):
        """Thread function for data synchronization"""
        self.is_syncing = True
        self.sync_started.emit()
        
        try:
            # Determine which data to sync
            data_to_sync = []
            
            if data_type == "all" or data_type == "device_history":
                data_to_sync.append(("device_history", self._get_device_history()))
            
            if data_type == "all" or data_type == "scan_results":
                data_to_sync.append(("scan_results", self._get_scan_results()))
            
            if data_type == "all" or data_type == "alerts":
                data_to_sync.append(("alerts", self._get_alerts()))
            
            if data_type == "all" or data_type == "settings":
                data_to_sync.append(("settings", self._get_settings()))
            
            # Sync data
            total_items = len(data_to_sync)
            for i, (item_type, item_data) in enumerate(data_to_sync):
                self.sync_progress.emit(i + 1, total_items)
                
                # Sync based on cloud provider
                if self.cloud_provider == "aws":
                    self._sync_to_aws(item_type, item_data)
                elif self.cloud_provider == "azure":
                    self._sync_to_azure(item_type, item_data)
                elif self.cloud_provider == "gcp":
                    self._sync_to_gcp(item_type, item_data)
                elif self.cloud_provider == "dropbox":
                    self._sync_to_dropbox(item_type, item_data)
                else:
                    self._sync_to_custom_api(item_type, item_data)
                
                # Simulate some delay for demo purposes
                time.sleep(0.5)
            
            # Update sync status
            self.last_sync_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sync_status = f"Last synced: {self.last_sync_time}"
            
            self.sync_completed.emit(True, "Sync completed successfully")
        
        except Exception as e:
            self.sync_status = f"Sync failed: {str(e)}"
            self.sync_completed.emit(False, f"Sync failed: {str(e)}")
        
        finally:
            self.is_syncing = False
    
    def _get_device_history(self):
        """Get device history data for sync"""
        history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "device_history.json")
        
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading device history: {str(e)}")
        
        return {}
    
    def _get_scan_results(self):
        """Get scan results data for sync"""
        # In a real implementation, this would load scan results from a database or file
        # For demo purposes, we'll return a simple structure
        return {
            "scan_history": [],
            "last_scan_time": None
        }
    
    def _get_alerts(self):
        """Get alerts data for sync"""
        # In a real implementation, this would load alerts from a database or file
        # For demo purposes, we'll return a simple structure
        return {
            "alerts": [],
            "last_alert_time": None
        }
    
    def _get_settings(self):
        """Get settings data for sync"""
        # In a real implementation, this would load settings from QSettings or a file
        # For demo purposes, we'll return a simple structure
        return {
            "settings": self.config,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _sync_to_aws(self, item_type, item_data):
        """Sync data to AWS S3"""
        if not self.s3_client:
            raise Exception("AWS S3 client not initialized")
        
        # Convert data to JSON
        json_data = json.dumps(item_data)
        
        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=f"usbmonitor/{item_type}.json",
            Body=json_data,
            ContentType="application/json"
        )
    
    def _sync_to_azure(self, item_type, item_data):
        """Sync data to Azure Blob Storage"""
        if not self.blob_service:
            raise Exception("Azure Blob Storage client not initialized")
        
        # Convert data to JSON
        json_data = json.dumps(item_data)
        
        # Upload to Azure Blob Storage
        container_client = self.blob_service.get_container_client(self.azure_container)
        blob_client = container_client.get_blob_client(f"usbmonitor/{item_type}.json")
        blob_client.upload_blob(json_data, overwrite=True)
    
    def _sync_to_gcp(self, item_type, item_data):
        """Sync data to Google Cloud Storage"""
        if not self.gcs_client:
            raise Exception("Google Cloud Storage client not initialized")
        
        # Convert data to JSON
        json_data = json.dumps(item_data)
        
        # Upload to GCS
        bucket = self.gcs_client.bucket(self.gcp_bucket)
        blob = bucket.blob(f"usbmonitor/{item_type}.json")
        blob.upload_from_string(json_data, content_type="application/json")
    
    def _sync_to_dropbox(self, item_type, item_data):
        """Sync data to Dropbox"""
        if not self.dbx_client:
            raise Exception("Dropbox client not initialized")
        
        # Convert data to JSON
        json_data = json.dumps(item_data)
        
        # Upload to Dropbox
        self.dbx_client.files_upload(
            json_data.encode('utf-8'),
            f"/usbmonitor/{item_type}.json",
            mode=dropbox.files.WriteMode.overwrite
        )
    
    def _sync_to_custom_api(self, item_type, item_data):
        """Sync data to custom API endpoint"""
        if not self.api_endpoint or not self.api_key:
            raise Exception("Custom API not configured")
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Make API request
        response = requests.post(
            f"{self.api_endpoint}/{item_type}",
            headers=headers,
            json=item_data
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            "is_syncing": self.is_syncing,
            "last_sync_time": self.last_sync_time,
            "status": self.sync_status,
            "cloud_provider": self.cloud_provider
        }
    
    def download_data(self, data_type):
        """Download data from cloud storage"""
        if self.is_syncing:
            return False, "Sync already in progress", None
        
        if not self._check_cloud_config():
            return False, "Cloud storage not configured", None
        
        try:
            # Download based on cloud provider
            if self.cloud_provider == "aws":
                data = self._download_from_aws(data_type)
            elif self.cloud_provider == "azure":
                data = self._download_from_azure(data_type)
            elif self.cloud_provider == "gcp":
                data = self._download_from_gcp(data_type)
            elif self.cloud_provider == "dropbox":
                data = self._download_from_dropbox(data_type)
            else:
                data = self._download_from_custom_api(data_type)
            
            return True, "Download successful", data
        
        except Exception as e:
            return False, f"Download failed: {str(e)}", None
    
    def _download_from_aws(self, data_type):
        """Download data from AWS S3"""
        if not self.s3_client:
            raise Exception("AWS S3 client not initialized")
        
        # Download from S3
        response = self.s3_client.get_object(
            Bucket=self.s3_bucket,
            Key=f"usbmonitor/{data_type}.json"
        )
        
        # Parse JSON
        return json.loads(response['Body'].read().decode('utf-8'))
    
    def _download_from_azure(self, data_type):
        """Download data from Azure Blob Storage"""
        if not self.blob_service:
            raise Exception("Azure Blob Storage client not initialized")
        
        # Download from Azure Blob Storage
        container_client = self.blob_service.get_container_client(self.azure_container)
        blob_client = container_client.get_blob_client(f"usbmonitor/{data_type}.json")
        download = blob_client.download_blob()
        
        # Parse JSON
        return json.loads(download.readall().decode('utf-8'))
    
    def _download_from_gcp(self, data_type):
        """Download data from Google Cloud Storage"""
        if not self.gcs_client:
            raise Exception("Google Cloud Storage client not initialized")
        
        # Download from GCS
        bucket = self.gcs_client.bucket(self.gcp_bucket)
        blob = bucket.blob(f"usbmonitor/{data_type}.json")
        
        # Parse JSON
        return json.loads(blob.download_as_string().decode('utf-8'))
    
    def _download_from_dropbox(self, data_type):
        """Download data from Dropbox"""
        if not self.dbx_client:
            raise Exception("Dropbox client not initialized")
        
        # Download from Dropbox
        metadata, response = self.dbx_client.files_download(f"/usbmonitor/{data_type}.json")
        
        # Parse JSON
        return json.loads(response.content.decode('utf-8'))
    
    def _download_from_custom_api(self, data_type):
        """Download data from custom API endpoint"""
        if not self.api_endpoint or not self.api_key:
            raise Exception("Custom API not configured")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Make API request
        response = requests.get(
            f"{self.api_endpoint}/{data_type}",
            headers=headers
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        # Parse JSON
        return response.json()
