# Enhanced YYS-SQR with Automatic Corner Detection
# Integrates auto-detection into the existing GUI

import sys
import os
import json
import uuid
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QPushButton, QFileDialog, QLineEdit, QMessageBox, QTextEdit, QMainWindow,
    QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QPoint, QStandardPaths, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PIL import Image
import trustmark
import requests
import base64
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import webbrowser
from web3 import Web3

# Import our auto corner detection
try:
    from auto_corner_detection import AutoCornerDetector
except ImportError:
    print("Warning: auto_corner_detection.py not found. Auto-detection will be disabled.")
    AutoCornerDetector = None

# --- Globals ---
# Get the standard application data location
APP_DATA_PATH = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
# Create our own subdirectory within it
APP_DIR = os.path.join(APP_DATA_PATH, "YYS-SQR")
os.makedirs(APP_DIR, exist_ok=True)
DATABASE_FILE = os.path.join(APP_DIR, "database.json")
ID_LENGTH = 5
# Using the strongest ECC as it was the most reliable
ENCODING_TYPE = trustmark.TrustMark.Encoding.BCH_SUPER 

# --- Filebase S3-Compatible Configuration ---
FILEBASE_ACCESS_KEY = "F27503EAB0C920092137"
FILEBASE_SECRET_KEY = "sZtWNzcoWWZkUhHDxM2WChGjt9OYrVDMsWZ0HYW3"
FILEBASE_BUCKET_NAME = "yys-yys"
FILEBASE_ENDPOINT = "https://s3.filebase.com"

# --- Web3/Blockchain Configuration ---
CONTRACT_ADDRESS = "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8"
# Using a dedicated Infura Sepolia RPC endpoint for reliability
SEPOLIA_RPC_URL = "https://sepolia.infura.io/v3/7d8b2ce49fe24184b30beb42dc1fa791" 
# This is the ABI for ProofOfScanV2
CONTRACT_ABI = json.loads('[{"inputs":[{"internalType":"string","name":"_uniqueId","type":"string"},{"internalType":"string","name":"_ipfsCid","type":"string"}],"name":"recordScan","outputs":[],"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"scanner","type":"address"},{"indexed":false,"internalType":"string","name":"uniqueId","type":"string"},{"indexed":false,"internalType":"string","name":"ipfsCid","type":"string"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"ScanRecorded","type":"event"},{"inputs":[{"internalType":"string","name":"_uniqueId","type":"string"}],"name":"getScanDetails","outputs":[{"internalType":"address","name":"scanner","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"ipfsCid","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"latestScan","outputs":[{"internalType":"address","name":"scanner","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"ipfsCid","type":"string"}],"stateMutability":"view","type":"function"}]')

# --- Helper Functions ---

def generate_unique_id(existing_ids):
    """Generates a unique 5-character alphanumeric ID."""
    while True:
        # Using uuid for better randomness than the previous implementation
        unique_id = str(uuid.uuid4())[:ID_LENGTH]
        if unique_id not in existing_ids:
            return unique_id

def upload_to_ipfs(file_path):
    """Uploads a file to Filebase and returns the IPFS CID."""
    s3_client = boto3.client(
        's3',
        endpoint_url=FILEBASE_ENDPOINT,
        aws_access_key_id=FILEBASE_ACCESS_KEY,
        aws_secret_access_key=FILEBASE_SECRET_KEY,
        region_name='us-east-1',
        config=Config(signature_version='s3v4')
    )

    object_name = os.path.basename(file_path)

    try:
        with open(file_path, 'rb') as f:
            s3_client.put_object(Body=f, Bucket=FILEBASE_BUCKET_NAME, Key=object_name)
        
        # After uploading, get the object's metadata to find the CID
        response = s3_client.head_object(
            Bucket=FILEBASE_BUCKET_NAME,
            Key=object_name
        )
        
        # The IPFS CID is stored in the 'x-amz-meta-cid' metadata field
        ipfs_cid = response['Metadata'].get('cid')
        if not ipfs_cid:
             # Fallback for older metadata key, just in case
             ipfs_cid = response['Metadata'].get('x-amz-meta-cid')

        print(f"Filebase upload successful. IPFS CID: {ipfs_cid}")
        return ipfs_cid

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        QMessageBox.warning(None, "Filebase Error", f"Failed to upload to Filebase S3.\nError Code: {error_code}\nMessage: {e}")
        return None
    except Exception as e:
        QMessageBox.warning(None, "Filebase Error", f"An unexpected error occurred during Filebase upload: {e}")
        return None

