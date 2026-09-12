import os
from rembg import remove, new_session

def remove_product_background(input_path, output_path, model_name="birefnet-general"):
    """
    Removes the background from a product image and saves it as a transparent PNG.
    """
    # 1. Validate the file exists
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' was not found.")
        return

    print(f"Initializing AI model: {model_name}...")
    # 2. Create a session to reuse the model (improves performance)
    session = new_session(model_name)

    print("Reading image data...")
    # 3. Read the image as raw bytes
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()

    print("Executing background removal...")
    # 4. Remove the background using the session
    output_data = remove(input_data, session=session)

    print("Saving transparent product image...")
    # 5. Write the resulting bytes to the new file
    with open(output_path, 'wb') as output_file:
        output_file.write(output_data)

    print(f"Success! The cutout image has been saved to: {output_path}")

# --- Test the function ---
# Make sure you have a test image named 'test_photo.jpg' in the same folder.
# The output MUST be a .png file to preserve the transparency.
remove_product_background('image4.jpg', 'product_cutout4.png')