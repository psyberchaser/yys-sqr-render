# Automatic Corner Detection for YYS-SQR
# Eliminates manual corner clicking for perspective correction

import cv2
import numpy as np
from PIL import Image
import trustmark

class AutoCornerDetector:
    """Automatically detect corners of watermarked images for perspective correction"""
    
    def __init__(self):
        self.tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    
    def detect_and_decode(self, image_path):
        """Main function: detect corners and decode watermark automatically"""
        print(f"🔍 Processing: {image_path}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Could not load image"}
        
        # Try multiple detection methods
        methods = [
            self.detect_document_corners,
            self.detect_contour_corners,
            self.detect_harris_corners,
            self.detect_edge_corners
        ]
        
        for i, method in enumerate(methods):
            print(f"  Trying method {i+1}: {method.__name__}")
            corners = method(image)
            
            if corners is not None and len(corners) == 4:
                print(f"  ✅ Found 4 corners with {method.__name__}")
                
                # Apply perspective correction
                corrected = self.correct_perspective(image, corners)
                
                # Try to decode watermark
                result = self.decode_watermark(corrected)
                if result['success']:
                    result['method'] = method.__name__
                    result['corners'] = corners.tolist()
                    return result
                else:
                    print(f"  ❌ Corners found but no watermark decoded")
            else:
                print(f"  ❌ Could not find 4 corners")
        
        return {"error": "Could not detect corners or decode watermark"}
    
    def detect_document_corners(self, image):
        """Method 1: Document/paper detection (best for printed images)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Morphological operations to close gaps
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for contour in contours[:10]:  # Check top 10 largest contours
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's a quadrilateral
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                # Must be reasonably large (at least 10% of image area)
                min_area = (image.shape[0] * image.shape[1]) * 0.1
                if area > min_area:
                    corners = approx.reshape(4, 2)
                    return self.order_corners(corners)
        
        return None
    
    def detect_contour_corners(self, image):
        """Method 2: General contour-based detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptive threshold for better edge detection
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio
        candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000:  # Too small
                continue
                
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Look for roughly square/rectangular shapes
            if 0.5 < aspect_ratio < 2.0:
                # Approximate to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:
                    candidates.append((area, approx.reshape(4, 2)))
        
        # Return largest valid candidate
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return self.order_corners(candidates[0][1])
        
        return None
    
    def detect_harris_corners(self, image):
        """Method 3: Harris corner detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        
        # Harris corner detection
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        
        # Dilate corner image to enhance corner points
        corners = cv2.dilate(corners, None)
        
        # Threshold for an optimal value
        threshold = 0.01 * corners.max()
        corner_points = np.where(corners > threshold)
        
        if len(corner_points[0]) < 4:
            return None
        
        # Convert to (x, y) coordinates
        points = list(zip(corner_points[1], corner_points[0]))
        
        # Find the 4 extreme corners
        if len(points) >= 4:
            points = np.array(points)
            
            # Find corners of bounding box
            top_left = points[np.argmin(points[:, 0] + points[:, 1])]
            top_right = points[np.argmax(points[:, 0] - points[:, 1])]
            bottom_right = points[np.argmax(points[:, 0] + points[:, 1])]
            bottom_left = points[np.argmin(points[:, 0] - points[:, 1])]
            
            corners = np.array([top_left, top_right, bottom_right, bottom_left])
            return corners
        
        return None
    
    def detect_edge_corners(self, image):
        """Method 4: Edge-based corner detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Edge detection with different parameters
        edges = cv2.Canny(filtered, 30, 80, apertureSize=3)
        
        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is None or len(lines) < 4:
            return None
        
        # Find intersection points of lines (corners)
        intersections = []
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                intersection = self.line_intersection(lines[i][0], lines[j][0])
                if intersection is not None:
                    intersections.append(intersection)
        
        if len(intersections) >= 4:
            # Cluster nearby intersections and find 4 main corners
            intersections = np.array(intersections)
            
            # Simple clustering: find 4 most distant points
            corners = self.find_corner_candidates(intersections, image.shape)
            if len(corners) == 4:
                return self.order_corners(np.array(corners))
        
        return None
    
    def line_intersection(self, line1, line2):
        """Find intersection point of two lines in polar form"""
        rho1, theta1 = line1
        rho2, theta2 = line2
        
        # Convert to cartesian form
        A = np.array([[np.cos(theta1), np.sin(theta1)],
                      [np.cos(theta2), np.sin(theta2)]])
        b = np.array([[rho1], [rho2]])
        
        try:
            intersection = np.linalg.solve(A, b)
            return intersection.flatten()
        except np.linalg.LinAlgError:
            return None
    
    def find_corner_candidates(self, points, image_shape):
        """Find 4 corner candidates from intersection points"""
        h, w = image_shape[:2]
        
        # Filter points within image bounds
        valid_points = []
        for point in points:
            x, y = point
            if 0 <= x < w and 0 <= y < h:
                valid_points.append(point)
        
        if len(valid_points) < 4:
            return []
        
        valid_points = np.array(valid_points)
        
        # Find extreme points
        top_left = valid_points[np.argmin(valid_points[:, 0] + valid_points[:, 1])]
        top_right = valid_points[np.argmax(valid_points[:, 0] - valid_points[:, 1])]
        bottom_right = valid_points[np.argmax(valid_points[:, 0] + valid_points[:, 1])]
        bottom_left = valid_points[np.argmin(valid_points[:, 0] - valid_points[:, 1])]
        
        return [top_left, top_right, bottom_right, bottom_left]
    
    def order_corners(self, corners):
        """Order corners as: top-left, top-right, bottom-right, bottom-left"""
        # Calculate centroid
        center = np.mean(corners, axis=0)
        
        # Sort by angle from center
        def angle_from_center(point):
            return np.arctan2(point[1] - center[1], point[0] - center[0])
        
        # Sort corners by angle
        sorted_indices = np.argsort([angle_from_center(corner) for corner in corners])
        sorted_corners = corners[sorted_indices]
        
        # Ensure correct order: TL, TR, BR, BL
        # Find top-left (minimum x+y)
        tl_idx = np.argmin(sorted_corners[:, 0] + sorted_corners[:, 1])
        
        # Reorder starting from top-left
        ordered = np.roll(sorted_corners, -tl_idx, axis=0)
        
        return ordered
    
    def correct_perspective(self, image, corners):
        """Apply perspective correction using detected corners"""
        # Define output size (square for better watermark detection)
        output_size = 1024
        
        # Destination points (square)
        dst_points = np.float32([
            [0, 0],                           # top-left
            [output_size, 0],                 # top-right
            [output_size, output_size],       # bottom-right
            [0, output_size]                  # bottom-left
        ])
        
        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(corners.astype(np.float32), dst_points)
        
        # Apply perspective correction
        corrected = cv2.warpPerspective(image, matrix, (output_size, output_size))
        
        return corrected
    
    def decode_watermark(self, corrected_image):
        """Decode watermark from perspective-corrected image"""
        try:
            # Convert to PIL Image
            rgb_image = cv2.cvtColor(corrected_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Decode watermark
            secret_id, present, confidence = self.tm.decode(pil_image)
            
            if present:
                return {
                    'success': True,
                    'watermark_id': secret_id,
                    'confidence': confidence
                }
            else:
                return {
                    'success': False,
                    'error': 'No watermark detected'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Decoding error: {str(e)}'
            }
    
    def visualize_detection(self, image_path, output_path=None):
        """Visualize the corner detection process (for debugging)"""
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Try each method and visualize
        methods = [
            self.detect_document_corners,
            self.detect_contour_corners,
            self.detect_harris_corners,
            self.detect_edge_corners
        ]
        
        results = []
        for method in methods:
            corners = method(image.copy())
            if corners is not None:
                # Draw corners on image
                vis_image = image.copy()
                for i, corner in enumerate(corners):
                    cv2.circle(vis_image, tuple(corner.astype(int)), 10, (0, 255, 0), -1)
                    cv2.putText(vis_image, str(i), tuple(corner.astype(int)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                results.append({
                    'method': method.__name__,
                    'corners': corners,
                    'image': vis_image
                })
        
        return results

# Integration with existing YYS-SQR system
def integrate_auto_detection(main_app):
    """Integrate automatic corner detection into the main YYS-SQR app"""
    
    def auto_decode_watermark(image_path):
        """Replace manual corner selection with automatic detection"""
        detector = AutoCornerDetector()
        result = detector.detect_and_decode(image_path)
        return result
    
    # This would replace the manual corner selection in main.py
    return auto_decode_watermark

# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_corner_detection.py <image_path> [--visualize]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    detector = AutoCornerDetector()
    
    if "--visualize" in sys.argv:
        # Visualization mode
        results = detector.visualize_detection(image_path)
        if results:
            for i, result in enumerate(results):
                cv2.imshow(f"Method {i+1}: {result['method']}", result['image'])
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        # Normal detection mode
        result = detector.detect_and_decode(image_path)
        print(json.dumps(result, indent=2))