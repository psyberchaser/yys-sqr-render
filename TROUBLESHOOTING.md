# YYS-SQR Troubleshooting Guide

## Installation Issues

### "python3: command not found"

**Problem**: Python is not installed or not in PATH

**Solutions**:
```bash
# macOS - Install via Homebrew
brew install python3

# macOS - Install via official installer
# Download from https://www.python.org/downloads/

# Check installation
python3 --version
```

### "No module named 'trustmark'"

**Problem**: Dependencies not installed or virtual environment not activated

**Solutions**:
```bash
# Make sure you're in the right directory
cd yys-sqr

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# If virtual environment doesn't exist
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied" errors

**Problem**: Insufficient permissions to create virtual environment or install packages

**Solutions**:
```bash
# macOS/Linux - Fix permissions
sudo chown -R $USER:$USER yys-sqr/

# Alternative - Use user install
pip install --user -r requirements.txt
```

### PyQt6 installation fails

**Problem**: Missing system dependencies for GUI framework

**Solutions**:
```bash
# macOS - Install Xcode command line tools
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt-get install python3-pyqt6 python3-pyqt6-dev

# Linux (CentOS/RHEL)
sudo yum install python3-qt6 python3-qt6-devel
```

## Application Launch Issues

### GUI window doesn't appear

**Problem**: Display or GUI framework issues

**Solutions**:
1. **Check display connection** (if using remote/SSH)
2. **Try running with display export**:
   ```bash
   export DISPLAY=:0
   python main.py
   ```
3. **Run in verbose mode**:
   ```bash
   python main.py --verbose
   ```

### "Application quit unexpectedly"

**Problem**: Missing dependencies or system incompatibility

**Solutions**:
1. **Check Python version**:
   ```bash
   python3 --version  # Should be 3.11+
   ```
2. **Reinstall dependencies**:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```
3. **Check system logs**:
   ```bash
   # macOS
   Console.app → search for "YYS-SQR"
   
   # Linux
   journalctl -f
   ```

### "Segmentation fault" or crashes

**Problem**: OpenCV or PyQt6 compatibility issues

**Solutions**:
1. **Update system libraries**:
   ```bash
   # macOS
   brew update && brew upgrade
   
   # Linux
   sudo apt update && sudo apt upgrade
   ```
2. **Try different OpenCV version**:
   ```bash
   pip uninstall opencv-python
   pip install opencv-python==4.8.1.78
   ```

## Watermarking Issues

### "No watermark detected"

**Problem**: Watermark extraction failed

**Possible causes and solutions**:

1. **Poor photo quality**:
   - Retake photo with better lighting
   - Ensure entire image is visible
   - Use higher resolution camera
   - Avoid shadows and glare

2. **Incorrect corner selection**:
   - Click corners in exact order: TL → TR → BR → BL
   - Click precisely on corners
   - Restart corner selection if needed

3. **Image degradation**:
   - Use higher quality print settings
   - Avoid heavily compressed images
   - Try different paper type (matte vs glossy)

4. **Wrong watermark settings**:
   - Ensure same encoding settings used
   - Check if message was actually embedded

### "Message too long" error

**Problem**: Message exceeds watermark capacity

**Solutions**:
- **Reduce message length** (max 5 characters)
- **Use abbreviations**: "HELLO" → "HI"
- **Use numbers**: "2024" instead of "YEAR2024"
- **Check capacity**:
  ```bash
  python scripts/check_capacity.py
  ```

### Embedding fails silently

**Problem**: Image format or size issues

**Solutions**:
1. **Convert image format**:
   ```bash
   # Convert to PNG
   python -c "from PIL import Image; Image.open('input.jpg').save('output.png')"
   ```
2. **Resize image**:
   ```bash
   # Resize to reasonable size
   python -c "from PIL import Image; img=Image.open('input.jpg'); img.resize((1024,1024)).save('resized.png')"
   ```
3. **Check image properties**:
   - Minimum size: 256x256 pixels
   - Supported formats: PNG, JPG, JPEG
   - Avoid grayscale images

## Blockchain Issues

### "Wrong network" error

**Problem**: Connected to wrong Ethereum network

