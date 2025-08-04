# Enhanced IPFS Integration for YYS-SQR

import requests
import json
import hashlib
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

class IPFSManager:
    """Enhanced IPFS management with multiple providers and metadata"""
    
    def __init__(self):
        self.providers = {
            'filebase': {
                'endpoint': 'https://s3.filebase.com',
                'access_key': 'F27503EAB0C920092137',
                'secret_key': 'sZtWNzcoWWZkUhHDxM2WChGjt9OYrVDMsWZ0HYW3',
                'bucket': 'yys-yys'
            },
            'pinata': {
                'api_url': 'https://api.pinata.cloud',
                'api_key': 'YOUR_PINATA_API_KEY',
                'secret_key': 'YOUR_PINATA_SECRET'
            },
            'web3_storage': {
                'api_url': 'https://api.web3.storage',
                'api_token': 'YOUR_WEB3_STORAGE_TOKEN'
            }
        }
        self.active_provider = 'filebase'
    
    def upload_with_metadata(self, file_path, metadata=None):
        """Upload file with enhanced metadata"""
        if metadata is None:
            metadata = {}
        
        # Add default metadata
        metadata.update({
            'uploaded_at': datetime.now().isoformat(),
            'file_hash': self._calculate_file_hash(file_path),
            'yys_sqr_version': '1.0.0',
            'content_type': self._get_content_type(file_path)
        })
        
        if self.active_provider == 'filebase':
            return self._upload_filebase(file_path, metadata)
        elif self.active_provider == 'pinata':
            return self._upload_pinata(file_path, metadata)
        elif self.active_provider == 'web3_storage':
            return self._upload_web3_storage(file_path, metadata)
        else:
            raise ValueError(f"Unknown provider: {self.active_provider}")
    
    def _upload_filebase(self, file_path, metadata):
        """Upload to Filebase with metadata"""
        try:
            config = self.providers['filebase']
            s3_client = boto3.client(
                's3',
                endpoint_url=config['endpoint'],
                aws_access_key_id=config['access_key'],
                aws_secret_access_key=config['secret_key'],
                region_name='us-east-1'
            )
            
            object_name = f"yys-sqr/{datetime.now().strftime('%Y/%m/%d')}/{hashlib.md5(open(file_path, 'rb').read()).hexdigest()}.png"
            
            # Convert metadata to S3 metadata format
            s3_metadata = {f'yys-{k}': str(v) for k, v in metadata.items()}
            
            with open(file_path, 'rb') as f:
                s3_client.put_object(
                    Body=f,
                    Bucket=config['bucket'],
                    Key=object_name,
                    Metadata=s3_metadata
                )
            
            # Get IPFS CID
            response = s3_client.head_object(
                Bucket=config['bucket'],
                Key=object_name
            )
            
            ipfs_cid = response['Metadata'].get('cid')
            return {
                'cid': ipfs_cid,
                'provider': 'filebase',
                'metadata': metadata,
                'gateway_url': f"https://ipfs.filebase.io/ipfs/{ipfs_cid}"
            }
            
        except Exception as e:
            print(f"Filebase upload error: {e}")
            return None
    
    def _upload_pinata(self, file_path, metadata):
        """Upload to Pinata (future implementation)"""
        # Implementation for Pinata API
        pass
    
    def _upload_web3_storage(self, file_path, metadata):
        """Upload to Web3.Storage (future implementation)"""
        # Implementation for Web3.Storage API
        pass
    
    def retrieve_metadata(self, cid):
        """Retrieve metadata for a given CID"""
        if self.active_provider == 'filebase':
            return self._retrieve_filebase_metadata(cid)
        # Add other providers as needed
    
    def _retrieve_filebase_metadata(self, cid):
        """Retrieve metadata from Filebase"""
        # Implementation to retrieve metadata
        pass
    
    def pin_content(self, cid):
        """Pin content to ensure persistence"""
        # Implementation for pinning content
        pass
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_content_type(self, file_path):
        """Get content type based on file extension"""
        extension = file_path.lower().split('.')[-1]
        content_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return content_types.get(extension, 'application/octet-stream')

class IPFSGatewayManager:
    """Manage multiple IPFS gateways for redundancy"""
    
    def __init__(self):
        self.gateways = [
            'https://ipfs.filebase.io/ipfs/',
            'https://gateway.pinata.cloud/ipfs/',
            'https://ipfs.io/ipfs/',
            'https://cloudflare-ipfs.com/ipfs/',
            'https://dweb.link/ipfs/'
        ]
    
    def get_accessible_url(self, cid):
        """Find the first accessible gateway for a CID"""
        for gateway in self.gateways:
            url = f"{gateway}{cid}"
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    return url
            except:
                continue
        return None
    
    def get_all_urls(self, cid):
        """Get all possible URLs for a CID"""
        return [f"{gateway}{cid}" for gateway in self.gateways]