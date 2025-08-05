# YYS-SQR Enhanced Server with Web App and Database
import os
import tempfile
import base64
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_migrate import Migrate
from PIL import Image
import io

# Import our existing modules
from database import db, TradingCard, ScanHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Starting YYS-SQR Enhanced Server v2.1...")

# Import watermarking modules
detector = None
tm = None

try:
    print("📦 Loading auto corner detection...")
    from auto_corner_detection import AutoCornerDetector
    detector = AutoCornerDetector()
    print("✅ AutoCornerDetector loaded successfully")
except Exception as e:
    print(f"❌ AutoCornerDetector failed: {e}")

try:
    print("📦 Loading TrustMark...")
    import trustmark
    tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
    print("✅ TrustMark loaded successfully")
except Exception as e:
    print(f"❌ TrustMark failed: {e}")

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///yys_sqr.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Create tables
with app.app_context():
    db.create_all()

# ============================================================================
# WEB APP ROUTES (Card Creation Interface)
# ============================================================================

@app.route('/')
def index():
    """Main web app dashboard"""
    total_cards = TradingCard.query.count()
    minted_cards = TradingCard.query.filter(TradingCard.owner_address.isnot(None)).count()
    recent_cards = TradingCard.query.order_by(TradingCard.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_cards=total_cards,
                         minted_cards=minted_cards,
                         recent_cards=recent_cards)

@app.route('/create')
def create_card():
    """Card creation form"""
    return render_template('create_card.html')

@app.route('/cards')
def list_cards():
    """List all cards"""
    page = request.args.get('page', 1, type=int)
    cards = TradingCard.query.order_by(TradingCard.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('cards.html', cards=cards)

@app.route('/card/<watermark_id>')
def view_card(watermark_id):
    """View individual card details"""
    card = TradingCard.query.get_or_404(watermark_id)
    scans = ScanHistory.query.filter_by(watermark_id=watermark_id).order_by(ScanHistory.scanned_at.desc()).all()
    return render_template('card_detail.html', card=card, scans=scans)

# ============================================================================
# API ROUTES (Enhanced for Mobile App + Web App)
# ============================================================================

@app.route('/api/health')
def health():
    """Health check with database status"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        db_status = True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = False
    
    components = {
        'auto_corner_detection': detector is not None,
        'trustmark_watermarking': tm is not None,
        'database': db_status
    }
    
    status = 'healthy' if all(components.values()) else 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'components': components,
        'ready': all(components.values())
    }), 200 if status == 'healthy' else 503

@app.route('/api/cards', methods=['GET'])
def api_get_cards():
    """Get all cards with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    cards = TradingCard.query.order_by(TradingCard.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    })

