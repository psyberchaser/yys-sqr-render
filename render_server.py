# YYS-SQR Render Production Server
import os
import tempfile
import base64
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Starting YYS-SQR on Render...")

# Import our modules with detailed error handling
detector = None
tm = None

try:
    print("📦 Loading auto corner detection...")
    from auto_corner_detection import AutoCornerDetector
    detector = AutoCornerDetector()
    print("✅ AutoCornerDetector loaded successfully")
except Exception as e:
    print(f"❌ AutoCornerDetector failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("📦 Loading TrustMark...")
    import trustmark
    tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    print("✅ TrustMark loaded successfully")
except Exception as e:
    print(f"❌ TrustMark failed: {e}")
    import traceback
    traceback.print_exc()

app = Flask(__name__)
CORS(app)

# Configure for production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/')
def home():
    """Root endpoint with full status"""
    return jsonify({
        'message': '🎉 YYS-SQR API is running on Render!',
        'version': '1.0.0',
        'status': 'healthy' if (detector and tm) else 'degraded',
        'components': {
            'auto_corner_detection': detector is not None,
            'trustmark_watermarking': tm is not None,
            'opencv': 'opencv-python-headless' in str(detector.__class__) if detector else False,
            'flask': True,
            'cors': True
        },
        'endpoints': {
            'health': '/api/health',
            'scan': '/api/scan (POST)',
            'embed': '/api/embed (POST)', 
            'capacity': '/api/capacity',
            'docs': '/api/docs'
        },
        'features': [
            'Automatic corner detection',
            'BCH Super error correction',
            'Mobile-optimized scanning',
            'Base64 image processing'
        ]
    })

@app.route('/api/health')
def health():
    """Detailed health check"""
    components = {
        'auto_corner_detection': detector is not None,
        'trustmark_watermarking': tm is not None
    }
    
    # Test basic functionality
    try:
        if tm:
            capacity = tm.schemaCapacity()
            components['watermark_capacity'] = f"{capacity} bits"
    except:
        pass
    
    status = 'healthy' if all([detector, tm]) else 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': components,
        'ready': detector is not None and tm is not None
    }), 200 if status == 'healthy' else 503

