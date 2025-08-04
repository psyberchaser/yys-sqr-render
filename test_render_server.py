#!/usr/bin/env python3
"""
Test script for Render server before deployment
"""
import requests
import base64
import json
from PIL import Image
import io

def test_local_server():
    """Test the render server running locally"""
    base_url = "http://localhost:10000"
    
    print("🧪 Testing YYS-SQR Render Server...")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        data = response.json()
        print(f"   Components: {data.get('components', {})}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code}")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Ready: {data.get('ready')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 3: Capacity check
    try:
        response = requests.get(f"{base_url}/api/capacity")
        print(f"✅ Capacity check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Capacity: {data.get('capacity_characters')} chars")
    except Exception as e:
        print(f"❌ Capacity check failed: {e}")
    
    # Test 4: Create test image for embedding/scanning
    try:
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Test embedding
        embed_data = {
            'image': img_b64,
            'message': 'TEST1'
        }
        
        response = requests.post(f"{base_url}/api/embed", json=embed_data)
        print(f"✅ Embed test: {response.status_code}")
        
        if response.status_code == 200:
            embed_result = response.json()
            if embed_result.get('success'):
                print("   Embedding successful!")
                
                # Test scanning the embedded image
                scan_data = {
                    'image': embed_result['watermarked_image']
                }
                
                response = requests.post(f"{base_url}/api/scan", json=scan_data)
                print(f"✅ Scan test: {response.status_code}")
                
                if response.status_code == 200:
                    scan_result = response.json()
                    if scan_result.get('success'):
                        print(f"   Scan successful! Found: {scan_result.get('watermark_id')}")
                    else:
                        print(f"   Scan failed: {scan_result.get('error')}")
            else:
                print(f"   Embedding failed: {embed_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Embed/Scan test failed: {e}")
    
    print("\n🎉 Server test completed!")
    return True

if __name__ == "__main__":
    print("To test locally:")
    print("1. Run: python render_server.py")
    print("2. In another terminal, run: python test_render_server.py")
    print()
    
    try:
        test_local_server()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python render_server.py")