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

# Blockchain and wallet imports
import secrets
import hashlib
from web3 import Web3
from eth_account import Account
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ boto3 not available - IPFS upload will be disabled")
    BOTO3_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IPFS database migration completed - restart to pick up new schema
# Retry build after network error

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
# BLOCKCHAIN CONFIGURATION
# ============================================================================

# Sepolia testnet configuration - USE REAL DEPLOYED VALUES
SEPOLIA_RPC_URL = os.environ.get('SEPOLIA_RPC_URL', "https://sepolia.infura.io/v3/7d8b2ce49fe24184b30beb42dc1fa791")
CHAIN_ID = 11155111

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))

# Server wallet for gas fees - USE REAL PRIVATE KEY
SERVER_PRIVATE_KEY = os.environ.get('SERVER_PRIVATE_KEY', '0051793c860c068bbc9baeeafaec8b0cbca30a6d69b8df79ec54922ac5e27b1a')
server_account = Account.from_key(SERVER_PRIVATE_KEY)

# REAL DEPLOYED CONTRACT ADDRESSES
PROOF_OF_SCAN_CONTRACT = os.environ.get('PROOF_OF_SCAN_CONTRACT', '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8')
NFT_CONTRACT_ADDRESS = os.environ.get('NFT_CONTRACT_ADDRESS', '0x3bd2b0dcaFae0964a92D0785ee5F565dA7471369')

# IPFS/Filebase configuration
FILEBASE_ACCESS_KEY = os.environ.get('FILEBASE_ACCESS_KEY', 'A8F8E8F8E8F8E8F8E8F8')
FILEBASE_SECRET_KEY = os.environ.get('FILEBASE_SECRET_KEY', 'secret-key-here')
FILEBASE_BUCKET_NAME = os.environ.get('FILEBASE_BUCKET_NAME', 'yys-sqr-images')

# Simple user wallet storage (in production, use encrypted database)
user_wallets = {}

# ============================================================================
# IPFS UPLOAD FUNCTIONALITY
# ============================================================================

