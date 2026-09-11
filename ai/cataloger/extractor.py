import os
import json
from typing import Literal, Optional
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# Define your exact target subcategories per category
CATEGORY_MAPPING = {
    "1. Handloom & Textiles": [
        "Sarees", "Dupattas", "Shawls", "Stoles", "Scarves", "Dress materials",
        "Fabrics", "Bedsheets", "Towels", "Rugs", "Carpets", "Durries", 
        "Blankets", "Handwoven bags", "Traditional garments", "Other / General"
    ],
    "2. Paintings & Art": [
        "Madhubani paintings", "Warli paintings", "Kalamkari", "Pattachitra", 
        "Gond art", "Tanjore paintings", "Miniature paintings", "Phad paintings", 
        "Folk paintings", "Handmade wall art", "Sketches/illustrations", "Other / General"
    ],
    "3. Pottery & Terracotta": [
        "Clay pots", "Diyas", "Vases", "Planters", "Decorative pots", 
        "Terracotta jewellery", "Terracotta figurines", "Kitchenware", 
        "Sculptures", "Clay lamps", "Other / General"
    ],
    "4. Ceramics": [
        "Cups", "Mugs", "Plates", "Bowls", "Vases", "Tableware", 
        "Decorative pieces", "Ceramic jewellery", "Home décor", "Other / General"
    ],
    "5. Bamboo, Cane & Natural Fibre": [
        "Baskets", "Mats", "Trays", "Lampshades", "Furniture", 
        "Storage boxes", "Bags", "Decorative items", "Bamboo bottles/containers", 
        "Household products", "Other / General"
    ],
    "6. Woodcraft": [
        "Wooden toys", "Sculptures", "Figurines", "Furniture", "Boxes", 
        "Trays", "Kitchenware", "Decorative panels", "Wall décor", 
        "Wooden jewellery", "Other / General"
    ],
    "7. Handmade Jewellery": [
        "Beaded jewellery", "Terracotta jewellery", "Wooden jewellery", 
        "Metal jewellery", "Tribal jewellery", "Lac jewellery", 
        "Handmade earrings", "Necklaces", "Bracelets", "Bangles", "Other / General"
    ],
    "8. Handmade Home Décor": [
        "Wall hangings", "Lamps", "Candles", "Decorative boxes", "Mirrors", 
        "Showpieces", "Sculptures", "Table décor", "Dreamcatchers", 
        "Handmade clocks", "Other / General"
    ],
    "9. Handmade Bags & Accessories": [
        "Handbags", "Tote bags", "Clutches", "Pouches", "Wallets", 
        "Backpacks", "Baskets", "Handmade belts", "Scarves", "Accessories", "Other / General"
    ],
    "10. Handmade Toys": [
        "Wooden toys", "Cloth dolls", "Stuffed toys", "Traditional toys", 
        "Puppets", "Educational toys", "Handmade games", "Other / General"
    ],
    "11. Embroidery & Needlecraft": [
        "Embroidered clothing", "Embroidered bags", "Cushion covers", 
        "Wall hangings", "Table runners", "Quilts", "Patchwork products", "Other / General"
    ],
    "12. Leather & Traditional Craft": [
        "Leather bags", "Wallets", "Footwear", "Belts", 
        "Traditional leather crafts", "Decorative leather products", "Other / General"
    ],
    "13. Metal Crafts": [
        "Brassware", "Copperware", "Bell-metal products", "Metal sculptures", 
        "Lamps", "Utensils", "Decorative items", "Jewellery", "Other / General"
    ],
    "14. Natural / Eco-friendly Crafts": [
        "Jute products", "Coir products", "Palm-leaf products", 
        "Banana-fibre products", "Natural-fibre baskets", 
        "Eco-friendly packaging", "Handmade paper products", "Other / General"
    ]
}

# Define Pydantic Schema for Enforcement
MajorCategoryType = Literal[
    "1. Handloom & Textiles", "2. Paintings & Art", "3. Pottery & Terracotta",
    "4. Ceramics", "5. Bamboo, Cane & Natural Fibre", "6. Woodcraft",
    "7. Handmade Jewellery", "8. Handmade Home Décor", "9. Handmade Bags & Accessories",
    "10. Handmade Toys", "11. Embroidery & Needlecraft", "12. Leather & Traditional Craft",
    "13. Metal Crafts", "14. Natural / Eco-friendly Crafts", "Not a valid craft/artisan product"
]

class ProductInformationExtractor(BaseModel):
    is_valid_artisan_product: bool = Field(description="True if the image contains an artisan, handicraft, or textile product.")
    major_category: MajorCategoryType = Field(description="The primary category matching the list.")
    sub_category: str = Field(description="The specific subcategory detected from the list.")
    materials_detected: list[str] = Field(description="Materials identified visually (e.g., Clay, Silk, Brass, Bamboo, Terracotta).")
    visual_features: list[str] = Field(description="Key patterns, colors, or art styles (e.g., Block print, Floral, Madhubani motif, Antiqued finish).")
    confidence_score: float = Field(description="Confidence rating between 0.0 and 1.0.")
    brief_summary: str = Field(description="A concise 1-sentence description of the item.")


def extract_product_data(image_path: str) -> dict:
    """
    Extracts structured classification data from an uploaded handicraft image via online Gemini API.
    """
    
    # Load and prepare image
    image = Image.open(image_path)
    
    prompt = f"""
    You are an expert e-commerce cataloger for Indian micro-entrepreneurs, artisans, and weavers.
    Analyze the provided product photograph and extract key information.

    Classify the product into ONE of these major categories:
    {list(CATEGORY_MAPPING.keys())}

    Select the sub-category using the mapping below:
    {json.dumps(CATEGORY_MAPPING, indent=2)}

    If the image is completely unrelated (e.g., a document, selfie, landscape, or generic modern machine item), 
    set `is_valid_artisan_product` to false and `major_category` to "Not a valid craft/artisan product".
    """

    # Call Gemini API with structured schema response format
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProductInformationExtractor,
            temperature=0.1
        )
    )

    # Parse JSON output string back to Python dictionary
    return json.loads(response.text)


if __name__ == "__main__":
    # Fixed file path using raw string prefix r"..."
    sample_image = r"C:\coding\projects\Craftel\test\image2.jpeg"
    
    if os.path.exists(sample_image):
        extracted_data = extract_product_data(sample_image)
        print(json.dumps(extracted_data, indent=2))
    else:
        print(f"Please place a valid test photo at '{sample_image}' to test.")