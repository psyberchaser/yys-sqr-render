#!/usr/bin/env python3
"""
Basic YYS-SQR server for Render - No heavy dependencies
"""
import os
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

print("🚀 Starting Basic YYS-SQR Server...")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'message': '🎉 YYS-SQR Basic API is running on Render!',
        'version': '1.0.0',
        'status': 'healthy',
        'deployment': 'basic',
        'endpoints': ['/api/health', '/api/test', '/api/docs'],
        'features': [
            'Basic image processing',
            'API framework ready',
            'CORS enabled',
            'Health monitoring'
        ],
        'note': 'This is a basic deployment. Watermarking features can be added with full dependencies.'
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'deployment': 'basic',
        'ready': True
    })

@app.route('/api/test', methods=['POST'])
def test():
    """Test endpoint with image processing"""
    try:
        data = request.get_json()
        
        if data and 'image' in data:
            # Test basic image processing
            try:
                image_data = base64.b64decode(data['image'])
                image = Image.open(io.BytesIO(image_data))
                
                return jsonify({
                    'success': True,
                    'message': 'Image processing test successful!',
                    'image_info': {
                        'size': image.size,
                        'mode': image.mode,
                        'format': image.format
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Image processing failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        else:
            return jsonify({
                'success': True,
                'message': 'Basic API test successful!',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scan', methods=['POST'])
def scan():
    """Placeholder scan endpoint"""
    return jsonify({
        'success': False,
        'error': 'Watermark scanning not available in basic deployment',
        'upgrade_info': 'Deploy with full requirements.txt for scanning functionality',
        'timestamp': datetime.now().isoformat()
    }), 503

@app.route('/api/embed', methods=['POST'])
def embed():
    """Placeholder embed endpoint"""
    return jsonify({
        'success': False,
        'error': 'Watermark embedding not available in basic deployment',
        'upgrade_info': 'Deploy with full requirements.txt for embedding functionality',
        'timestamp': datetime.now().isoformat()
    }), 503

@app.route('/api/docs')
def docs():
    """API documentation"""
    return jsonify({
        'title': 'YYS-SQR Basic API',
        'version': '1.0.0',
        'description': 'Basic deployment ready for watermarking features',
        'deployment': 'basic',
        'endpoints': {
            'GET /': 'API status and information',
            'GET /api/health': 'Health check',
            'POST /api/test': 'Test API and basic image processing',
            'POST /api/scan': 'Watermark scanning (requires upgrade)',
            'POST /api/embed': 'Watermark embedding (requires upgrade)',
            'GET /api/docs': 'This documentation'
        },
        'upgrade_path': {
            'step1': 'Use requirements.txt instead of requirements-minimal.txt',
            'step2': 'Include trustmark models in deployment',
            'step3': 'Switch to render_server.py for full functionality'
        },
        'test_example': {
            'method': 'POST',
            'url': '/api/test',
            'body': {
                'image': 'base64_encoded_image_data (optional)'
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting basic server on port {port}")
    print("✅ Ready for connections!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)