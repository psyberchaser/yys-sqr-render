# YYS-SQR Installation Guide

## Quick Setup

1. **Navigate to the project directory**:
   ```bash
   cd yys-sqr
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Build macOS App Bundle

To create a standalone macOS application:

```bash
./build.sh
```

The application will be available at `dist/YYS-SQR.app`

## Command Line Tools

All command-line utilities are in the `scripts/` directory:

### Check Watermark Capacity
```bash
python scripts/check_capacity.py
```

### Embed Watermark
```bash
python scripts/embed.py --input_image photo.jpg --output_image watermarked.png
```

### Decode Watermark
```bash
python scripts/decode.py watermarked.png
```

### Manual Perspective Correction
```bash
python scripts/manual_decode.py photo_of_printed_image.jpg
```

## System Requirements

- **Python**: 3.11+ (tested with 3.11.13, 3.12.2)
- **Operating System**: macOS, Linux, Windows
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for blockchain/IPFS features

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure virtual environment is activated
2. **GUI Not Starting**: Check PyQt6 installation
3. **Watermark Not Detected**: Ensure image quality and corner selection accuracy
4. **Blockchain Errors**: Verify private key format and network connectivity

### Getting Help

- Check the complete documentation in `docs/documentation.tex`
- Review error messages in the GUI status display
- Ensure all dependencies are properly installed

## Development

To modify the system:

1. **Edit GUI**: Modify `main.py`
2. **Update Scripts**: Edit files in `scripts/`
3. **Smart Contract**: Modify `contracts/ProofOfScanV2.sol`
4. **Documentation**: Update `docs/documentation.tex`

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.