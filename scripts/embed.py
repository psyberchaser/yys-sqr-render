import argparse
from PIL import Image
from trustmark import TrustMark

def main(args):
    """
    Embeds a watermark into an image using TrustMark, saves it,
    and then decodes it to verify the process.
    """
    # --- 1. Initialize TrustMark ---
    # We use schema 0 for the strongest ECC (BCH_SUPER)
    # We use model_type 'Q' for quality, as recommended for photos
    print("Starting up...")
    tm = TrustMark(verbose=False, model_type='Q', encoding_type=TrustMark.Encoding.BCH_SUPER)

    # --- 2. Load Image ---
    print(f"Loading image: {args.input_image}")
    try:
        cover_image = Image.open(args.input_image).convert('RGB')
    except FileNotFoundError:
        print(f"Error: Input image not found at '{args.input_image}'")
        return

    # --- 3. Embed Watermark ---
    message = "OK"
    print(f"Embedding message: '{message}'")
    watermarked_image = tm.encode(cover_image, message)
    watermarked_image.save(args.output_image)
    print(f"Saved watermarked image to: {args.output_image}")

    # --- 4. Decode Watermark for Verification ---
    print("\n--- Verification Step ---")
    print(f"Loading watermarked image for decoding: {args.output_image}")
    image_to_decode = Image.open(args.output_image).convert('RGB')
    
    secret, present, _ = tm.decode(image_to_decode)

    if present:
        print(f"Watermark detected!")
        print(f"Decoded message: '{secret}'")
        if secret == message:
            print("SUCCESS: Decoded message matches original message.")
        else:
            print("FAILURE: Decoded message does not match original.")
    else:
        print("FAILURE: No watermark detected in the output image.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed and verify a TrustMark watermark.")
    parser.add_argument("--input_image", type=str, default="/Users/parallel/encoded/doom.jpg", help="Path to the input image.")
    parser.add_argument("--output_image", type=str, default="doom_watermarked.png", help="Path to save the watermarked image.")
    args = parser.parse_args()
    main(args) 