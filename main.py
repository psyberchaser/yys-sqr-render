import sys
import os
import json
import uuid
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QPushButton, QFileDialog, QLineEdit, QMessageBox, QTextEdit, QMainWindow,
    QCheckBox
)
from PyQt6.QtCore import Qt, QPoint, QStandardPaths
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

# --- UI Classes (Reverting to the user-preferred version) ---

class ClickableImageView(QLabel):
    """ A QLabel that can display an image and capture/drag mouse clicks. """
    def __init__(self, parent=None, on_four_points=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Please select a photo to begin.")
        self.points = []
        self.original_pixmap = None
        self.on_four_points = on_four_points
        self.dragging_point_index = None

    def set_image(self, image_path):
        self.points = []
        self.original_pixmap = QPixmap(image_path)
        self.update_display()

    def get_point_at(self, click_pos):
        if not self.pixmap(): return None
        offset_x = (self.width() - self.pixmap().width()) / 2
        offset_y = (self.height() - self.pixmap().height()) / 2
        for i, point_on_pixmap in enumerate(self.points):
            point_on_widget = point_on_pixmap + QPoint(int(offset_x), int(offset_y))
            if (click_pos - point_on_widget).manhattanLength() < 10:
                return i
        return None

    def resizeEvent(self, event):
        self.update_display()

    def mousePressEvent(self, event):
        if not self.original_pixmap: return
        self.dragging_point_index = self.get_point_at(event.pos())
        if self.dragging_point_index is not None: return

        if len(self.points) < 4:
            scaled_pixmap = self.pixmap()
            if not scaled_pixmap: return
            offset_x = (self.width() - scaled_pixmap.width()) / 2
            offset_y = (self.height() - scaled_pixmap.height()) / 2
            click_pos = event.pos()
            if (offset_x <= click_pos.x() < self.width() - offset_x and
                offset_y <= click_pos.y() < self.height() - offset_y):
                point_on_pixmap = click_pos - QPoint(int(offset_x), int(offset_y))
                self.points.append(point_on_pixmap)
                self.update_display()
                if len(self.points) == 4 and self.on_four_points: self.on_four_points()

    def mouseMoveEvent(self, event):
        if self.dragging_point_index is not None:
            scaled_pixmap = self.pixmap()
            if not scaled_pixmap: return
            offset_x = (self.width() - scaled_pixmap.width()) / 2
            offset_y = (self.height() - scaled_pixmap.height()) / 2
            self.points[self.dragging_point_index] = event.pos() - QPoint(int(offset_x), int(offset_y))
            self.update_display()

    def mouseReleaseEvent(self, event):
        self.dragging_point_index = None

    def update_display(self):
        if not self.original_pixmap: return
        scaled_pixmap = self.original_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        painter = QPainter(scaled_pixmap)
        for point in self.points:
            painter.setBrush(Qt.GlobalColor.green)
            painter.drawEllipse(point, 5, 5)
        painter.end()
        self.setPixmap(scaled_pixmap)
    
    def get_scaled_points(self):
        if not self.original_pixmap or not self.pixmap(): return []
        original_size = self.original_pixmap.size()
        scaled_size = self.pixmap().size()
        return [
            [p.x() * (original_size.width() / scaled_size.width()), p.y() * (original_size.height() / scaled_size.height())]
            for p in self.points
        ]

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YYS - SQR')
        self.setGeometry(100, 100, 800, 700)
        self.db = self.load_database()
        self.tm = trustmark.TrustMark(verbose=False, encoding_type=ENCODING_TYPE)

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.embed_tab = QWidget()
        self.decode_tab = QWidget()
        self.tabs.addTab(self.embed_tab, "Embed SQR")
        self.tabs.addTab(self.decode_tab, "Decode SQR")

        self.setup_embed_ui()
        self.setup_decode_ui()

    def load_database(self):
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r') as f: return json.load(f)
        return {}

    def save_database(self):
        with open(DATABASE_FILE, 'w') as f: json.dump(self.db, f, indent=4)

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
        self.destroy_on_scan_checkbox.setChecked(False) # Default to off
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
            
            # Use PIL, which is what TrustMark expects
            cover_image = Image.open(self.selected_embed_image_path).convert('RGB')
            watermarked_image = self.tm.encode(cover_image, new_id)

            # Use Python's rock-solid method to get the user's home directory.
            # This avoids issues with QStandardPaths in the packaged app.
            save_dir = os.path.expanduser('~')
            default_save_path = os.path.join(save_dir, f"watermarked_{new_id}.png")

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Watermarked Image", default_save_path, "PNG Image (*.png)")
            if not save_path:
                self.embed_status_label.setText("Save cancelled.")
                return
            
            watermarked_image.save(save_path)

            ipfs_cid = None # Default to None
            if self.web3_toggle_checkbox.isChecked():
                # --- IPFS UPLOAD ---
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

    def setup_decode_ui(self):
        layout = QVBoxLayout(self.decode_tab)
        layout.addWidget(QLabel("Step 1: Select photo of printed image"))
        self.select_decode_btn = QPushButton("Select Photo")
        self.select_decode_btn.clicked.connect(self.select_decode_image)
        layout.addWidget(self.select_decode_btn)

        layout.addWidget(QLabel("Step 2: Click the 4 corners of the image (TL, TR, BR, BL)"))
        self.image_viewer = ClickableImageView(self, on_four_points=lambda: self.decode_btn.setEnabled(True))
        layout.addWidget(self.image_viewer)

        self.decode_btn = QPushButton("Step 3: Correct Perspective and Decode SQR")
        self.decode_btn.setEnabled(False)
        self.decode_btn.clicked.connect(self.decode_watermark)
        layout.addWidget(self.decode_btn)
        
        # --- New Web3 UI Elements ---
        web3_layout = QHBoxLayout()
        web3_layout.addWidget(QLabel("Your Sepolia Private Key:"))
        self.private_key_input = QLineEdit()
        self.private_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.private_key_input.setPlaceholderText("Enter private key for a TESTNET wallet with Sepolia ETH")
        web3_layout.addWidget(self.private_key_input)
        layout.addLayout(web3_layout)

        self.etherscan_btn = QPushButton("View Transaction on Etherscan")
        self.etherscan_btn.setEnabled(False)
        self.etherscan_btn.clicked.connect(self.open_etherscan)
        layout.addWidget(self.etherscan_btn)
        # ---
        
        self.decode_result_display = QTextEdit()
        self.decode_result_display.setReadOnly(True)
        layout.addWidget(self.decode_result_display)

    def select_decode_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_decode_image_path = path
            self.image_viewer.set_image(path)
            self.decode_btn.setEnabled(False)
            self.etherscan_btn.setEnabled(False) # Disable on new image
            self.transaction_hash = None
            self.decode_result_display.setText("Image loaded. Please select the four corners.")

    def open_etherscan(self):
        if hasattr(self, 'transaction_hash') and self.transaction_hash:
            url = f"https://sepolia.etherscan.io/tx/{self.transaction_hash}"
            webbrowser.open(url)

    def decode_watermark(self):
        if not hasattr(self, 'selected_decode_image_path') or len(self.image_viewer.points) != 4:
            QMessageBox.warning(self, "Warning", "Please select an image and click the four corners first.")
            return

        self.decode_result_display.setText("Processing image...")
        QApplication.processEvents()

        try:
            image_cv = cv2.imread(self.selected_decode_image_path)
            
            scaled_points = self.image_viewer.get_scaled_points()
            coordinates = np.float32(scaled_points)
            
            output_width, output_height = 1024, 1024
            destination_points = np.float32([[0,0], [output_width,0], [output_width,output_height], [0,output_height]])

            matrix = cv2.getPerspectiveTransform(coordinates, destination_points)
            corrected_image_cv = cv2.warpPerspective(image_cv, matrix, (output_width, output_height))
            
            corrected_image_rgb = cv2.cvtColor(corrected_image_cv, cv2.COLOR_BGR2RGB)
            image_to_decode = Image.fromarray(corrected_image_rgb)

            secret_id, present, _ = self.tm.decode(image_to_decode)

            if not present:
                self.decode_result_display.setText("FAILURE: No watermark was detected.")
                QMessageBox.warning(self, "Warning", "No watermark was detected.")
                return

            was_destroyed = False # Flag to track deletion
            ipfs_cid_to_send = "" # Default to empty string
            retrieved_data = self.db.get(secret_id)
            if retrieved_data:
                ipfs_cid_to_send = retrieved_data.get('ipfs_cid', "") or ""
                result_text = (f"SUCCESS!\n\nID: {secret_id}\n\n"
                               f"Message: {retrieved_data.get('secret_message', 'N/A')}\n"
                               f"IPFS CID: {ipfs_cid_to_send}")
                
                # Check for the self-destruct flag
                if retrieved_data.get('destroy_on_scan', False):
                    result_text += "\n\nNOTICE: This was a single-use SQR. The data has been deleted."
                    del self.db[secret_id]
                    self.save_database()
                    was_destroyed = True
            else:
                result_text = f"FAILURE: Decoded ID '{secret_id}' not found in database."
            
            self.decode_result_display.setText(result_text)

            if was_destroyed:
                self.decode_result_display.append("\nProceeding with final proof-of-scan transaction...")

            # --- Call Smart Contract ---
            private_key = self.private_key_input.text()
            if not private_key:
                self.decode_result_display.append("\n\nSkipping blockchain transaction: No private key entered.")
                QMessageBox.warning(self, "Warning", "No private key entered.")
                return

            self.decode_result_display.append("\n\nConnecting to blockchain and sending transaction...")
            QApplication.processEvents()
            
            try:
                # Increase the timeout to handle slow public RPCs
                w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={'timeout': 120}))
                if w3.eth.chain_id != 11155111: # Sepolia's Chain ID
                    raise ConnectionError(f"Connected to wrong network. Expected Sepolia (11155111), but got {w3.eth.chain_id}.")

                account = w3.eth.account.from_key(private_key)
                wallet_address = account.address
                
                contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
                
                nonce = w3.eth.get_transaction_count(wallet_address)
                
                # Build transaction using the correct web3.py v6+ syntax
                tx = contract.functions.recordScan(secret_id, ipfs_cid_to_send).build_transaction({
                    'chainId': 11155111, # Sepolia Chain ID
                    'from': wallet_address,
                    'nonce': nonce,
                    'gas': 200000,
                    'gasPrice': w3.to_wei('10', 'gwei')
                })

                # Sign and send
                signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                self.decode_result_display.append(f"Transaction sent. Waiting for confirmation...\\nHash: {tx_hash.hex()}")
                QApplication.processEvents()

                # Wait for receipt
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                if tx_receipt.status == 1:
                    self.transaction_hash = tx_hash.hex()
                    self.etherscan_btn.setEnabled(True)
                    self.decode_result_display.append("\nTransaction Confirmed! Proof-of-Scan recorded on the Sepolia testnet.")
                else:
                    self.decode_result_display.append("\nBlockchain Transaction Failed. Check Etherscan for details.")

            except Exception as e:
                self.decode_result_display.append(f"\n\nBlockchain Error: {e}")

        except Exception as e:
            self.decode_result_display.setText(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred during decoding: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec())
