# YYS-SQR Examples and Use Cases

## Real-World Examples

### Example 1: Document Authentication

**Scenario**: Law firm wants to authenticate legal documents

**Process**:
1. **Embed**: Hide "AUTH" in the firm's letterhead logo
2. **Print**: Include watermarked logo on all official documents  
3. **Verify**: Clients can scan logo to confirm authenticity
4. **Blockchain**: Proof-of-scan creates immutable verification record

**Benefits**:
- Prevents document forgery
- Easy verification for clients
- Permanent audit trail

### Example 2: Event Ticket Validation

**Scenario**: Concert venue needs secure ticket validation

**Process**:
1. **Embed**: Hide unique ticket ID (e.g., "T1234") in ticket design
2. **Single-Use**: Enable single-use SQR to prevent reuse
3. **Print**: Distribute tickets with watermarked design
4. **Scan**: Gate staff scan tickets with phones
5. **Validation**: Message appears once, then self-destructs

**Benefits**:
- Prevents ticket duplication
- Instant validation at gates
- Automatic ticket deactivation

### Example 3: Product Anti-Counterfeiting

**Scenario**: Luxury brand wants to prevent counterfeiting

**Process**:
1. **Embed**: Hide brand code in product labels/packaging
2. **IPFS**: Store product images on decentralized storage
3. **Print**: Apply watermarked labels to authentic products
4. **Consumer Verification**: Customers scan to verify authenticity
5. **Blockchain**: Each scan creates proof of authenticity check

**Benefits**:
- Customers can verify authenticity
- Difficult for counterfeiters to replicate
- Global verification system

### Example 4: Academic Certificate Verification

**Scenario**: University wants to issue verifiable diplomas

**Process**:
1. **Embed**: Hide graduation year in university seal
2. **Print**: Include watermarked seal on diplomas
3. **Verify**: Employers scan seal to confirm legitimacy
4. **Permanent Record**: Blockchain stores verification history

**Benefits**:
- Prevents diploma mills
- Easy employer verification
- Permanent academic record

## Step-by-Step Tutorials

### Tutorial 1: Basic Message Hiding

**Goal**: Hide "HELLO" in a family photo

**Steps**:
1. **Launch YYS-SQR**:
   ```bash
   cd yys-sqr
   source .venv/bin/activate
   python main.py
   ```

2. **Embed Tab**:
   - Click "Select Image" → choose `family_photo.jpg`
   - Type "HELLO" in message box
   - Leave checkboxes unchecked for simple test
   - Click "Embed SQR"
   - Save as `family_photo_watermarked.png`

3. **Test Locally**:
   - Switch to "Decode SQR" tab
   - Click "Select Photo" → choose `family_photo_watermarked.png`
   - Click all 4 corners (TL→TR→BR→BL)
   - Click "Step 3" button
   - Result: "HELLO" appears!

### Tutorial 2: Mobile Scanning Workflow

**Goal**: Scan a printed watermarked image with your phone

**Steps**:
1. **Print the watermarked image** from Tutorial 1
2. **Take phone photo**:
   - Use good lighting
   - Ensure entire image is visible
   - Hold phone steady
   - Take photo straight-on

3. **Transfer photo to computer**:
   - Email to yourself
   - Use AirDrop (Mac)
   - Use cloud storage
   - USB transfer

4. **Scan in YYS-SQR**:
   - "Decode SQR" tab
   - "Select Photo" → choose phone photo
   - Click corners carefully (zoom in if needed)
   - Process and see results

### Tutorial 3: Blockchain Integration

**Goal**: Record proof-of-scan on Ethereum blockchain

**Prerequisites**:
- Ethereum wallet (MetaMask recommended)
- Sepolia testnet ETH (get from faucet)

**Steps**:
1. **Get Testnet ETH**:
   - Visit https://sepoliafaucet.com/
   - Enter your wallet address
   - Wait for ETH to arrive

2. **Export Private Key**:
   - MetaMask → Account Details → Export Private Key
   - Copy the 64-character hex string

3. **Embed with Web3**:
   - Create watermarked image (Tutorial 1)
   - Check "Enable Web3 Features" 
   - Embed and note the IPFS CID

4. **Scan with Blockchain**:
   - Decode the watermarked image
   - Paste private key in "Your Sepolia Private Key" field
   - Process scan
   - Click "View Transaction on Etherscan" to see blockchain record

### Tutorial 4: Single-Use Security

**Goal**: Create a self-destructing watermark

**Use Case**: One-time access code

**Steps**:
1. **Embed with Single-Use**:
   - Select image
   - Enter message (e.g., "CODE1")
   - Check "Single-Use SQR" checkbox
   - Embed and save