**Solutions**:
1. **Verify network**: Should be Sepolia testnet (Chain ID: 11155111)
2. **Check RPC URL**: Should point to Sepolia endpoint
3. **Get testnet ETH**:
   - Visit Sepolia faucet: https://sepoliafaucet.com/
   - Enter your wallet address
   - Wait for ETH to arrive

### "Insufficient gas" error

**Problem**: Not enough ETH for transaction fees

**Solutions**:
1. **Get more testnet ETH** from faucet
2. **Check wallet balance**:
   ```bash
   # Use any Ethereum wallet or block explorer
   # Search your address on https://sepolia.etherscan.io/
   ```
3. **Lower gas price** (edit main.py):
   ```python
   'gasPrice': w3.to_wei('5', 'gwei')  # Reduce from 10 to 5
   ```

### "Invalid private key" error

**Problem**: Malformed or incorrect private key

**Solutions**:
1. **Check key format**:
   - Should be 64 hex characters
   - No "0x" prefix needed
   - Example: `a1b2c3d4e5f6...` (64 chars)
2. **Export from wallet**:
   - MetaMask: Account Details → Export Private Key
   - Other wallets: Look for "Export" or "Private Key" option
3. **Create new testnet wallet** if needed

### Transaction timeout

**Problem**: Network congestion or RPC issues

**Solutions**:
1. **Wait and retry** - Network may be congested
2. **Try different RPC endpoint**:
   ```python
   # Edit main.py, try alternative RPC
   SEPOLIA_RPC_URL = "https://rpc.sepolia.org"
   ```
3. **Increase timeout**:
   ```python
   # Edit main.py
   request_kwargs={'timeout': 300}  # Increase from 120 to 300
   ```

## IPFS/Storage Issues

### "Upload failed" error

**Problem**: IPFS upload to Filebase failed

**Solutions**:
1. **Check internet connection**
2. **Verify file size** (should be < 100MB)
3. **Try again later** - Service may be temporarily down
4. **Disable Web3 features** if not needed:
   - Uncheck "Enable Web3 Features" checkbox

### "Access denied" error

**Problem**: Filebase API credentials issue

**Solutions**:
1. **Check credentials** in main.py (should be valid)
2. **Try different endpoint** if available
3. **Disable IPFS upload** temporarily:
   - Uncheck "Enable Web3 Features"

## Performance Issues

### Slow processing

**Problem**: System resources or large files

**Solutions**:
1. **Close other applications**
2. **Use smaller images** (resize to 1024x1024)
3. **Increase system RAM** if possible
4. **Use SSD storage** for better I/O

### High memory usage

**Problem**: Large images or memory leaks

**Solutions**:
1. **Restart application** periodically
2. **Process smaller batches**
3. **Monitor system resources**:
   ```bash
   # macOS
   Activity Monitor
   
   # Linux
   htop
   ```

## Getting Help

### Enable Debug Mode

Add debug output to troubleshoot:
```python
# Edit main.py, change:
self.tm = trustmark.TrustMark(verbose=False, encoding_type=ENCODING_TYPE)
# To:
self.tm = trustmark.TrustMark(verbose=True, encoding_type=ENCODING_TYPE)
```

### Collect System Information

```bash
# System info
python3 --version
pip list | grep -E "(trustmark|opencv|PyQt6|web3)"

# macOS
system_profiler SPSoftwareDataType

# Linux
uname -a
lsb_release -a
```

### Log Files

Check application logs:
- **macOS**: Console.app → search "YYS-SQR"
- **Linux**: `journalctl -f` or `/var/log/syslog`
- **Windows**: Event Viewer → Application logs

### Common Error Patterns

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |
| `Permission denied` | File permissions | `chmod +x` or run as admin |
| `Segmentation fault` | Library conflict | Reinstall dependencies |
| `Connection refused` | Network/firewall | Check internet connection |
| `Invalid key` | Wrong private key | Verify key format |
| `Gas estimation failed` | Insufficient ETH | Get testnet ETH |

### Still Need Help?

1. **Check documentation**: `USER_GUIDE.md`, `INSTALL.md`
2. **Review error messages** carefully
3. **Try minimal test case** with simple image/message
4. **Search for similar issues** online
5. **Create detailed bug report** with:
   - System information
   - Exact error message
   - Steps to reproduce
   - Screenshots if applicable