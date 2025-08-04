# YYS-SQR Mobile Auto-Scanner
# Automated watermark detection and scanning

import cv2
import numpy as np
from PIL import Image
import trustmark
from web3 import Web3
import json
import time

class AutoScanner:
    """Automated watermark scanning with computer vision"""
    
    def __init__(self):
        self.tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
        self.camera = None
        self.scanning = False
        self.last_scan_time = 0
        self.scan_cooldown = 2.0  # seconds between scans
        
    def start_camera_scanning(self, camera_index=0):
        """Start continuous camera scanning"""
        self.camera = cv2.VideoCapture(camera_index)
        self.scanning = True
        
        print("🔍 Auto-scanner started. Point camera at watermarked images...")
        
        while self.scanning:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_scan_time < self.scan_cooldown:
                continue
            
            # Detect and process potential watermarks
            result = self.process_frame(frame)
            if result:
                print(f"✅ Found watermark: {result}")
                self.last_scan_time = current_time
                
            # Show preview (optional)
            cv2.imshow('YYS-SQR Auto Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cleanup()
    
    def process_frame(self, frame):
        """Process a single camera frame for watermarks"""
        try:
            # Convert to PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Try to decode watermark directly (no corner selection needed)
            secret_id, present, confidence = self.tm.decode(pil_image)
            
            if present and confidence > 0.7:  # High confidence threshold
                return {
                    'watermark_id': secret_id,
                    'confidence': confidence,
                    'timestamp': time.time()
                }
                
            # If direct decode fails, try with rectangle detection
            rectangles = self.detect_rectangles(frame)
            for rect in rectangles:
                cropped = self.extract_rectangle(frame, rect)
                if cropped is not None:
                    result = self.scan_cropped_image(cropped)
                    if result:
                        return result
                        
        except Exception as e:
            print(f"Frame processing error: {e}")
            
        return None
    
    def detect_rectangles(self, frame):
        """Detect rectangular regions that might contain watermarks"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular (4 corners)
            if len(approx) == 4:
                area = cv2.contourArea(contour)
                if 10000 < area < 500000:  # Reasonable size range
                    rectangles.append(approx.reshape(4, 2))
                    
        return rectangles
    
    def extract_rectangle(self, frame, corners):
        """Extract and correct perspective of detected rectangle"""
        try:
            # Order corners: TL, TR, BR, BL
            corners = self.order_corners(corners)
            
            # Define destination size
            width, height = 512, 512
            dst_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
            
            # Get perspective transform
            matrix = cv2.getPerspectiveTransform(corners.astype(np.float32), dst_points)
            corrected = cv2.warpPerspective(frame, matrix, (width, height))
            
            return corrected
            
        except Exception as e:
            print(f"Rectangle extraction error: {e}")
            return None
    
    def order_corners(self, corners):
        """Order corners as TL, TR, BR, BL"""
        # Calculate center
        center = np.mean(corners, axis=0)
        
        # Sort by angle from center
        def angle_from_center(point):
            return np.arctan2(point[1] - center[1], point[0] - center[0])
        
        sorted_corners = sorted(corners, key=angle_from_center)
        
        # Reorder to TL, TR, BR, BL
        # This is a simplified ordering - might need refinement
        return np.array(sorted_corners)
    
    def scan_cropped_image(self, cropped_frame):
        """Scan a cropped/corrected image for watermarks"""
        try:
            rgb_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            secret_id, present, confidence = self.tm.decode(pil_image)
            
            if present and confidence > 0.5:  # Lower threshold for cropped images
                return {
                    'watermark_id': secret_id,
                    'confidence': confidence,
                    'timestamp': time.time(),
                    'method': 'auto_crop'
                }
                
        except Exception as e:
            print(f"Cropped scan error: {e}")
            
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        self.scanning = False

class BatchScanner:
    """Scan multiple images in a directory automatically"""
    
    def __init__(self):
        self.tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
        self.results = []
    
    def scan_directory(self, directory_path, extensions=('.jpg', '.jpeg', '.png')):
        """Scan all images in a directory"""
        import os
        
        print(f"🔍 Scanning directory: {directory_path}")
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(extensions):
                file_path = os.path.join(directory_path, filename)
                result = self.scan_single_file(file_path)
                if result:
                    self.results.append(result)
                    print(f"✅ {filename}: {result['watermark_id']}")
                else:
                    print(f"❌ {filename}: No watermark found")
        
        return self.results
    
    def scan_single_file(self, file_path):
        """Scan a single image file"""
        try:
            image = Image.open(file_path).convert('RGB')
            secret_id, present, confidence = self.tm.decode(image)
            
            if present:
                return {
                    'file_path': file_path,
                    'watermark_id': secret_id,
                    'confidence': confidence,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return None
    
    def export_results(self, output_file="scan_results.json"):
        """Export scan results to JSON"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        return output_file

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "camera":
        # Camera mode
        scanner = AutoScanner()
        scanner.start_camera_scanning()
    elif len(sys.argv) > 1:
        # Directory mode
        batch_scanner = BatchScanner()
        batch_scanner.scan_directory(sys.argv[1])
        batch_scanner.export_results()
    else:
        print("Usage:")
        print("  python auto_scanner.py camera          # Start camera scanning")
        print("  python auto_scanner.py /path/to/images # Batch scan directory")