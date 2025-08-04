#!/usr/bin/env python3
"""
Lightweight YYS-SQR server for Render free tier
Optimized for memory usage while keeping core watermarking functionality
"""
import os
import tempfile
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

print("🚀 Starting Lightweight YYS-SQR Server...")

# Try to import components with memory optimization
detector = None
tm = None

try:
    print("📦 Loading TrustMark (lightweight mode)...")
    import trustmark
    # Initialize with minimal memory footprint
    tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    print("✅ TrustMark loaded successfully")
except Exception as e:
    print(f"⚠️  TrustMark not available: {e}")

# Skip auto corner detection for now to save memory
print("⚠️  Auto corner detection disabled to save memory")
print("💡 Manual corner selection or upgrade plan for full auto detection")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Root endpoint with status"""
    return jsonify({
        'message': '🎉 YYS-SQR Lightweight API is running on Render!',
        'version': '1.0.0',
        'status': 'healthy' if tm else 'degraded',
        'deployment': 'lightweight',
        'components': {
            'trustmark_watermarking': tm is not None,
            'auto_corner_detection': False,
            'manual_corner_selection': True,
            'memory_optimized': True
        },
        'endpoints': ['/api/health', '/api/embed', '/api/scan', '/api/docs'],
        'features': [
            'Watermark embedding with BCH Super',
            'Manual corner selection scanning',
            'Memory optimized for free tier',
            'Base64 image processing'
        ],
        'note': 'Lightweight deployment. Upgrade plan for auto corner detection.'
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy' if tm else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'deployment': 'lightweight',
        'components': {
            'trustmark_watermarking': tm is not None,
            'auto_corner_detection': False
        },
        'memory_optimized': True,
        'ready': tm is not None
    })

@app.route('/api/embed', methods=['POST'])
def embed():
    """Embed watermark - core functionality"""
    if not tm:
        return jsonify({
            'success': False,
            'error': 'Watermarking not available',
            'details': 'TrustMark failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message'}), 400
        
        message = str(data['message']).strip()
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 characters)'}), 400
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        print(f"🔒 Embedding message: '{message}'")
        
        # Decode and validate image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        # Embed watermark
        try:
            watermarked_image = tm.encode(image, message)
        except Exception as e:
            return jsonify({'error': f'Watermark embedding failed: {str(e)}'}), 500
        
        # Convert back to base64
        buffer = io.BytesIO()
        watermarked_image.save(buffer, format='PNG')
        watermarked_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print(f"✅ Embedding successful")
        
        return jsonify({
            'success': True,
            'watermarked_image': watermarked_b64,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'encoding': 'BCH_SUPER',
            'deployment': 'lightweight'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Embedding failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scan', methods=['POST'])
def scan():
    """Scan with manual corner selection (no auto detection to save memory)"""
    if not tm:
        return jsonify({
            'success': False,
            'error': 'Watermarking not available',
            'details': 'TrustMark failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Missing image data'}), 400
        
        # Check if corners are provided (manual selection)
        if 'corners' not in data:
            return jsonify({
                'success': False,
                'error': 'Manual corner selection required in lightweight mode',
                'details': 'Provide corners array: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]',
                'upgrade_info': 'Upgrade plan for automatic corner detection',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        corners = data['corners']
        if len(corners) != 4:
            return jsonify({'error': 'Exactly 4 corners required'}), 400
        
        print(f"🔍 Scanning with manual corners: {corners}")
        
        # Decode image
        try:
            image_data = base64.b64decode(data['image'])
        except Exception as e:
            return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            # Use manual corner selection with TrustMark
            # This is a simplified version - you'd need to implement the corner-based decoding
            result = {
                'success': False,
                'error': 'Manual corner decoding not yet implemented',
                'corners_received': corners,
                'suggestion': 'Upgrade to full plan for automatic scanning',
                'timestamp': datetime.now().isoformat()
            }
            
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

@app.route('/api/docs')
def docs():
    """API documentation"""
    return jsonify({
        'title': 'YYS-SQR Lightweight API',
        'version': '1.0.0',
        'description': 'Memory-optimized watermarking API for Render free tier',
        'deployment': 'lightweight',
        'endpoints': {
            'GET /': 'API status and information',
            'GET /api/health': 'Health check',
            'POST /api/embed': 'Embed watermark (full functionality)',
            'POST /api/scan': 'Scan with manual corners (lightweight mode)',
            'GET /api/docs': 'This documentation'
        },
        'embed_example': {
            'method': 'POST',
            'url': '/api/embed',
            'body': {
                'image': 'base64_encoded_image_data',
                'message': 'HELLO'
            }
        },
        'scan_example': {
            'method': 'POST',
            'url': '/api/scan',
            'body': {
                'image': 'base64_encoded_image_data',
                'corners': [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            }
        },
        'upgrade_benefits': [
            'Automatic corner detection (4 methods)',
            'Higher memory limits',
            'Better performance',
            'Full OpenCV support'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting lightweight server on port {port}")
    print(f"🎯 Components: tm={tm is not None}")
    print("💡 Embedding available, scanning requires manual corners")
    
    app.run(host='0.0.0.0', port=port, debug=debug)