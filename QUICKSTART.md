# YYS-SQR Quick Start Guide

## What is YYS-SQR?

YYS-SQR is a powerful watermarking system that lets you:
- **Hide secret messages** in images invisibly
- **Scan printed photos** with your phone to reveal hidden messages
- **Record proof** of scans on the blockchain
- **Store images** on decentralized IPFS storage

## 🚀 Get Started in 3 Minutes

### Step 1: Setup (One-time only)

1. **Open Terminal** (on Mac: press `Cmd+Space`, type "Terminal")

2. **Navigate to the project**:
   ```bash
   cd yys-sqr
   ```

3. **Install everything automatically**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Step 2: Run the Application

```bash
python main.py
```

The YYS-SQR window will open!

## 📱 How to Use

### Embedding a Watermark (Hide a Message)

1. **Click "Embed SQR" tab**
2. **Select Image**: Click "Select Image" and choose your photo
3. **Enter Message**: Type your secret message (up to 5 characters)
4. **Optional Settings**:
   - ✅ **Single-Use SQR**: Message deletes after first scan
   - ✅ **Web3 Features**: Upload to IPFS and use blockchain
5. **Click "Embed SQR"**
6. **Save**: Choose where to save your watermarked image

### Scanning a Watermark (Reveal a Message)

1. **Print your watermarked image** or display it on screen
2. **Take a photo** with your phone (make sure the whole image is visible)
3. **Click "Decode SQR" tab**
4. **Select Photo**: Click "Select Photo" and choose your phone photo
5. **Mark Corners**: Click the 4 corners of the watermarked image:
   - Top-left → Top-right → Bottom-right → Bottom-left
6. **Optional**: Enter your Ethereum private key for blockchain proof
7. **Click "Step 3: Computer Vision Processing and Verification"**
8. **See Results**: Your secret message appears!

## 🔧 Troubleshooting

### "No module named 'trustmark'"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "No watermark detected"
- Make sure your photo shows the entire watermarked image
- Click corners more precisely
- Ensure good lighting when taking the photo

### GUI won't start
- Make sure you're in the `yys-sqr` folder
- Check that Python 3.11+ is installed: `python3 --version`

## 💡 Tips for Best Results

1. **High Quality Photos**: Use good lighting and steady hands
2. **Corner Precision**: Click exactly on the corners of the image
3. **Print Quality**: Use high-quality printer settings
4. **Message Length**: Keep messages short (5 characters max)

## 🎯 Example Workflow

1. **Embed**: Hide "HELLO" in `photo.jpg` → saves `watermarked.png`
2. **Print**: Print `watermarked.png` on paper
3. **Photo**: Take phone photo of printed image
4. **Scan**: Load phone photo, click corners, decode
5. **Result**: "HELLO" appears + blockchain proof recorded!

## Need More Help?

- Check `INSTALL.md` for detailed installation
- See `USER_GUIDE.md` for complete feature documentation
- Review `TROUBLESHOOTING.md` for common issues