@app.route('/api/scan/manual', methods=['POST'])
def scan_manual():
    """Scan watermark with manual corner selection (like desktop app)"""
    if not tm:
        return jsonify({
            'error': 'Watermarking service not available',
            'details': 'TrustMark failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'corners' not in data:
            return jsonify({'error': 'Missing image or corners data'}), 400
        
        corners = data['corners']
        if len(corners) != 4:
            return jsonify({'error': 'Exactly 4 corners required'}), 400
        
        logger.info(f"🔍 Manual scan with corners: {corners}")
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'])
            logger.info(f"📊 Image size: {len(image_data)} bytes")
        except Exception as e:
            return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            # Load image with OpenCV
            import cv2
            import numpy as np
            from PIL import Image as PILImage
            
            image = cv2.imread(temp_path)
            if image is None:
                return jsonify({'error': 'Could not load image'}), 400
            
            # Convert corners to numpy array
            coordinates = np.float32(corners)
            
            # Define output size (same as desktop app)
            output_width, output_height = 1024, 1024
            destination_points = np.float32([
                [0, 0], 
                [output_width, 0], 
                [output_width, output_height], 
                [0, output_height]
            ])
            
            # Apply perspective transformation
            matrix = cv2.getPerspectiveTransform(coordinates, destination_points)
            corrected_image_cv = cv2.warpPerspective(image, matrix, (output_width, output_height))
            
            # Convert to RGB for TrustMark
            corrected_image_rgb = cv2.cvtColor(corrected_image_cv, cv2.COLOR_BGR2RGB)
            image_to_decode = PILImage.fromarray(corrected_image_rgb)
            
            # Decode watermark
            secret_id, present, _ = tm.decode(image_to_decode)
            
            if present:
                logger.info(f"✅ Manual scan successful: {secret_id}")
                return jsonify({
                    'success': True,
                    'watermark_id': secret_id,
                    'method': 'manual_corner_selection',
                    'corners': corners,
                    'timestamp': datetime.now().isoformat(),
                    'server': 'render'
                })
            else:
                logger.info("❌ No watermark found with manual corners")
                return jsonify({
                    'success': False,
                    'error': 'No watermark detected',
                    'details': 'Check corner selection - ensure corners are on the watermarked area',
                    'method': 'manual_corner_selection',
                    'corners': corners,
                    'timestamp': datetime.now().isoformat()
                })
            
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"💥 Manual scan error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal scan error',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scan', methods=['POST'])
def scan():
    """Scan watermark with full auto corner detection"""
    if not detector:
        return jsonify({
            'error': 'Auto corner detection not available',
            'details': 'The corner detection system failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        logger.info("📷 Processing scan request...")
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'])
            logger.info(f"📊 Image size: {len(image_data)} bytes")
        except Exception as e:
            return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            logger.info("🔍 Running auto corner detection...")
            # This is the full auto corner detection with all 4 methods
            result = detector.detect_and_decode(temp_path)
            
            # Add API metadata
            result['api_version'] = '1.0.0'
            result['timestamp'] = datetime.now().isoformat()
            result['server'] = 'render'
            
            if result.get('success'):
                logger.info(f"✅ Scan successful: {result.get('watermark_id')}")
            else:
                logger.info(f"❌ No watermark found: {result.get('error', 'Unknown error')}")
            
            return jsonify(result)
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"💥 Scan error: {e}")
        return jsonify({
            'error': 'Internal scan error',
            'details': str(e),
            'success': False
        }), 500

@app.route('/api/embed', methods=['POST'])
def embed():
    """Embed watermark with full TrustMark functionality"""
    if not tm:
        return jsonify({
            'error': 'Watermarking not available',
            'details': 'TrustMark failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message data'}), 400
        
        message = str(data['message']).strip()
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 characters)'}), 400
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"🔒 Embedding message: '{message}'")
        
        # Decode and validate image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            logger.info(f"📊 Image size: {image.size}")
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        # Embed watermark using full TrustMark with BCH_SUPER
        try:
            watermarked_image = tm.encode(image, message)
        except Exception as e:
            logger.error(f"💥 Embedding error: {e}")
            return jsonify({'error': f'Watermark embedding failed: {str(e)}'}), 500
        
        # Convert back to base64
        buffer = io.BytesIO()
        watermarked_image.save(buffer, format='PNG')
        watermarked_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"✅ Embedding successful")
        
        return jsonify({
            'success': True,
            'watermarked_image': watermarked_b64,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'encoding': 'BCH_SUPER',
            'server': 'render'
        })
        
    except Exception as e:
        logger.error(f"💥 Embed error: {e}")
        return jsonify({
            'error': 'Internal embedding error',
            'details': str(e),
            'success': False
        }), 500

@app.route('/api/capacity')
def capacity():
    """Get full watermark capacity information"""
    if not tm:
        return jsonify({'error': 'Watermarking not available'}), 503
    
    try:
        capacity_bits = tm.schemaCapacity()
        capacity_chars = capacity_bits // 7  # ASCII7 encoding
        
        return jsonify({
            'capacity_bits': capacity_bits,
            'capacity_characters': capacity_chars,
            'encoding': 'BCH_SUPER',
            'model_type': 'Q',
            'max_message_length': 5,
            'error_correction': 'Maximum (BCH Super)',
            'recommended_use': 'Short identifiers, codes, or references'
        })
        
    except Exception as e:
        logger.error(f"💥 Capacity error: {e}")
        return jsonify({'error': f'Capacity check failed: {str(e)}'}), 500

@app.route('/api/docs')
def docs():
    """Complete API documentation"""
    return jsonify({
        'title': 'YYS-SQR Production API',
        'version': '1.0.0',
        'description': 'Advanced watermarking with automatic corner detection',
        'server': 'Render',
        'features': [
            'Automatic corner detection (4 methods)',
            'BCH Super error correction',
            'Mobile-optimized scanning',
            'High-quality watermark embedding'
        ],
        'endpoints': {
            'GET /': 'API status and information',
            'GET /api/health': 'Health check with component status',
            'POST /api/scan': 'Scan watermark with auto corner detection',
            'POST /api/embed': 'Embed watermark with BCH Super encoding',
            'GET /api/capacity': 'Get watermark capacity information',
            'GET /api/docs': 'This documentation'
        },
        'scan_methods': [
            'document_corners - Best for printed images',
            'contour_corners - General purpose detection', 
            'harris_corners - Complex image detection',
            'edge_corners - High contrast detection'
        ],
        'limits': {
            'max_file_size': '16MB',
            'max_message_length': '5 characters',
            'supported_formats': ['PNG', 'JPG', 'JPEG']
        }
    })

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"💥 Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render uses port 10000
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🌐 Starting server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🎯 Components ready: detector={detector is not None}, tm={tm is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)