2. **First Scan**:
   - Scan the watermarked image
   - Message "CODE1" appears
   - Notice: "This was a single-use SQR. The data has been deleted."

3. **Second Scan**:
   - Scan the same image again
   - Result: "Decoded ID 'xxxxx' not found in database"
   - Message is permanently deleted

## Command Line Examples

### Batch Processing Script

Create multiple watermarked images:

```bash
#!/bin/bash
cd yys-sqr
source .venv/bin/activate

# Array of images and messages
images=("photo1.jpg" "photo2.jpg" "photo3.jpg")
messages=("MSG01" "MSG02" "MSG03")

# Process each image
for i in "${!images[@]}"; do
    echo "Processing ${images[$i]} with message ${messages[$i]}"
    python scripts/embed.py \
        --input_image "${images[$i]}" \
        --output_image "watermarked_${i}.png"
done

echo "Batch processing complete!"
```

### Automated Verification

Verify multiple images:

```bash
#!/bin/bash
cd yys-sqr
source .venv/bin/activate

# Check all watermarked images
for file in watermarked_*.png; do
    echo "Checking $file:"
    python scripts/decode.py "$file"
    echo "---"
done
```

### Capacity Testing

Check different encoding options:

```bash
cd yys-sqr
source .venv/bin/activate

echo "Current capacity:"
python scripts/check_capacity.py

echo "Testing with different settings..."
# Modify check_capacity.py to test different encodings
```

## Integration Examples

### Python API Usage

```python
import sys
sys.path.append('yys-sqr')

from PIL import Image
import trustmark

# Initialize
tm = trustmark.TrustMark(
    verbose=False, 
    model_type='Q', 
    encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER
)

# Embed
image = Image.open('input.jpg').convert('RGB')
watermarked = tm.encode(image, 'HELLO')
watermarked.save('output.png')

# Decode
secret, present, confidence = tm.decode(watermarked)
if present:
    print(f"Found message: {secret}")
```

### Web Service Integration

```python
from flask import Flask, request, jsonify
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def embed_watermark():
    # Get image and message from request
    image_data = request.json['image']  # base64 encoded
    message = request.json['message']
    
    # Decode image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    
    # Embed watermark
    watermarked = tm.encode(image, message)
    
    # Return watermarked image
    buffer = BytesIO()
    watermarked.save(buffer, format='PNG')
    result = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'watermarked_image': result})

if __name__ == '__main__':
    app.run(debug=True)
```

## Advanced Use Cases

### Multi-Layer Security

Combine multiple security features:

1. **Primary Watermark**: Visible company logo
2. **Hidden Watermark**: Invisible authentication code
3. **Blockchain Record**: Immutable creation timestamp
4. **IPFS Storage**: Decentralized backup

### Workflow Automation

Integrate with existing systems:

1. **Document Generation**: Auto-embed watermarks in PDFs
2. **Print Queue Integration**: Watermark before printing
3. **Email Attachments**: Watermark outgoing files
4. **Cloud Storage**: Watermark uploaded files

### Analytics and Tracking

Monitor watermark usage:

1. **Scan Analytics**: Track when/where scans occur
2. **Geographic Data**: Location-based verification
3. **Usage Patterns**: Identify suspicious activity
4. **Audit Trails**: Complete verification history

## Performance Benchmarks

### Typical Processing Times

| Operation | Image Size | Time |
|-----------|------------|------|
| Embed | 1024x1024 | 2-5 seconds |
| Decode | 1024x1024 | 3-7 seconds |
| Perspective Correction | 2048x1536 | 1-3 seconds |
| IPFS Upload | 1MB file | 5-15 seconds |
| Blockchain Transaction | N/A | 10-30 seconds |

### Optimization Tips

1. **Image Size**: Optimal range 512x512 to 2048x2048
2. **Format**: PNG for best quality, JPEG for smaller files
3. **Batch Processing**: Process multiple images together
4. **Network**: Stable connection for Web3 features
5. **Hardware**: SSD storage and 8GB+ RAM recommended

## Best Practices Summary

### For Embedding
- Use high-quality source images
- Keep messages short and meaningful
- Test with print/scan workflow
- Consider single-use for security

### For Scanning  
- Good lighting and steady hands
- Click corners precisely
- Use high-resolution photos
- Verify results immediately

### For Security
- Use blockchain for important documents
- Enable IPFS for global access
- Implement single-use for sensitive data
- Keep private keys secure

### For Integration
- Test thoroughly before deployment
- Monitor performance and errors
- Implement proper error handling
- Document your specific workflow