# Database models for YYS-SQR Trading Cards
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class TradingCard(db.Model):
    __tablename__ = 'trading_cards'
    
    # Primary identifier
    watermark_id = db.Column(db.String(5), primary_key=True)
    
    # Card metadata
    card_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    series = db.Column(db.String(100), nullable=True)
    rarity = db.Column(db.String(50), nullable=True)
    creator_address = db.Column(db.String(42), nullable=True)
    
    # Images
    image_url = db.Column(db.Text, nullable=True)
    watermarked_image_url = db.Column(db.Text, nullable=True)
    metadata_uri = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NFT tracking
    owner_address = db.Column(db.String(42), nullable=True)
    nft_token_id = db.Column(db.BigInteger, nullable=True)
    minted_at = db.Column(db.DateTime, nullable=True)
    mint_transaction_hash = db.Column(db.String(66), nullable=True)
    scan_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<TradingCard {self.watermark_id}: {self.card_name}>'
    
    def to_dict(self):
        return {
            'watermark_id': self.watermark_id,
            'card_name': self.card_name,
            'description': self.description,
            'series': self.series,
            'rarity': self.rarity,
            'creator_address': self.creator_address,
            'image_url': self.image_url,
            'watermarked_image_url': self.watermarked_image_url,
            'metadata_uri': self.metadata_uri,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner_address': self.owner_address,
            'nft_token_id': self.nft_token_id,
            'minted_at': self.minted_at.isoformat() if self.minted_at else None,
            'mint_transaction_hash': self.mint_transaction_hash,
            'scan_count': self.scan_count,
            'is_minted': self.owner_address is not None
        }
    
    @staticmethod
    def generate_watermark_id():
        """Generate a unique 5-character watermark ID"""
        while True:
            # Generate 5 random uppercase letters/numbers
            watermark_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            
            # Check if it already exists
            if not TradingCard.query.filter_by(watermark_id=watermark_id).first():
                return watermark_id

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'
    
    id = db.Column(db.Integer, primary_key=True)
    watermark_id = db.Column(db.String(5), db.ForeignKey('trading_cards.watermark_id'), nullable=False)
    scanner_address = db.Column(db.String(42), nullable=True)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
    was_first_scan = db.Column(db.Boolean, default=False)
    
    # Relationship
    card = db.relationship('TradingCard', backref=db.backref('scans', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'watermark_id': self.watermark_id,
            'scanner_address': self.scanner_address,
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None,
            'was_first_scan': self.was_first_scan
        }