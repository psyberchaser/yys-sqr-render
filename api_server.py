# YYS-SQR API Server
# REST API for watermark embedding and automatic scanning

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import base64
from PIL import Image
import io
import json
from datetime import datetime

# Import our modules
from auto_corner_detection import AutoCornerDetector
import trustmark

app = Flask(__name__)
CORS(app)  # Enable CORS for web apps

# Initialize components
detector = AutoCornerDetector()
tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/embed', methods=['POST'])
def embed_watermark():
    """Embed watermark in image"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Validate message length
        message = data['message']
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 characters)'}), 400
        
        # Embed watermark
        watermarked_image = tm.encode(image, message)
        
        # Convert back to base64
        buffer = io.BytesIO()
        watermarked_image.save(buffer, format='PNG')
        watermarked_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'watermarked_image': watermarked_b64,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def scan_watermark():
    """Automatically scan watermark from image"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'image' not in data:
            return jsonify({'error': 'Missing image'}), 400
        
        # Decode base64 image and save temporarily
        image_data = base64.b64decode(data['image'])
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # Perform automatic detection and decoding
            result = detector.detect_and_decode(temp_path)
            
            # Add API-specific metadata
            result['api_version'] = '1.0.0'
            result['timestamp'] = datetime.now().isoformat()
            
            return jsonify(result)
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/batch', methods=['POST'])
def batch_scan():
    """Scan multiple images at once"""
    try:
        data = request.get_json()
        
        if 'images' not in data or not isinstance(data['images'], list):
            return jsonify({'error': 'Missing images array'}), 400
        
        results = []
        
        for i, image_b64 in enumerate(data['images']):
            try:
                # Decode and save temporarily
                image_data = base64.b64decode(image_b64)
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(image_data)
                    temp_path = temp_file.name
                
                try:
                    # Scan image
                    result = detector.detect_and_decode(temp_path)
                    result['image_index'] = i
                    results.append(result)
                    
                finally:
                    os.unlink(temp_path)
                    
            except Exception as e:
                results.append({
                    'image_index': i,
                    'error': str(e),
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_images': len(data['images']),
            'successful_scans': len([r for r in results if r.get('success', False)]),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/capacity', methods=['GET'])
def get_capacity():
    """Get watermark capacity information"""
    try:
        capacity_bits = tm.schemaCapacity()
        capacity_chars = capacity_bits // 7  # ASCII7 encoding
        
        return jsonify({
            'capacity_bits': capacity_bits,
            'capacity_characters': capacity_chars,
            'encoding': 'BCH_SUPER',
            'model_type': 'Q'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/methods', methods=['GET'])
def get_detection_methods():
    """Get available detection methods"""
    return jsonify({
        'methods': [
            {
                'name': 'document_corners',
                'description': 'Best for printed documents and papers',
                'recommended_for': ['printed_images', 'documents', 'photos_of_papers']
            },
            {
                'name': 'contour_corners', 
                'description': 'General contour-based detection',
                'recommended_for': ['digital_images', 'screenshots', 'clear_boundaries']
            },
            {
                'name': 'harris_corners',
                'description': 'Harris corner detection algorithm',
                'recommended_for': ['complex_images', 'multiple_objects']
            },
            {
                'name': 'edge_corners',
                'description': 'Edge-based corner detection',
                'recommended_for': ['high_contrast_images', 'geometric_shapes']
            }
        ],
        'default_order': ['document_corners', 'contour_corners', 'harris_corners', 'edge_corners']
    })

@app.route('/api/scan/visualize', methods=['POST'])
def visualize_detection():
    """Visualize the corner detection process"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Missing image'}), 400
        
        # Decode image and save temporarily
        image_data = base64.b64decode(data['image'])
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # Get visualization results
            vis_results = detector.visualize_detection(temp_path)
            
            if not vis_results:
                return jsonify({'error': 'No corners detected by any method'}), 404
            
            # Convert visualization images to base64
            response_data = []
            for result in vis_results:
                # Convert OpenCV image to base64
                _, buffer = cv2.imencode('.png', result['image'])
                img_b64 = base64.b64encode(buffer).decode()
                
                response_data.append({
                    'method': result['method'],
                    'corners': result['corners'].tolist(),
                    'visualization': img_b64
                })
            
            return jsonify({
                'success': True,
                'visualizations': response_data,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            os.unlink(temp_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        'title': 'YYS-SQR API',
        'version': '1.0.0',
        'description': 'REST API for watermark embedding and automatic scanning',
        'endpoints': {
            'GET /api/health': 'Health check',
            'POST /api/embed': 'Embed watermark in image',
            'POST /api/scan': 'Automatically scan watermark from image',
            'POST /api/scan/batch': 'Scan multiple images',
            'GET /api/capacity': 'Get watermark capacity info',
            'GET /api/methods': 'Get detection methods',
            'POST /api/scan/visualize': 'Visualize corner detection',
            'GET /api/docs': 'This documentation'
        },
        'examples': {
            'embed': {
                'method': 'POST',
                'url': '/api/embed',
                'body': {
                    'image': 'base64_encoded_image_data',
                    'message': 'HELLO'
                }
            },
            'scan': {
                'method': 'POST', 
                'url': '/api/scan',
                'body': {
                    'image': 'base64_encoded_image_data'
                }
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("🚀 Starting YYS-SQR API Server...")
    print("📖 API Documentation: http://localhost:5000/api/docs")
    print("❤️  Health Check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)