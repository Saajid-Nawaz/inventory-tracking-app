import pytesseract
from PIL import Image
import re
import logging

# Configure pytesseract path if needed (uncomment and adjust path as needed)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def extract_materials_from_image(image_path):
    """
    Extract material information from an image using OCR
    Returns a list of dictionaries with material_name, quantity, and unit
    """
    try:
        # Open and preprocess image
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        logging.info(f"OCR extracted text: {text}")
        
        # Parse the extracted text to find materials and quantities
        materials = parse_materials_from_text(text)
        
        return materials
        
    except Exception as e:
        logging.error(f"Error in OCR processing: {str(e)}")
        raise e

def parse_materials_from_text(text):
    """
    Parse the OCR text to extract material information
    This is a basic implementation that can be improved with more sophisticated parsing
    """
    materials = []
    
    # Common construction materials patterns
    material_patterns = [
        # Material name followed by quantity and unit
        r'(?i)(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(bags?|tons?|tonnes?|kg|kgs?|pieces?|pcs?|meters?|metres?|m|ft|feet|liters?|litres?|l|cubic|m3|units?)',
        
        # Quantity followed by unit and material name
        r'(?i)(\d+(?:\.\d+)?)\s*(bags?|tons?|tonnes?|kg|kgs?|pieces?|pcs?|meters?|metres?|m|ft|feet|liters?|litres?|l|cubic|m3|units?)\s*(?:of\s+)?(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board)',
        
        # Simple quantity and material patterns
        r'(?i)(\d+(?:\.\d+)?)\s*(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board)'
    ]
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try each pattern
        for pattern in material_patterns:
            matches = re.findall(pattern, line)
            
            for match in matches:
                if len(match) == 3:  # material, quantity, unit
                    material_name, quantity, unit = match
                    try:
                        quantity = float(quantity)
                        materials.append({
                            'name': material_name.capitalize(),
                            'quantity': quantity,
                            'unit': unit.lower()
                        })
                    except ValueError:
                        continue
                elif len(match) == 2:  # quantity, material (no unit)
                    quantity, material_name = match
                    try:
                        quantity = float(quantity)
                        materials.append({
                            'name': material_name.capitalize(),
                            'quantity': quantity,
                            'unit': 'units'  # default unit
                        })
                    except ValueError:
                        continue
    
    # Remove duplicates and clean up
    unique_materials = []
    seen = set()
    
    for material in materials:
        key = (material['name'].lower(), material['unit'])
        if key not in seen:
            seen.add(key)
            unique_materials.append(material)
    
    # If no materials found, try a more general approach
    if not unique_materials:
        # Look for any numbers in the text and common materials
        common_materials = ['cement', 'concrete', 'steel', 'brick', 'sand', 'gravel', 'rebar', 'pipe', 'wire', 'cable', 'timber', 'wood', 'plywood', 'board']
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        for material in common_materials:
            if material.lower() in text.lower():
                # Try to find a number near this material
                for num in numbers:
                    try:
                        quantity = float(num)
                        if quantity > 0:
                            unique_materials.append({
                                'name': material.capitalize(),
                                'quantity': quantity,
                                'unit': 'units'
                            })
                            break
                    except ValueError:
                        continue
    
    logging.info(f"Extracted materials: {unique_materials}")
    return unique_materials
