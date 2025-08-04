# YYS-SQR Production API Server
# Optimized for cloud deployment with proper error handling and monitoring

import os
import tempfile
import base64
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Sentry for error tracking (optional)
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

# Import our modules
try:
    from auto_corner_detection import AutoCornerDetector
    import trustmark
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    AutoCornerDetector = None
    trustmark = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Production configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-change-this'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    JSON_SORT_KEYS=False
)

# Initialize components
detector = None
tm = None

def initialize_components():
    """Initialize watermarking components with error handling"""
    global detector, tm
    
    try:
        if AutoCornerDetector:
            detector = AutoCornerDetector()
            logger.info("AutoCornerDetector initialized successfully")
        else:
            logger.error("AutoCornerDetector not available")
            
        if trustmark:
            tm = trustmark.TrustMark(
                verbose=False, 
                encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER
            )
            logger.info("TrustMark initialized successfully")
        else:
            logger.error("TrustMark not available")
            
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")

# Initialize on startup
initialize_components()

@app.before_request
def log_request_info():
    """Log incoming requests"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response status"""
    logger.info(f"Response: {response.status_code}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with component status"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': {
            'detector': detector is not None,
            'trustmark': tm is not None,
        }
    }
    
    # Check if critical components are available
    if not detector or not tm:
        status['status'] = 'degraded'
        return jsonify(status), 503
    
    return jsonify(status)

@app.route('/api/embed', methods=['POST'])
def embed_watermark():
    """Embed watermark in image with enhanced error handling"""
    try:
        if not tm:
            return jsonify({'error': 'Watermarking service not available'}), 503
            
        data = request.get_json()
        
        # Validate input
        if not data or 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message'}), 400
        
        # Validate message length
        message = str(data['message']).strip()
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 characters)'}), 400
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Decode and validate base64 image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            logger.error(f"Image decode error: {e}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Embed watermark
        try:
            watermarked_image = tm.encode(image, message)
        except Exception as e:
            logger.error(f"Watermark embedding error: {e}")
            return jsonify({'error': 'Failed to embed watermark'}), 500
        
        # Convert back to base64
        buffer = io.BytesIO()
        watermarked_image.save(buffer, format='PNG')
        watermarked_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"Successfully embedded watermark with message: {message}")
        
        return jsonify({
            'success': True,
            'watermarked_image': watermarked_b64,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Embed watermark error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/scan', methods=['POST'])
def scan_watermark():
    """Automatically scan watermark from image with enhanced error handling"""
    try:
        if not detector:
            return jsonify({'error': 'Corner detection service not available'}), 503
            
        data = request.get_json()
        
        # Validate input
        if not data or 'image' not in data:
            return jsonify({'error': 'Missing image data'}), 400
        
        # Decode and validate base64 image
        try:
            image_data = base64.b64decode(data['image'])
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return jsonify({'error': 'Invalid base64 image data'}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # Perform automatic detection and decoding
            result = detector.detect_and_decode(temp_path)
            
            # Add API-specific metadata
            result['api_version'] = '1.0.0'
            result['timestamp'] = datetime.now().isoformat()
            
            if result.get('success'):
                logger.info(f"Successfully scanned watermark: {result.get('watermark_id')}")
            else:
                logger.info(f"No watermark found: {result.get('error')}")
            
            return jsonify(result)
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"Scan watermark error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/scan/batch', methods=['POST'])
def batch_scan():
    """Scan multiple images with rate limiting"""
    try:
        if not detector:
            return jsonify({'error': 'Corner detection service not available'}), 503
            
        data = request.get_json()
        
        if not data or 'images' not in data or not isinstance(data['images'], list):
            return jsonify({'error': 'Missing images array'}), 400
        
        # Limit batch size
        if len(data['images']) > 10:
            return jsonify({'error': 'Batch size limited to 10 images'}), 400
        
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
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
            except Exception as e:
                logger.error(f"Batch scan error for image {i}: {e}")
                results.append({
                    'image_index': i,
                    'error': str(e),
                    'success': False
                })
        
        successful_scans = len([r for r in results if r.get('success', False)])
        logger.info(f"Batch scan completed: {successful_scans}/{len(data['images'])} successful")
        
        return jsonify({
            'success': True,
            'results': results,
            'total_images': len(data['images']),
            'successful_scans': successful_scans,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch scan error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/capacity', methods=['GET'])
def get_capacity():
    """Get watermark capacity information"""
    try:
        if not tm:
            return jsonify({'error': 'Watermarking service not available'}), 503
            
        capacity_bits = tm.schemaCapacity()
        capacity_chars = capacity_bits // 7  # ASCII7 encoding
        
        return jsonify({
            'capacity_bits': capacity_bits,
            'capacity_characters': capacity_chars,
            'encoding': 'BCH_SUPER',
            'model_type': 'Q'
        })
        
    except Exception as e:
        logger.error(f"Capacity check error: {e}")
        return jsonify({'error': 'Failed to get capacity information'}), 500

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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        'title': 'YYS-SQR Production API',
        'version': '1.0.0',
        'description': 'Production REST API for watermark embedding and automatic scanning',
        'base_url': request.base_url.replace('/api/docs', ''),
        'endpoints': {
            'GET /api/health': 'Health check with component status',
            'POST /api/embed': 'Embed watermark in image',
            'POST /api/scan': 'Automatically scan watermark from image',
            'POST /api/scan/batch': 'Scan multiple images (max 10)',
            'GET /api/capacity': 'Get watermark capacity info',
            'GET /api/methods': 'Get detection methods',
            'GET /api/docs': 'This documentation'
        },
        'rate_limits': {
            'batch_scan': '10 images per request',
            'file_size': '16MB maximum'
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting YYS-SQR API server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    if debug:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Use gunicorn in production
        import gunicorn.app.base
        
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 2,
            'worker_class': 'sync',
            'timeout': 120,
            'keepalive': 2,
            'max_requests': 1000,
            'max_requests_jitter': 100,
            'preload_app': True,
        }
        
        StandaloneApplication(app, options).run()