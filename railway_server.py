# YYS-SQR Railway Server - Simplified
import os
import tempfile
import base64
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

print("🚀 Starting YYS-SQR Railway Server...")

# Import our modules with error handling
detector = None
tm = None

try:
    from auto_corner_detection import AutoCornerDetector
    detector = AutoCornerDetector()
    print("✅ AutoCornerDetector loaded")
except Exception as e:
    print(f"❌ AutoCornerDetector failed: {e}")

try:
    import trustmark
    tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    print("✅ TrustMark loaded")
except Exception as e:
    print(f"❌ TrustMark failed: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': '🎉 YYS-SQR API is running on Railway!',
        'version': '1.0.0',
        'status': 'healthy',
        'components': {
            'detector': detector is not None,
            'trustmark': tm is not None
        },
        'endpoints': ['/api/health', '/api/scan', '/api/embed', '/api/capacity']
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy' if (detector and tm) else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'detector': detector is not None,
            'trustmark': tm is not None
        }
    })

@app.route('/api/scan', methods=['POST'])
def scan():
    if not detector:
        return jsonify({'error': 'Scanner not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'])
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            # Scan with auto corner detection
            result = detector.detect_and_decode(temp_path)
            result['timestamp'] = datetime.now().isoformat()
            return jsonify(result)
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/api/embed', methods=['POST'])
def embed():
    if not tm:
        return jsonify({'error': 'Embedder not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'message' not in data:
            return jsonify({'error': 'Missing image or message'}), 400
        
        message = str(data['message']).strip()
        if len(message) > 5:
            return jsonify({'error': 'Message too long (max 5 chars)'}), 400
        
        # Decode and process image
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
        return jsonify({'error': f'Embed failed: {str(e)}'}), 500

@app.route('/api/capacity')
def capacity():
    if not tm:
        return jsonify({'error': 'Capacity check not available'}), 503
    
    try:
        bits = tm.schemaCapacity()
        chars = bits // 7
        return jsonify({
            'capacity_bits': bits,
            'capacity_characters': chars,
            'encoding': 'BCH_SUPER'
        })
    except Exception as e:
        return jsonify({'error': f'Capacity check failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)