@app.route('/api/cards', methods=['POST'])
def api_create_card():
    """Create a new trading card"""
    if not tm:
        return jsonify({'error': 'Watermarking service not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['card_name', 'image']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate unique watermark ID
        watermark_id = TradingCard.generate_watermark_id()
        
        # Decode and validate image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        # Create watermarked image
        try:
            watermarked_image = tm.encode(image, watermark_id)
            
            # Convert to base64 for storage
            buffer = io.BytesIO()
            watermarked_image.save(buffer, format='PNG')
            watermarked_base64 = base64.b64encode(buffer.getvalue()).decode()
            
        except Exception as e:
            logger.error(f"💥 Watermarking error: {e}")
            return jsonify({'error': f'Failed to create watermark: {str(e)}'}), 500
        
        # Create database record
        card = TradingCard(
            watermark_id=watermark_id,
            card_name=data['card_name'],
            description=data.get('description', ''),
            series=data.get('series', ''),
            rarity=data.get('rarity', 'Common'),
            creator_address=data.get('creator_address', ''),
            image_url=f"data:image/png;base64,{data['image']}",
            watermarked_image_url=f"data:image/png;base64,{watermarked_base64}"
        )
        
        db.session.add(card)
        db.session.commit()
        
        logger.info(f"✅ Created card: {watermark_id} - {data['card_name']}")
        
        return jsonify({
            'success': True,
            'card': card.to_dict(),
            'watermarked_image': watermarked_base64
        })
        
    except Exception as e:
        logger.error(f"💥 Card creation error: {e}")
        return jsonify({'error': f'Failed to create card: {str(e)}'}), 500

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Enhanced scan with database lookup"""
    if not detector:
        return jsonify({
            'error': 'Auto corner detection not available',
            'details': 'The corner detection system failed to initialize'
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        logger.info("📷 Processing enhanced scan request...")
        
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
            result = detector.detect_and_decode(temp_path)
            
            if result.get('success'):
                watermark_id = result.get('watermark_id')
                
                # Look up card in database
                card = TradingCard.query.get(watermark_id)
                if card:
                    # Update scan count
                    card.scan_count += 1
                    
                    # Record scan history
                    scan = ScanHistory(
                        watermark_id=watermark_id,
                        scanner_address=data.get('scanner_address'),
                        was_first_scan=(card.owner_address is None)
                    )
                    db.session.add(scan)
                    db.session.commit()
                    
                    # Enhanced result with card data
                    result.update({
                        'card': card.to_dict(),
                        'scan_count': card.scan_count,
                        'is_first_scan': card.owner_address is None
                    })
                    
                    logger.info(f"✅ Enhanced scan successful: {watermark_id}")
                else:
                    logger.info(f"⚠️ Watermark found but no card data: {watermark_id}")
            
            # Add API metadata
            result['api_version'] = '2.0.0'
            result['timestamp'] = datetime.now().isoformat()
            result['server'] = 'render-enhanced'
            
            return jsonify(result)
            
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"💥 Enhanced scan error: {e}")
        return jsonify({
            'error': 'Internal scan error',
            'details': str(e),
            'success': False
        }), 500

@app.route('/api/scan/manual', methods=['POST'])
def api_scan_manual():
    """Manual scan with database lookup"""
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
                # Look up card in database
                card = TradingCard.query.get(secret_id)
                if card:
                    # Update scan count
                    card.scan_count += 1
                    
                    # Record scan history
                    scan = ScanHistory(
                        watermark_id=secret_id,
                        scanner_address=data.get('scanner_address'),
                        was_first_scan=(card.owner_address is None)
                    )
                    db.session.add(scan)
                    db.session.commit()
                    
                    logger.info(f"✅ Manual scan successful: {secret_id}")
                    return jsonify({
                        'success': True,
                        'watermark_id': secret_id,
                        'method': 'manual_corner_selection',
                        'corners': corners,
                        'card': card.to_dict(),
                        'scan_count': card.scan_count,
                        'is_first_scan': card.owner_address is None,
                        'timestamp': datetime.now().isoformat(),
                        'server': 'render-enhanced'
                    })
                else:
                    logger.info(f"✅ Manual scan successful but no card data: {secret_id}")
                    return jsonify({
                        'success': True,
                        'watermark_id': secret_id,
                        'method': 'manual_corner_selection',
                        'corners': corners,
                        'timestamp': datetime.now().isoformat(),
                        'server': 'render-enhanced'
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

# ============================================================================
# MOBILE APP COMPATIBILITY ENDPOINTS
# ============================================================================

@app.route('/api/health')
@app.route('/health')  # Mobile app compatibility
def health_compat():
    """Health check - mobile app compatibility"""
    return health()

@app.route('/api/capacity')
@app.route('/capacity')  # Mobile app compatibility
def capacity():
    """Get watermark capacity information"""
    if not tm:
        return jsonify({'error': 'TrustMark not available'}), 503
    
    try:
        capacity = tm.schemaCapacity()
        return jsonify({
            'capacity_characters': capacity,
            'encoding': 'BCH_SUPER',
            'max_message_length': 5,
            'status': 'available'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get capacity: {str(e)}'}), 500

@app.route('/api/methods')
@app.route('/methods')  # Mobile app compatibility
def detection_methods():
    """Get available detection methods"""
    return jsonify({
        'methods': [
            'automatic_corner_detection',
            'manual_corner_selection'
        ],
        'default': 'automatic_corner_detection',
        'status': 'available'
    })

@app.route('/api/embed', methods=['POST'])
@app.route('/embed', methods=['POST'])  # Mobile app compatibility
def embed():
    """Embed watermark - mobile app compatibility"""
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
        
        # Embed watermark using TrustMark
        try:
            watermarked_image = tm.encode(image, message)
            
            # Convert to base64
            buffer = io.BytesIO()
            watermarked_image.save(buffer, format='PNG')
            watermarked_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"✅ Embedding successful: '{message}'")
            
            return jsonify({
                'success': True,
                'message': message,
                'watermarked_image': watermarked_base64,
                'timestamp': datetime.now().isoformat(),
                'server': 'render-enhanced'
            })
            
        except Exception as e:
            logger.error(f"💥 Embedding error: {e}")
            return jsonify({'error': f'Failed to embed watermark: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"💥 Embed endpoint error: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/scan/batch', methods=['POST'])
@app.route('/scan/batch', methods=['POST'])  # Mobile app compatibility
def batch_scan():
    """Batch scan multiple images"""
    return jsonify({
        'error': 'Batch scanning not implemented yet',
        'details': 'Use individual scan endpoints instead'
    }), 501

@app.route('/api/scan/visualize', methods=['POST'])
@app.route('/scan/visualize', methods=['POST'])  # Mobile app compatibility
def visualize_detection():
    """Visualize corner detection process"""
    return jsonify({
        'error': 'Visualization not implemented yet',
        'details': 'Use regular scan endpoints instead'
    }), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)