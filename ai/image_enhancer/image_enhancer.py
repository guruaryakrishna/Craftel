import torch
import torch.nn as nn
import numpy as np
import cv2
import os

# ==========================================
# 1. AI MODEL ARCHITECTURE (ZERO-DCE)
# ==========================================
class DCE_net(nn.Module):
    def __init__(self):
        super(DCE_net, self).__init__()
        self.relu = nn.ReLU(inplace=True)
        number_f = 32
        
        self.e_conv1 = nn.Conv2d(3, number_f, 3, 1, 1, bias=True)
        self.e_conv2 = nn.Conv2d(number_f, number_f, 3, 1, 1, bias=True)
        self.e_conv3 = nn.Conv2d(number_f, number_f, 3, 1, 1, bias=True)
        self.e_conv4 = nn.Conv2d(number_f, number_f, 3, 1, 1, bias=True)
        self.e_conv5 = nn.Conv2d(number_f*2, number_f, 3, 1, 1, bias=True)
        self.e_conv6 = nn.Conv2d(number_f*2, number_f, 3, 1, 1, bias=True)
        self.e_conv7 = nn.Conv2d(number_f*2, 24, 3, 1, 1, bias=True)

    def forward(self, x):
        x1 = self.relu(self.e_conv1(x))
        x2 = self.relu(self.e_conv2(x1))
        x3 = self.relu(self.e_conv3(x2))
        x4 = self.relu(self.e_conv4(x3))
        x5 = self.relu(self.e_conv5(torch.cat([x3, x4], 1)))
        x6 = self.relu(self.e_conv6(torch.cat([x2, x5], 1)))
        x_r = torch.tanh(self.e_conv7(torch.cat([x1, x6], 1)))

        x_r1, x_r2, x_r3, x_r4, x_r5, x_r6, x_r7, x_r8 = torch.split(x_r, 3, dim=1)
        x = x + x_r1 * (torch.pow(x, 2) - x)
        x = x + x_r2 * (torch.pow(x, 2) - x)
        x = x + x_r3 * (torch.pow(x, 2) - x)
        x = x + x_r4 * (torch.pow(x, 2) - x)
        x = x + x_r5 * (torch.pow(x, 2) - x)
        x = x + x_r6 * (torch.pow(x, 2) - x)
        x = x + x_r7 * (torch.pow(x, 2) - x)
        enhance_image = x + x_r8 * (torch.pow(x, 2) - x)
        
        return enhance_image

# ==========================================
# 2. INITIALIZATION & WEIGHTS LOADING (ON STARTUP)
# ==========================================
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
zero_dce_model = DCE_net().to(DEVICE)
WEIGHTS_PATH = "Epoch99.pth" 

def load_ai_weights():
    """Loads weights once into memory."""
    if not os.path.exists(WEIGHTS_PATH):
        return False, f"Weights file '{WEIGHTS_PATH}' not found."
        
    zero_dce_model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=DEVICE))
    zero_dce_model.eval()
    return True, "Zero-DCE Model Loaded Successfully."

# Initialize model once when the file is imported by the backend
_model_ready, _init_msg = load_ai_weights()

# ==========================================
# 3. PROCEDURAL PROCESSING FUNCTIONS
# ==========================================
def check_lighting_routing(image_matrix, dark_reject=15.0, bright_bypass=110.0):
    """
    Evaluates image brightness.
    Returns: (is_valid: bool, needs_ai: bool, message: str)
    """
    gray = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    
    # Pitch black -> Reject
    if mean_brightness < dark_reject:
        return False, False, f"Rejected: Image is too dark ({mean_brightness:.1f}). Retake with better lighting."

    # Already bright -> Bypass AI
    if mean_brightness > bright_bypass:
        return True, False, f"Accepted: Image is well-lit ({mean_brightness:.1f}). Skipping enhancement."

    # Dim -> Enhance with AI
    return True, True, f"Accepted: Dim lighting detected ({mean_brightness:.1f}). Applying Zero-DCE."

def apply_ai_lighting(image_matrix):
    """
    Applies Zero-DCE enhancement to the in-memory OpenCV matrix.
    """
    img = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2RGB)
    img = (np.asarray(img) / 255.0).astype(np.float32)
    
    img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        enhanced_tensor = zero_dce_model(img_tensor)
        
    enhanced_img = enhanced_tensor.squeeze().permute(1, 2, 0).cpu().numpy()
    enhanced_img = (np.clip(enhanced_img, 0, 1) * 255.0).astype(np.uint8)
    enhanced_bgr = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR)
    
    return enhanced_bgr

# ==========================================
# 4. MAIN BACKEND ENTRY POINT
# ==========================================
def process_lighting_pipeline(image_matrix):
    """
    Takes an OpenCV matrix received by the backend router.
    Returns: (success: bool, output_matrix, message: str)
    """
    if image_matrix is None:
        return False, None, "Invalid image matrix."
        
    if not _model_ready:
        return False, None, "Zero-DCE model weights not loaded."

    is_valid, needs_ai, msg = check_lighting_routing(image_matrix)
    
    if not is_valid:
        return False, None, msg

    if needs_ai:
        processed_image = apply_ai_lighting(image_matrix)
    else:
        processed_image = image_matrix

    return True, processed_image, msg