#!/usr/bin/env python3
"""
Minimal YYS-SQR server for Render deployment
Only includes essential functionality to get started
"""
import os
import tempfile
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

print("🚀 Starting Minimal YYS-SQR Server...")

# Try to import optional components
detector = None
tm = None

try:
    print("📦 Loading auto corner detection...")
    from auto_corner_detection import AutoCornerDetector
    detector = AutoCornerDetector()
    print("✅ AutoCornerDetector loaded")
except Exception as e:
    print(f"⚠️  AutoCornerDetector not available: {e}")

try:
    print("📦 Loading TrustMark...")
    import trustmark
    tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    print("✅ TrustMark loaded")
except Exception as e:
    print(f"⚠️  TrustMark not available: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Root endpoint with status"""
    return jsonify({
        'message': '🎉 YYS-SQR Minimal API is running on Render!',
        'version': '1.0.0',
        'status': 'healthy',
        'components': {
            'auto_corner_detection': detector is not None,
            'trustmark_watermarking': tm is not None,
            'basic_image_processing': True
        },
        'endpoints': ['/api/health', '/api/scan', '/api/embed', '/api/docs'],
        'note': 'This is a minimal deployment. Full features available when all components load.'
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'auto_corner_detection': detector is not None,
            'trustmark_watermarking': tm is not None
        },
        'ready': True  # Always ready, even with limited functionality
    })

@app.route('/api/scan', methods=['POST'])
def scan():
    """Scan endpoint - works with or without full detection"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        if not detector:
            return jsonify({
                'success': False,
                'error': 'Auto corner detection not available in this deployment',
                'suggestion': 'Use manual corner selection or upgrade deployment',
                'timestamp': datetime.now().isoformat()
            })
        
        # Decode image
        image_data = base64.b64decode(data['image'])
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            # Full auto corner detection
            result = detector.detect_and_decode(temp_path)
            result['timestamp'] = datetime.now().isoformat()
            return jsonify(result)
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Scan failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/embed', methods=['POST'])
def embed():
    """Embed endpoint - works with or without trustmark"""
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message'}), 400
        
        if not tm:
            return jsonify({
                'success': False,
                'error': 'Watermark embedding not available in this deployment',
                'suggestion': 'Upgrade deployment to include TrustMark',
                'timestamp': datetime.now().isoformat()
            })
        
        message = str(data['message']).strip()
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 chars)'}), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Embed watermark
        watermarked = tm.encode(image, message)
        
        # Convert back to base64
        buffer = io.BytesIO()
        watermarked.save(buffer, format='PNG')
        result_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'watermarked_image': result_b64,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Embed failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test', methods=['POST'])
def test():
    """Simple test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'timestamp': datetime.now().isoformat(),
        'components_available': {
            'detection': detector is not None,
            'embedding': tm is not None
        }
    })

@app.route('/api/docs')
def docs():
    """API documentation"""
    return jsonify({
        'title': 'YYS-SQR Minimal API',
        'version': '1.0.0',
        'description': 'Lightweight watermarking API for Render deployment',
        'endpoints': {
            'GET /': 'API status',
            'GET /api/health': 'Health check',
            'POST /api/scan': 'Scan watermark (requires full deployment)',
            'POST /api/embed': 'Embed watermark (requires full deployment)',
            'POST /api/test': 'Test API functionality',
            'GET /api/docs': 'This documentation'
        },
        'deployment_notes': [
            'This is a minimal deployment that gracefully handles missing components',
            'Full functionality requires PyTorch and OpenCV dependencies',
            'Basic image processing always available'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting server on port {port}")
    print(f"🎯 Components: detector={detector is not None}, tm={tm is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)