class AutoDetectionThread(QThread):
    """Background thread for automatic corner detection"""
    
    detection_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.detector = AutoCornerDetector()
    
    def run(self):
        """Run automatic detection in background"""
        try:
            self.progress_update.emit("Analyzing image...")
            result = self.detector.detect_and_decode(self.image_path)
            self.detection_complete.emit(result)
        except Exception as e:
            self.detection_complete.emit({
                'error': f'Detection failed: {str(e)}'
            })

class EnhancedImageView(QLabel):
    """Enhanced image viewer with both auto-detection and manual corner selection"""
    
    def __init__(self, parent=None, on_four_points=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Please select a photo to begin.")
        self.original_pixmap = None
        self.detected_corners = None
        self.manual_points = []  # For manual corner selection
        self.auto_mode = True  # Default to auto mode
        self.on_four_points = on_four_points
        self.dragging_point_index = None
    
    def set_image(self, image_path):
        """Set image and reset corner selection"""
        self.original_pixmap = QPixmap(image_path)
        self.detected_corners = None
        self.manual_points = []
        self.update_display()
    
    def set_detected_corners(self, corners):
        """Set corners from automatic detection"""
        self.detected_corners = corners
        self.manual_points = []  # Clear manual points when auto-detection succeeds
        self.update_display()
    
    def set_manual_mode(self, manual_mode):
        """Switch between auto and manual modes"""
        self.auto_mode = not manual_mode
        if manual_mode:
            self.detected_corners = None  # Clear auto-detected corners
            self.manual_points = []  # Reset manual points
        self.update_display()
    
    def get_point_at(self, click_pos):
        """Check if click is near an existing manual point"""
        if not self.pixmap() or not self.manual_points: 
            return None
        offset_x = (self.width() - self.pixmap().width()) / 2
        offset_y = (self.height() - self.pixmap().height()) / 2
        for i, point_on_pixmap in enumerate(self.manual_points):
            point_on_widget = point_on_pixmap + QPoint(int(offset_x), int(offset_y))
            if (click_pos - point_on_widget).manhattanLength() < 10:
                return i
        return None

    def mousePressEvent(self, event):
        """Handle mouse clicks for manual corner selection"""
        if self.auto_mode or not self.original_pixmap:
            return
            
        self.dragging_point_index = self.get_point_at(event.pos())
        if self.dragging_point_index is not None: 
            return

        if len(self.manual_points) < 4:
            scaled_pixmap = self.pixmap()
            if not scaled_pixmap: 
                return
            offset_x = (self.width() - scaled_pixmap.width()) / 2
            offset_y = (self.height() - scaled_pixmap.height()) / 2
            click_pos = event.pos()
            if (offset_x <= click_pos.x() < self.width() - offset_x and
                offset_y <= click_pos.y() < self.height() - offset_y):
                point_on_pixmap = click_pos - QPoint(int(offset_x), int(offset_y))
                self.manual_points.append(point_on_pixmap)
                self.update_display()
                if len(self.manual_points) == 4 and self.on_four_points: 
                    self.on_four_points()

    def mouseMoveEvent(self, event):
        """Handle dragging of manual corner points"""
        if self.auto_mode or self.dragging_point_index is None:
            return
        scaled_pixmap = self.pixmap()
        if not scaled_pixmap: 
            return
        offset_x = (self.width() - self.pixmap().width()) / 2
        offset_y = (self.height() - self.pixmap().height()) / 2
        self.manual_points[self.dragging_point_index] = event.pos() - QPoint(int(offset_x), int(offset_y))
        self.update_display()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.dragging_point_index = None
    
    def get_scaled_points(self):
        """Get corner points scaled to original image coordinates"""
        if not self.original_pixmap or not self.pixmap(): 
            return []
        
        # Use manual points if in manual mode, otherwise use detected corners
        points_to_scale = self.manual_points if not self.auto_mode and self.manual_points else []
        if not points_to_scale and self.detected_corners is not None:
            # Convert detected corners to QPoint format for scaling
            points_to_scale = [QPoint(int(corner[0]), int(corner[1])) for corner in self.detected_corners]
        
        if not points_to_scale:
            return []
            
        original_size = self.original_pixmap.size()
        scaled_size = self.pixmap().size()
        return [
            [p.x() * (original_size.width() / scaled_size.width()), 
             p.y() * (original_size.height() / scaled_size.height())]
            for p in points_to_scale
        ]
    
    def update_display(self):
        """Update display with corners (auto-detected or manual)"""
        if not self.original_pixmap:
            return
            
        scaled_pixmap = self.original_pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        painter = QPainter(scaled_pixmap)
        
        # Draw auto-detected corners (if in auto mode)
        if self.auto_mode and self.detected_corners is not None:
            original_size = self.original_pixmap.size()
            scaled_size = scaled_pixmap.size()
            scale_x = scaled_size.width() / original_size.width()
            scale_y = scaled_size.height() / original_size.height()
            
            for i, corner in enumerate(self.detected_corners):
                x = int(corner[0] * scale_x)
                y = int(corner[1] * scale_y)
                
                # Draw corner with different colors
                colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, Qt.GlobalColor.yellow]
                painter.setBrush(colors[i % 4])
                painter.drawEllipse(x-8, y-8, 16, 16)
                
                # Draw corner number
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(x-5, y+5, str(i+1))
        
        # Draw manual points (if in manual mode)
        elif not self.auto_mode and self.manual_points:
            for i, point in enumerate(self.manual_points):
                colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, Qt.GlobalColor.yellow]
                painter.setBrush(colors[i % 4])
                painter.drawEllipse(point, 5, 5)
                
                # Draw corner number
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(point.x()-5, point.y()+5, str(i+1))
        
        painter.end()
        self.setPixmap(scaled_pixmap)