def upload_to_ipfs(file_path, object_name=None):
    """Upload a file to Filebase and return the IPFS CID"""
    if not BOTO3_AVAILABLE:
        logger.warning("⚠️ boto3 not available for IPFS upload")
        return None
        
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    # Initialize S3 client for Filebase
    s3_client = boto3.client(
        's3',
        endpoint_url='https://s3.filebase.com',
        aws_access_key_id=FILEBASE_ACCESS_KEY,
        aws_secret_access_key=FILEBASE_SECRET_KEY,
        region_name='us-east-1'
    )
    
    try:
        with open(file_path, 'rb') as f:
            s3_client.put_object(Body=f, Bucket=FILEBASE_BUCKET_NAME, Key=object_name)
        
        # Get the object's metadata to find the CID
        response = s3_client.head_object(
            Bucket=FILEBASE_BUCKET_NAME,
            Key=object_name
        )
        
        # The IPFS CID is stored in the metadata
        ipfs_cid = response['Metadata'].get('cid')
        if not ipfs_cid:
            ipfs_cid = response['Metadata'].get('x-amz-meta-cid')
        
        logger.info(f"✅ IPFS upload successful. CID: {ipfs_cid}")
        return ipfs_cid
        
    except ClientError as e:
        logger.error(f"❌ IPFS upload failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected IPFS upload error: {e}")
        return None

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
        
        # Upload images to IPFS (optional - don't fail if this doesn't work)
        original_ipfs_cid = None
        watermarked_ipfs_cid = None
        
        try:
            # Only attempt IPFS upload if boto3 is available and configured
            if BOTO3_AVAILABLE and FILEBASE_ACCESS_KEY and FILEBASE_SECRET_KEY:
                # Save original image temporarily and upload to IPFS
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_original:
                    image.save(temp_original.name, format='PNG')
                    original_ipfs_cid = upload_to_ipfs(temp_original.name, f"{watermark_id}_original.png")
                    os.unlink(temp_original.name)
                
                # Save watermarked image temporarily and upload to IPFS
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_watermarked:
                    watermarked_image.save(temp_watermarked.name, format='PNG')
                    watermarked_ipfs_cid = upload_to_ipfs(temp_watermarked.name, f"{watermark_id}_watermarked.png")
                    os.unlink(temp_watermarked.name)
            else:
                logger.info("📝 IPFS upload skipped - boto3 or credentials not configured")
                
        except Exception as e:
            logger.warning(f"⚠️ IPFS upload failed (continuing without IPFS): {e}")
        
        # Create database record with IPFS fields
        card = TradingCard(
            watermark_id=watermark_id,
            card_name=data['card_name'],
            description=data.get('description', ''),
            series=data.get('series', ''),
            rarity=data.get('rarity', 'Common'),
            creator_address=data.get('creator_address', ''),
            image_url=f"data:image/png;base64,{data['image']}",
            watermarked_image_url=f"data:image/png;base64,{watermarked_base64}",
            metadata_uri=f"https://gateway.pinata.cloud/ipfs/{original_ipfs_cid}" if original_ipfs_cid else None,
            ipfs_cid=original_ipfs_cid,
            watermarked_ipfs_cid=watermarked_ipfs_cid
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
                    
                    # Check if this is the first scan (before updating scan count)
                    is_first_scan = card.owner_address is None
                    
                    # Record scan history
                    scan = ScanHistory(
                        watermark_id=watermark_id,
                        scanner_address=data.get('scanner_address'),
                        was_first_scan=is_first_scan
                    )
                    db.session.add(scan)
                    db.session.commit()
                    
                    # Enhanced result with card data
                    result.update({
                        'card': card.to_dict(),
                        'scan_count': card.scan_count,
                        'is_first_scan': is_first_scan,
                        'can_claim_nft': is_first_scan
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
                    
                    # Check if this is the first scan (before updating scan count)
                    is_first_scan = card.owner_address is None
                    
                    # Record scan history
                    scan = ScanHistory(
                        watermark_id=secret_id,
                        scanner_address=data.get('scanner_address'),
                        was_first_scan=is_first_scan
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
                        'is_first_scan': is_first_scan,
                        'can_claim_nft': is_first_scan,
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
# WALLET & NFT ENDPOINTS
# ============================================================================

@app.route('/api/wallet/create', methods=['POST'])
def create_wallet():
    """Create a new Ethereum wallet for user"""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        if not email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        logger.info(f"🔐 Creating wallet for: {email}")
        
        # Check if user already has a wallet
        if email in user_wallets:
            existing_wallet = user_wallets[email]
            logger.info(f"✅ Returning existing wallet for: {email}")
            return jsonify({
                'success': True,
                'walletAddress': existing_wallet['address'],
                'message': 'Wallet already exists'
            })
        
        # Generate new Ethereum wallet
        account = Account.create()
        wallet_address = account.address
        private_key = account.key.hex()
        
        # Store wallet (in production, encrypt this!)
        user_wallets[email] = {
            'address': wallet_address,
            'private_key': private_key,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Created new wallet: {wallet_address} for {email}")
        
        return jsonify({
            'success': True,
            'walletAddress': wallet_address,
            'message': 'Wallet created successfully'
        })
        
    except Exception as e:
        logger.error(f"💥 Wallet creation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create wallet: {str(e)}'
        }), 500

@app.route('/api/wallet/balance/<wallet_address>')
def get_wallet_balance(wallet_address):
    """Get wallet balance from Sepolia"""
    try:
        if not w3.is_address(wallet_address):
            return jsonify({'error': 'Invalid wallet address'}), 400
        
        # Get balance from Sepolia
        balance_wei = w3.eth.get_balance(wallet_address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        logger.info(f"💰 Balance for {wallet_address}: {balance_eth} ETH")
        
        return jsonify({
            'success': True,
            'balance': f"{balance_eth:.4f}",
            'balanceWei': str(balance_wei),
            'network': 'sepolia'
        })
        
    except Exception as e:
        logger.error(f"💥 Balance check error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get balance: {str(e)}'
        }), 500

@app.route('/api/nft/claim', methods=['POST'])
def claim_nft():
    """Claim NFT for scanned card"""
    try:
        data = request.get_json()
        if not data or 'walletAddress' not in data or 'watermarkId' not in data:
            return jsonify({'error': 'Wallet address and watermark ID required'}), 400
        
        wallet_address = data['walletAddress']
        watermark_id = data['watermarkId']
        
        logger.info(f"🎯 NFT claim request: {watermark_id} → {wallet_address}")
        
        # Validate wallet address
        if not w3.is_address(wallet_address):
            return jsonify({'error': 'Invalid wallet address'}), 400
        
        # Check if card exists
        card = TradingCard.query.get(watermark_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        # Check if already claimed
        if card.owner_address:
            return jsonify({
                'success': False,
                'error': 'NFT already claimed',
                'owner': card.owner_address
            }), 400
        
        # REAL NFT MINTING - Mint actual ERC-721 NFT
        try:
            # NFT Contract ABI for minting
            nft_abi = [
                {
                    "inputs": [
                        {"name": "to", "type": "address"},
                        {"name": "watermarkId", "type": "string"},
                        {"name": "metadataURI", "type": "string"}
                    ],
                    "name": "mintCard",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            # Create NFT contract instance
            nft_contract = w3.eth.contract(
                address=NFT_CONTRACT_ADDRESS,
                abi=nft_abi
            )
            
            # Create metadata URI (IPFS or placeholder)
            metadata_uri = card.metadata_uri or f"https://ipfs.io/ipfs/QmYYSSQR{watermark_id}"
            
            # Build NFT minting transaction
            transaction = nft_contract.functions.mintCard(
                wallet_address,
                watermark_id,
                metadata_uri
            ).build_transaction({
                'from': server_account.address,
                'gas': 300000,  # Higher gas for NFT minting
                'gasPrice': w3.to_wei('10', 'gwei'),
                'nonce': w3.eth.get_transaction_count(server_account.address),
                'chainId': CHAIN_ID
            })
            
            # Sign and send transaction
            signed_txn = server_account.sign_transaction(transaction)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Ensure transaction hash has 0x prefix for logging
            tx_hash_str = tx_hash.hex()
            if not tx_hash_str.startswith('0x'):
                tx_hash_str = '0x' + tx_hash_str
            logger.info(f"🎯 REAL NFT MINTING transaction sent: {tx_hash_str}")
            
            # Wait for transaction receipt to get token ID
            try:
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                if receipt.status == 1:
                    # Parse logs to get token ID (simplified)
                    token_id = len(receipt.logs)  # Approximate token ID
                    logger.info(f"🎉 NFT MINTED! Token ID: {token_id}")
                else:
                    logger.error(f"❌ NFT minting transaction failed")
            except Exception as receipt_error:
                logger.error(f"⚠️ Could not get receipt: {receipt_error}")
                token_id = None
            
            # Update database with real NFT info
            # Ensure transaction hash has 0x prefix for storage
            tx_hash_str = tx_hash.hex()
            if not tx_hash_str.startswith('0x'):
                tx_hash_str = '0x' + tx_hash_str
                
            card.owner_address = wallet_address
            card.minted_at = datetime.now()
            card.mint_transaction_hash = tx_hash_str
            card.nft_token_id = token_id
            
            # Record the claim
            scan = ScanHistory(
                watermark_id=watermark_id,
                scanner_address=wallet_address,
                was_first_scan=True
            )
            db.session.add(scan)
            db.session.commit()
            
            # Ensure transaction hash has 0x prefix
            tx_hash_str = tx_hash.hex()
            if not tx_hash_str.startswith('0x'):
                tx_hash_str = '0x' + tx_hash_str
            
            logger.info(f"🎉 REAL NFT MINTED: {watermark_id} → {wallet_address} (tx: {tx_hash_str})")
            
            return jsonify({
                'success': True,
                'message': 'NFT minted successfully on blockchain!',
                'card': card.to_dict(),
                'transactionHash': tx_hash_str,
                'etherscanUrl': f'https://sepolia.etherscan.io/tx/{tx_hash_str}',
                'nftContract': NFT_CONTRACT_ADDRESS,
                'tokenId': token_id
            })
            
        except Exception as blockchain_error:
            logger.error(f"💥 Blockchain transaction failed: {blockchain_error}")
            
            # Fallback to database-only claim
            card.owner_address = wallet_address
            card.minted_at = datetime.now()
            
            scan = ScanHistory(
                watermark_id=watermark_id,
                scanner_address=wallet_address,
                was_first_scan=True
            )
            db.session.add(scan)
            db.session.commit()
            
            logger.info(f"⚠️ Database-only NFT claimed (blockchain failed): {watermark_id} → {wallet_address}")
            
            return jsonify({
                'success': True,
                'message': 'NFT claimed (database only - blockchain unavailable)',
                'card': card.to_dict(),
                'transactionHash': None,
                'error': str(blockchain_error)
            })
        
    except Exception as e:
        logger.error(f"💥 NFT claim error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to claim NFT: {str(e)}'
        }), 500

@app.route('/api/wallet/<wallet_address>/nfts')
def get_user_nfts(wallet_address):
    """Get NFTs owned by a specific wallet"""
    try:
        # Query database for cards owned by this wallet
        owned_cards = TradingCard.query.filter_by(owner_address=wallet_address).all()
        
        nfts = []
        for card in owned_cards:
            if card.is_minted and card.nft_token_id:
                nfts.append({
                    'tokenId': card.nft_token_id,
                    'watermarkId': card.watermark_id,
                    'cardName': card.card_name,
                    'description': card.description,
                    'transactionHash': card.mint_transaction_hash,
                    'etherscanUrl': f'https://sepolia.etherscan.io/tx/{card.mint_transaction_hash}',
                    'nftContract': NFT_CONTRACT_ADDRESS,
                    'mintedAt': card.minted_at.isoformat() if card.minted_at else None,
                    'ipfs_cid': card.ipfs_cid,
                    'watermarked_ipfs_cid': card.watermarked_ipfs_cid,
                    'imageUrl': f'https://gateway.pinata.cloud/ipfs/{card.ipfs_cid}' if card.ipfs_cid else card.image_url,
                    'watermarkedImageUrl': f'https://gateway.pinata.cloud/ipfs/{card.watermarked_ipfs_cid}' if card.watermarked_ipfs_cid else card.watermarked_image_url
                })
        
        return jsonify({
            'success': True,
            'nfts': nfts,
            'count': len(nfts)
        })
        
    except Exception as e:
        logger.error(f"Error fetching user NFTs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch NFTs'
        }), 500

@app.route('/api/admin/migrate-database')
def migrate_database():
    """Add IPFS fields to database (admin endpoint)"""
    try:
        # Add the IPFS columns if they don't exist
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text("ALTER TABLE trading_cards ADD COLUMN ipfs_cid VARCHAR(100)"))
                conn.execute(db.text("ALTER TABLE trading_cards ADD COLUMN watermarked_ipfs_cid VARCHAR(100)"))
                conn.commit()
                return jsonify({
                    'success': True,
                    'message': 'IPFS columns added successfully'
                })
            except Exception as e:
                if "already exists" in str(e).lower():
                    return jsonify({
                        'success': True,
                        'message': 'IPFS columns already exist'
                    })
                else:
                    raise e
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wallet/list')
def list_wallets():
    """List all created wallets (admin endpoint)"""
    try:
        wallets = []
        for email, wallet_info in user_wallets.items():
            wallets.append({
                'email': email,
                'address': wallet_info['address'],
                'created_at': wallet_info['created_at']
            })
        
        return jsonify({
            'success': True,
            'wallets': wallets,
            'count': len(wallets)
        })
        
    except Exception as e:
        logger.error(f"💥 Wallet list error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to list wallets: {str(e)}'
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