import cv2
import numpy as np

def format_ecommerce_canvas(rgba_image, canvas_size=1080, padding=120):
    """
    Takes an RGBA image (output from rembg) and formats it onto a professional
    1080x1080 white canvas with a soft drop shadow.
    Returns: (success: bool, final_image_matrix, message: str)
    """
    if rgba_image is None or rgba_image.shape[2] != 4:
        return False, None, "Error: Expected a 4-channel RGBA image from rembg."

    # 1. Calculate Dimensions (Maintain Aspect Ratio)
    h, w = rgba_image.shape[:2]
    max_dim = canvas_size - (padding * 2)
    scale = max_dim / max(h, w)
    
    new_w, new_h = int(w * scale), int(h * scale)
    resized_img = cv2.resize(rgba_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # 2. Create the Base White Canvas
    canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255
    
    # Calculate centering coordinates for the product
    x_offset = (canvas_size - new_w) // 2
    y_offset = (canvas_size - new_h) // 2
    
    # 3. Separate Channels (Split the BGR color from the Alpha mask)
    b, g, r, a = cv2.split(resized_img)
    rgb_product = cv2.merge((b, g, r))
    alpha_mask = a.astype(float) / 255.0  # Normalize to 0.0 - 1.0 range
    
    # 4. Generate the Drop Shadow Mathematically
    shadow_offset_y = 25
    shadow_offset_x = 15
    shadow_blur_ksize = 61
    shadow_intensity = 0.5
    
    # Create a completely white mask canvas (values at 1.0)
    shadow_mask = np.ones((canvas_size, canvas_size), dtype=float)
    
    # Subtract the alpha mask to create a dark silhouette (offset slightly down and right)
    shadow_y1, shadow_y2 = y_offset + shadow_offset_y, y_offset + shadow_offset_y + new_h
    shadow_x1, shadow_x2 = x_offset + shadow_offset_x, x_offset + shadow_offset_x + new_w
    
    shadow_mask[shadow_y1:shadow_y2, shadow_x1:shadow_x2] -= (alpha_mask * shadow_intensity)
    
    # Apply Gaussian Blur to soften the silhouette into a realistic shadow
    shadow_mask = cv2.GaussianBlur(shadow_mask, (shadow_blur_ksize, shadow_blur_ksize), 0)
    
    # Multiply the shadow directly into the white canvas
    for i in range(3):
        canvas[:, :, i] = (canvas[:, :, i].astype(float) * shadow_mask).astype(np.uint8)
        
    # 5. Composite the Product onto the Canvas (Alpha Blending)
    for c in range(3):
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] = \
            (alpha_mask * rgb_product[:, :, c] +
             (1 - alpha_mask) * canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c])

    return True, canvas, "Successfully formatted to 1080x1080 white canvas."