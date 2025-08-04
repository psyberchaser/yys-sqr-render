import argparse
from PIL import Image
from trustmark import TrustMark

def main(args):
    """
    Decodes a watermark from an image using TrustMark.
    """
    # --- 1. Initialize TrustMark ---
    # Must use the same settings as the encoder
    print("Starting up...")
    tm = TrustMark(verbose=False, model_type='Q', encoding_type=TrustMark.Encoding.BCH_SUPER)

    # --- 2. Load Image ---
    print(f"Loading image for decoding: {args.image_to_decode}")
    try:
        image_to_decode = Image.open(args.image_to_decode).convert('RGB')
    except FileNotFoundError:
        print(f"Error: Input image not found at '{args.image_to_decode}'")
        return

    # --- 3. Decode Watermark ---
    print("Attempting to decode watermark...")
    secret, present, _ = tm.decode(image_to_decode)

    if present:
        print("\n--- RESULT ---")
        print("SUCCESS: Watermark detected!")
        print(f"Decoded message: '{secret}'")
    else:
        print("\n--- RESULT ---")
        print("FAILURE: No watermark was detected in the image.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode a TrustMark watermark from an image.")
    parser.add_argument("image_to_decode", type=str, help="Path to the watermarked image to decode.")
    args = parser.parse_args()
    main(args) 