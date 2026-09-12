import cv2

BLUR_THRESHOLD = 150.0

def validate_image_sharpness(image_matrix, max_dimension=1024):
    """
    Takes an in-memory OpenCV matrix.
    Returns: (is_valid: bool, score: float, message: str)
    """
    if image_matrix is None:
        return False, 0.0, "Error: Invalid image matrix provided."

    # 1. Standardize resolution to ensure the 150.0 threshold works universally
    h, w = image_matrix.shape[:2]
    scale = max_dimension / max(h, w)
    
    if scale < 1.0:
        target_w, target_h = int(w * scale), int(h * scale)
        evaluation_frame = cv2.resize(image_matrix, (target_w, target_h), interpolation=cv2.INTER_AREA)
    else:
        evaluation_frame = image_matrix

    # 2. Compute Laplacian Variance
    gray = cv2.cvtColor(evaluation_frame, cv2.COLOR_BGR2GRAY)
    sharpness_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 3. Return actionable data to the API router
    if sharpness_score < BLUR_THRESHOLD:
        return False, sharpness_score, f"Rejected: Image is too blurry for the digital marketplace. (Score: {sharpness_score:.2f})"
    
    return True, sharpness_score, f"Accepted: Image is sharp and ready for AI processing. (Score: {sharpness_score:.2f})"