class EnhancedWatermarkApp(QMainWindow):
    """Enhanced YYS-SQR app with automatic corner detection"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YYS-SQR Enhanced')
        self.setGeometry(100, 100, 900, 800)
        
        # Initialize components
        self.db = self.load_database()
        self.tm = trustmark.TrustMark(verbose=False, encoding_type=ENCODING_TYPE)
        self.detection_thread = None
        
        # Setup UI
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.embed_tab = QWidget()
        self.decode_tab = QWidget()
        self.tabs.addTab(self.embed_tab, "Embed SQR")
        self.tabs.addTab(self.decode_tab, "Decode SQR (Auto)")

        self.setup_embed_ui()
        self.setup_enhanced_decode_ui()
    
    def setup_enhanced_decode_ui(self):
        """Setup enhanced decode UI with auto-detection"""
        layout = QVBoxLayout(self.decode_tab)
        
        # Step 1: Photo Selection
        layout.addWidget(QLabel("Step 1: Select Photo of Watermarked Image"))
        self.select_decode_btn = QPushButton("Select Photo")
        self.select_decode_btn.clicked.connect(self.select_decode_image)
        layout.addWidget(self.select_decode_btn)

        # Auto/Manual mode toggle
        mode_layout = QHBoxLayout()
        self.auto_mode_checkbox = QCheckBox("Automatic Corner Detection (Recommended)")
        self.auto_mode_checkbox.setChecked(True)
        self.auto_mode_checkbox.stateChanged.connect(self.toggle_detection_mode)
        mode_layout.addWidget(self.auto_mode_checkbox)
        layout.addLayout(mode_layout)

        # Enhanced image viewer
        layout.addWidget(QLabel("Step 2: Image Analysis"))
        self.enhanced_image_viewer = EnhancedImageView(self, on_four_points=self.on_manual_four_points)
        layout.addWidget(self.enhanced_image_viewer)
        
        # Progress bar for auto-detection
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.detection_status = QLabel("Ready for image selection")
        layout.addWidget(self.detection_status)

        # Manual corner adjustment (hidden by default)
        self.manual_controls = QWidget()
        manual_layout = QVBoxLayout(self.manual_controls)
        manual_layout.addWidget(QLabel("Manual Mode: Click 4 corners (TL→TR→BR→BL)"))
        self.manual_controls.setVisible(False)
        layout.addWidget(self.manual_controls)

        # Step 3: Blockchain integration
        layout.addWidget(QLabel("Step 3: Blockchain Integration (Optional)"))
        
        # Auto blockchain checkbox
        self.auto_blockchain_checkbox = QCheckBox("Automatically record blockchain proof when watermark is found")
        self.auto_blockchain_checkbox.setChecked(True)
        layout.addWidget(self.auto_blockchain_checkbox)
        
        web3_layout = QHBoxLayout()
        web3_layout.addWidget(QLabel("Sepolia Private Key:"))
        self.private_key_input = QLineEdit()
        self.private_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.private_key_input.setPlaceholderText("Enter 64-character hex private key (with or without 0x)")
        self.private_key_input.textChanged.connect(self.validate_private_key_input)
        web3_layout.addWidget(self.private_key_input)
        
        # Private key status label
        self.private_key_status = QLabel("")
        web3_layout.addWidget(self.private_key_status)
        layout.addLayout(web3_layout)

        # Decode button
        self.auto_decode_btn = QPushButton("Step 4: Decode Watermark")
        self.auto_decode_btn.setEnabled(False)
        self.auto_decode_btn.clicked.connect(self.auto_decode_watermark)
        layout.addWidget(self.auto_decode_btn)

        # Etherscan button
        self.etherscan_btn = QPushButton("View Transaction on Etherscan")
        self.etherscan_btn.setEnabled(False)
        self.etherscan_btn.clicked.connect(self.open_etherscan)
        layout.addWidget(self.etherscan_btn)
        
        # Results display
        self.decode_result_display = QTextEdit()
        self.decode_result_display.setReadOnly(True)
        layout.addWidget(self.decode_result_display)
    
    def select_decode_image(self):
        """Select image and trigger auto-detection if enabled"""
        path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_decode_image_path = path
            self.enhanced_image_viewer.set_image(path)
            self.auto_decode_btn.setEnabled(False)
            self.etherscan_btn.setEnabled(False)
            self.transaction_hash = None
            
            if self.auto_mode_checkbox.isChecked():
                self.start_auto_detection()
            else:
                self.detection_status.setText("Manual mode: Click 4 corners on the image")
    
    def start_auto_detection(self):
        """Start automatic corner detection in background thread"""
        if not hasattr(self, 'selected_decode_image_path'):
            return
        
        self.detection_status.setText("🔍 Analyzing image for corners...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start detection thread
        self.detection_thread = AutoDetectionThread(self.selected_decode_image_path)
        self.detection_thread.detection_complete.connect(self.on_detection_complete)
        self.detection_thread.progress_update.connect(self.on_progress_update)
        self.detection_thread.start()
    
    def on_progress_update(self, message):
        """Handle progress updates from detection thread"""
        self.detection_status.setText(message)
    
    def on_detection_complete(self, result):
        """Handle completion of automatic detection"""
        self.progress_bar.setVisible(False)
        
        if 'error' in result:
            self.detection_status.setText(f"❌ Auto-detection failed: {result['error']}")
            self.decode_result_display.setText(f"Automatic detection failed: {result['error']}\n\nTry switching to manual mode or use a clearer image.")
        else:
            if result['success']:
                watermark_id = result['watermark_id']
                
                # Look up the actual message from database
                retrieved_data = self.db.get(watermark_id)
                if retrieved_data:
                    secret_message = retrieved_data.get('secret_message', 'N/A')
                    ipfs_cid = retrieved_data.get('ipfs_cid', '')
                    destroy_on_scan = retrieved_data.get('destroy_on_scan', False)
                    
                    self.detection_status.setText(f"✅ Watermark decoded! Message: '{secret_message}'")
                    
                    result_text = f"SUCCESS! Auto-detection found watermark.\n\n"
                    result_text += f"Watermark ID: {watermark_id}\n"
                    result_text += f"Secret Message: '{secret_message}'\n"
                    result_text += f"Confidence: {result.get('confidence', 'N/A')}\n"
                    result_text += f"Detection Method: {result.get('method', 'N/A')}\n"
                    
                    if ipfs_cid:
                        result_text += f"IPFS CID: {ipfs_cid}\n"
                    
                    if destroy_on_scan:
                        result_text += "\nNOTICE: This was a single-use SQR. The data will be deleted after blockchain proof."
                        # Delete the data now
                        del self.db[watermark_id]
                        self.save_database()
                        result_text += "\nData has been deleted from local database."
                    
                    self.decode_result_display.setText(result_text)
                    
                    # Store the complete result including the message
                    result['secret_message'] = secret_message
                    result['ipfs_cid'] = ipfs_cid
                    result['was_destroyed'] = destroy_on_scan
                    
                else:
                    self.detection_status.setText(f"❌ Watermark ID '{watermark_id}' not found in database")
                    self.decode_result_display.setText(f"Watermark detected but ID '{watermark_id}' not found in local database.\n\nThis could mean:\n- The watermark was created on a different device\n- The database was reset\n- This is a single-use SQR that was already scanned")
                
                # Show detected corners if available
                if 'corners' in result:
                    self.enhanced_image_viewer.set_detected_corners(result['corners'])
                
                # Store result for blockchain transaction
                self.auto_detection_result = result
                
                # Automatically trigger blockchain transaction if enabled and private key is provided
                private_key = self.private_key_input.text()
                if self.auto_blockchain_checkbox.isChecked() and private_key:
                    self.decode_result_display.append("\n\n🔗 Auto-triggering blockchain transaction...")
                    QApplication.processEvents()
                    self.record_blockchain_proof(result)
                else:
                    # Enable manual blockchain transaction
                    self.auto_decode_btn.setEnabled(True)
                    self.auto_decode_btn.setText("Record Blockchain Proof")
                    if not private_key:
                        self.decode_result_display.append("\n\n💡 Enter private key to enable blockchain proof recording.")
                    elif not self.auto_blockchain_checkbox.isChecked():
                        self.decode_result_display.append("\n\n💡 Click 'Record Blockchain Proof' to create on-chain record.")
            else:
                self.detection_status.setText("❌ No watermark found with auto-detection")
                self.decode_result_display.setText("Auto-detection completed but no watermark was found.\n\nTry:\n- Using a clearer image\n- Better lighting\n- Manual mode")
    
    def toggle_detection_mode(self, state):
        """Toggle between automatic and manual detection modes"""
        auto_mode = state == Qt.CheckState.Checked.value
        self.manual_controls.setVisible(not auto_mode)
        self.enhanced_image_viewer.set_manual_mode(not auto_mode)
        
        if auto_mode:
            self.detection_status.setText("Auto-detection mode enabled")
            # If we have an image, trigger auto-detection
            if hasattr(self, 'selected_decode_image_path'):
                self.start_auto_detection()
        else:
            self.detection_status.setText("Manual mode: Click 4 corners on image (TL→TR→BR→BL)")
            self.auto_decode_btn.setEnabled(False)
    
    def on_manual_four_points(self):
        """Called when user has selected 4 manual corners"""
        self.detection_status.setText("✅ 4 corners selected manually")
        self.auto_decode_btn.setEnabled(True)
        self.auto_decode_btn.setText("Decode with Manual Corners")
    
    def auto_decode_watermark(self):
        """Handle decoding with auto-detected corners, manual corners, or record blockchain proof"""
        if hasattr(self, 'auto_detection_result') and self.auto_detection_result.get('success') and self.auto_mode_checkbox.isChecked():
            # We already have the watermark from auto-detection, just record blockchain proof
            self.record_blockchain_proof(self.auto_detection_result)
        else:
            # Manual decoding or auto-detection fallback
            self.decode_with_manual_corners()
    
    def decode_with_manual_corners(self):
        """Decode watermark using manual corner selection or fallback"""
        if not hasattr(self, 'selected_decode_image_path'):
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return
        
        # Get corner points (manual or auto-detected)
        scaled_points = self.enhanced_image_viewer.get_scaled_points()
        if len(scaled_points) != 4:
            QMessageBox.warning(self, "Warning", "Please select 4 corners first.")
            return

        self.decode_result_display.setText("Processing image...")
        QApplication.processEvents()

        try:
            import cv2
            import numpy as np
            
            # Load image
            image_cv = cv2.imread(self.selected_decode_image_path)
            
            # Apply perspective correction
            coordinates = np.float32(scaled_points)
            output_width, output_height = 1024, 1024
            destination_points = np.float32([[0,0], [output_width,0], [output_width,output_height], [0,output_height]])

            matrix = cv2.getPerspectiveTransform(coordinates, destination_points)
            corrected_image_cv = cv2.warpPerspective(image_cv, matrix, (output_width, output_height))
            
            # Convert to PIL for watermark decoding
            corrected_image_rgb = cv2.cvtColor(corrected_image_cv, cv2.COLOR_BGR2RGB)
            image_to_decode = Image.fromarray(corrected_image_rgb)

            # Decode watermark
            secret_id, present, confidence = self.tm.decode(image_to_decode)

            if not present:
                self.decode_result_display.setText("FAILURE: No watermark was detected.")
                QMessageBox.warning(self, "Warning", "No watermark was detected.")
                return

            # Look up message in database
            retrieved_data = self.db.get(secret_id)
            if retrieved_data:
                secret_message = retrieved_data.get('secret_message', 'N/A')
                ipfs_cid = retrieved_data.get('ipfs_cid', '')
                destroy_on_scan = retrieved_data.get('destroy_on_scan', False)
                
                result_text = f"SUCCESS!\n\nID: {secret_id}\n"
                result_text += f"Message: '{secret_message}'\n"
                result_text += f"Confidence: {confidence}\n"
                
                if ipfs_cid:
                    result_text += f"IPFS CID: {ipfs_cid}\n"
                
                if destroy_on_scan:
                    result_text += "\nNOTICE: This was a single-use SQR. The data has been deleted."
                    del self.db[secret_id]
                    self.save_database()
                
                self.decode_result_display.setText(result_text)
                
                # Store result for blockchain transaction
                self.manual_decode_result = {
                    'success': True,
                    'watermark_id': secret_id,
                    'secret_message': secret_message,
                    'ipfs_cid': ipfs_cid,
                    'confidence': confidence,
                    'was_destroyed': destroy_on_scan
                }
                
                # Update button for blockchain proof
                self.auto_decode_btn.setText("Record Blockchain Proof")
                
            else:
                result_text = f"FAILURE: Decoded ID '{secret_id}' not found in database."
                self.decode_result_display.setText(result_text)

        except Exception as e:
            self.decode_result_display.setText(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred during decoding: {e}")
    
    def record_blockchain_proof(self, detection_result):
        """Record proof-of-scan on blockchain"""
        # Get the result from either auto-detection or manual decoding
        if not detection_result and hasattr(self, 'manual_decode_result'):
            detection_result = self.manual_decode_result
        
        if not detection_result or not detection_result.get('success'):
            QMessageBox.warning(self, "Warning", "No successful watermark detection to record.")
            return
            
        private_key = self.private_key_input.text().strip()
        if not private_key:
            self.decode_result_display.append("\n\nSkipping blockchain transaction: No private key entered.")
            return
        
        # Validate private key format
        if not self.validate_private_key(private_key):
            self.decode_result_display.append("\n\n❌ Invalid private key format. Must be 64 hex characters (with or without 0x prefix).")
            return
        
        self.decode_result_display.append("\n\n🔗 Recording proof-of-scan on blockchain...")
        QApplication.processEvents()
        
        try:
            # Blockchain transaction logic
            w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={'timeout': 120}))
            if w3.eth.chain_id != 11155111:
                raise ConnectionError(f"Wrong network. Expected Sepolia (11155111), got {w3.eth.chain_id}")

            # Clean and validate private key before using
            clean_private_key = self.clean_private_key(private_key)
            account = w3.eth.account.from_key(clean_private_key)
            wallet_address = account.address
            
            contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
            nonce = w3.eth.get_transaction_count(wallet_address)
            
            # Use IPFS CID from result if available
            ipfs_cid = detection_result.get('ipfs_cid', '') or ''
            
            tx = contract.functions.recordScan(detection_result['watermark_id'], ipfs_cid).build_transaction({
                'chainId': 11155111,
                'from': wallet_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3.to_wei('10', 'gwei')
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key=clean_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            self.decode_result_display.append(f"Transaction sent: {tx_hash.hex()}")
            QApplication.processEvents()

            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt.status == 1:
                self.transaction_hash = tx_hash.hex()
                self.etherscan_btn.setEnabled(True)
                
                # Show properly formatted URL
                tx_url = f"https://sepolia.etherscan.io/tx/{self.transaction_hash}"
                self.decode_result_display.append(f"\n✅ Blockchain proof recorded successfully!")
                self.decode_result_display.append(f"🔗 View on Etherscan: {tx_url}")
            else:
                self.decode_result_display.append("\n❌ Blockchain transaction failed.")

        except Exception as e:
            self.decode_result_display.append(f"\n\n❌ Blockchain Error: {e}")
    
    def validate_private_key(self, private_key):
        """Validate private key format"""
        try:
            # Remove 0x prefix if present
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Check if it's 64 hex characters
            if len(private_key) != 64:
                return False
            
            # Check if all characters are hex
            int(private_key, 16)
            return True
        except ValueError:
            return False
    
    def clean_private_key(self, private_key):
        """Clean and format private key"""
        # Remove whitespace
        private_key = private_key.strip()
        
        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        
        # Ensure it's lowercase
        private_key = private_key.lower()
        
        return private_key
    
    def validate_private_key_input(self):
        """Real-time validation of private key input"""
        private_key = self.private_key_input.text().strip()
        
        if not private_key:
            self.private_key_status.setText("")
            self.private_key_status.setStyleSheet("")
            return
        
        if self.validate_private_key(private_key):
            self.private_key_status.setText("✅ Valid")
            self.private_key_status.setStyleSheet("color: green;")
        else:
            self.private_key_status.setText("❌ Invalid format")
            self.private_key_status.setStyleSheet("color: red;")
    
    def load_database(self):
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_database(self):
        with open(DATABASE_FILE, 'w') as f:
            json.dump(self.db, f, indent=4)

    def setup_embed_ui(self):
        layout = QVBoxLayout(self.embed_tab)
        layout.addWidget(QLabel("Step 1: Select Image"))
        self.select_embed_btn = QPushButton("Select Image")
        self.select_embed_btn.clicked.connect(self.select_embed_image)
        layout.addWidget(self.select_embed_btn)
        self.embed_image_label = QLabel("No image selected.")
        layout.addWidget(self.embed_image_label)

        layout.addWidget(QLabel("Step 2: Enter Secret Message"))
        self.message_input = QTextEdit()
        layout.addWidget(self.message_input)

        self.destroy_on_scan_checkbox = QCheckBox("Single-Use SQR (deletes after one scan)")
        self.destroy_on_scan_checkbox.setChecked(False)
        layout.addWidget(self.destroy_on_scan_checkbox)

        self.web3_toggle_checkbox = QCheckBox("Enable Web3 Features (Upload to IPFS)")
        self.web3_toggle_checkbox.setChecked(True)
        layout.addWidget(self.web3_toggle_checkbox)

        layout.addWidget(QLabel("Step 3: Embed and Save"))
        self.embed_btn = QPushButton("Embed SQR")
        self.embed_btn.clicked.connect(self.embed_watermark)
        layout.addWidget(self.embed_btn)
        
        self.embed_status_label = QTextEdit()
        self.embed_status_label.setReadOnly(True)
        layout.addWidget(self.embed_status_label)

    def select_embed_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_embed_image_path = path
            self.embed_image_label.setText(f"Selected: {os.path.basename(path)}")
            self.embed_status_label.setText("Ready to embed.")

    def embed_watermark(self):
        if not hasattr(self, 'selected_embed_image_path'):
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return
        
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Warning", "Please enter a secret message.")
            return

        self.embed_status_label.setText("Starting up...")
        QApplication.processEvents()

        try:
            new_id = generate_unique_id(list(self.db.keys()))
            
            # Use PIL, which is what the watermarking expects
            cover_image = Image.open(self.selected_embed_image_path).convert('RGB')
            watermarked_image = self.tm.encode(cover_image, new_id)

            # Use Python's rock-solid method to get the user's home directory.
            save_dir = os.path.expanduser('~')
            default_save_path = os.path.join(save_dir, f"watermarked_{new_id}.png")

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Watermarked Image", default_save_path, "PNG Image (*.png)")
            if not save_path:
                self.embed_status_label.setText("Save cancelled.")
                return
            
            watermarked_image.save(save_path)

            ipfs_cid = None
            if self.web3_toggle_checkbox.isChecked():
                self.embed_status_label.append("\nUploading to IPFS...")
                QApplication.processEvents()
                ipfs_cid = upload_to_ipfs(save_path)
            
            destroy_on_scan = self.destroy_on_scan_checkbox.isChecked()
            self.db[new_id] = {
                "secret_message": message, 
                "ipfs_cid": ipfs_cid,
                "destroy_on_scan": destroy_on_scan
            }
            self.save_database()
            
            status_text = f"Success! Watermark embedded.\nSaved to: {save_path}\nID: '{new_id}'"
            if destroy_on_scan:
                status_text += "\nType: Single-Use (will be deleted after scan)"
            if ipfs_cid:
                status_text += f"\nIPFS CID: {ipfs_cid}"
            elif self.web3_toggle_checkbox.isChecked():
                status_text += "\nIPFS upload failed. See console for details."
            else:
                status_text += "\nWeb3 features disabled. IPFS upload skipped."

            self.embed_status_label.setText(status_text)
            QMessageBox.information(self, "Success", status_text)

        except Exception as e:
            self.embed_status_label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def open_etherscan(self):
        if hasattr(self, 'transaction_hash') and self.transaction_hash:
            # Ensure the transaction hash has 0x prefix
            tx_hash = self.transaction_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            url = f"https://sepolia.etherscan.io/tx/{tx_hash}"
            webbrowser.open(url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedWatermarkApp()
    window.show()
    sys.exit(app.exec())