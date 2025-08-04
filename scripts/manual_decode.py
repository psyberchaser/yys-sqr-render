import cv2
import numpy as np
import argparse
from PIL import Image
from trustmark import TrustMark

# Global list to store the clicked points
points = []

def click_event(event, x, y, flags, params):
    """Callback function to record clicks."""
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"Point {len(points)} captured: ({x}, {y})") # Print point immediately
            # Draw a circle on the image to show where the user clicked
            cv2.circle(params['img'], (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("image", params['img'])

def main(args):
    """
    Displays an image, waits for 4 corner clicks, performs perspective correction,
    and then attempts to decode a TrustMark watermark.
    """
    global points
    
    img_cv = cv2.imread(args.image_path)
    if img_cv is None:
        print(f"Error: Could not load image from {args.image_path}")
        return
        
    cv2.imshow('image', img_cv)
    cv2.setMouseCallback('image', click_event, {'img': img_cv})
    
    print("Please click on the 4 corners of the watermarked region in this order:")
    print("1. Top-Left -> 2. Top-Right -> 3. Bottom-Right -> 4. Bottom-Left")
    print("Press any key after clicking the 4th corner to proceed...")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(points) != 4:
        print(f"Error: Expected 4 points, but got {len(points)}. Please try again.")
        return

    # Save coordinates to a file to bypass hanging issue
    try:
        with open("coords.txt", "w") as f:
            f.write(str(points))
        print("Successfully saved coordinates to coords.txt")
    except Exception as e:
        print(f"Error saving coordinates: {e}")
        return

    # --- Correct Perspective ---
    src_points = np.float32(points)
    
    # Define the destination image size (we'll warp it to a square)
    width = 512
    height = 512
    dst_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    
    # Compute the perspective transform matrix and apply it
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped_cv = cv2.warpPerspective(img_cv, matrix, (width, height))
    
    # Convert back to PIL Image for the decoder
    corrected_image_pil = Image.fromarray(cv2.cvtColor(warped_cv, cv2.COLOR_BGR2RGB))
    
    # Save the corrected image for inspection
    corrected_image_pil.save("trustmark_corrected.png")
    print("Saved perspective-corrected image to 'trustmark_corrected.png'")

    # --- Decode Watermark ---
    print("\nStarting up...")
    tm = TrustMark(verbose=False, model_type='Q', encoding_type=TrustMark.Encoding.BCH_SUPER)
    
    print("Attempting to decode watermark from corrected image...")
    secret, present, _ = tm.decode(corrected_image_pil)
    
    if present:
        print("\n--- RESULT ---")
        print("SUCCESS: Watermark detected!")
        print(f"Decoded message: '{secret}'")
    else:
        print("\n--- RESULT ---")
        print("FAILURE: No watermark was detected in the image.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manually correct perspective and decode a TrustMark watermark.")
    parser.add_argument("image_path", type=str, help="Path to the watermarked image photo.")
    args = parser.parse_args()
    main(args) 