import numpy as np
import cv2
from rembg import remove, new_session

# Initialize session once globally to optimize performance
_rembg_session = new_session("birefnet-general")

def remove_product_background(image_matrix):
    """
    Takes an in-memory OpenCV BGR matrix.
    Removes the background using rembg and returns a 4-channel BGRA OpenCV matrix.
    """
    if image_matrix is None:
        return False, None, "Error: Invalid image matrix provided for background removal."

    # 1. Encode OpenCV matrix to PNG bytes in memory
    success, encoded_img = cv2.imencode('.png', image_matrix)
    if not success:
        return False, None, "Error: Failed to encode image for background removal."
    
    input_bytes = encoded_img.tobytes()

    # 2. Execute background removal using the pre-loaded session
    try:
        output_bytes = remove(input_bytes, session=_rembg_session)
    except Exception as e:
        return False, None, f"Error during background removal execution: {str(e)}"

    # 3. Decode output bytes back into a 4-channel BGRA OpenCV matrix (preserving alpha)
    rgba_matrix = cv2.imdecode(np.frombuffer(output_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

    if rgba_matrix is None or rgba_matrix.shape[2] != 4:
        return False, None, "Error: Background removal output is not a valid 4-channel RGBA image."

    return True, rgba_matrix, "Background removed successfully."