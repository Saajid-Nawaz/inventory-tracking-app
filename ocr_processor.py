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
        
        # Preprocess image for better OCR results
        processed_image = preprocess_image_for_ocr(image)
        
        # Extract text using OCR with custom configuration
        custom_config = r'--oem 3 --psm 6'  # Assume uniform block of text
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        logging.info(f"OCR extracted text: {text}")
        
        # Also try with different PSM modes for better results
        if not text.strip():
            custom_config = r'--oem 3 --psm 4'  # Assume single column of text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            logging.info(f"OCR extracted text (PSM 4): {text}")
        
        # Parse the extracted text to find materials and quantities
        materials = parse_materials_from_text(text)
        
        return materials
        
    except Exception as e:
        logging.error(f"Error in OCR processing: {str(e)}")
        raise e

def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy
    """
    import numpy as np
    
    # Convert PIL image to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        # Convert RGB to grayscale
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        gray = img_array
    
    # Convert back to PIL Image
    processed_image = Image.fromarray(gray.astype('uint8'))
    
    # Resize image if too small (minimum 300 DPI equivalent)
    width, height = processed_image.size
    if width < 1000 or height < 1000:
        scale_factor = max(1000/width, 1000/height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return processed_image

def parse_materials_from_text(text):
    """
    Parse the OCR text to extract material information
    Enhanced to handle invoice formats with Description and Qty columns
    """
    materials = []
    
    # Split text into lines for processing
    lines = text.split('\n')
    
    # First, try to parse invoice format (Description and Qty columns)
    invoice_materials = parse_invoice_format(lines)
    if invoice_materials:
        materials.extend(invoice_materials)
    
    # If no invoice format found, try standard patterns
    if not materials:
        materials = parse_standard_format(lines)
    
    # Remove duplicates and clean up
    unique_materials = []
    seen = set()
    
    for material in materials:
        key = (material['name'].lower(), material['unit'])
        if key not in seen:
            seen.add(key)
            unique_materials.append(material)
    
    logging.info(f"Extracted materials: {unique_materials}")
    return unique_materials

def parse_invoice_format(lines):
    """
    Parse invoice format where materials are listed with Description and Qty columns
    """
    materials = []
    
    # Look for lines that contain both description and quantity
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Skip header lines
        if any(header in line.lower() for header in ['description', 'qty', 'rate', 'amount', 'total']):
            continue
            
        # Look for lines with material descriptions and quantities
        # Pattern: Description text followed by quantity (various formats)
        
        # Try to find quantity patterns in the line
        qty_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:T|t|units?|pcs?|pieces?|bags?|kg|kgs?|m|meters?|metres?|ft|feet|l|liters?|litres?)',
            r'(\d+(?:\.\d+)?)\s+(?=\d+\.\d+|\d+$)',  # Quantity followed by price
            r'(\d+(?:\.\d+)?)\s*$',  # Quantity at end of line
            r'(\d+(?:\.\d+)?)\s+[A-Z]',  # Quantity followed by uppercase letter
        ]
        
        # Extract potential material names and quantities
        for pattern in qty_patterns:
            matches = re.findall(pattern, line)
            if matches:
                try:
                    quantity = float(matches[0])
                    if quantity > 0:
                        # Extract material name (everything before the quantity)
                        material_name = extract_material_name(line, matches[0])
                        if material_name:
                            # Try to determine unit
                            unit = determine_unit(line, material_name)
                            materials.append({
                                'name': material_name,
                                'quantity': quantity,
                                'unit': unit
                            })
                except ValueError:
                    continue
    
    return materials

def parse_standard_format(lines):
    """
    Parse standard material listing format
    """
    materials = []
    
    # Common construction materials patterns
    material_patterns = [
        # Material name followed by quantity and unit
        r'(?i)(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board|trap|shower|valve|strap|arm|head)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(bags?|tons?|tonnes?|kg|kgs?|pieces?|pcs?|meters?|metres?|m|ft|feet|liters?|litres?|l|cubic|m3|units?)',
        
        # Quantity followed by unit and material name
        r'(?i)(\d+(?:\.\d+)?)\s*(bags?|tons?|tonnes?|kg|kgs?|pieces?|pcs?|meters?|metres?|m|ft|feet|liters?|litres?|l|cubic|m3|units?)\s*(?:of\s+)?(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board|trap|shower|valve|strap|arm|head)',
        
        # Simple quantity and material patterns
        r'(?i)(\d+(?:\.\d+)?)\s*(cement|concrete|steel|brick|sand|gravel|rebar|pipe|wire|cable|timber|wood|plywood|board|trap|shower|valve|strap|arm|head)'
    ]
    
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
    
    return materials

def extract_material_name(line, quantity_str):
    """
    Extract material name from invoice line by removing quantity and other non-material text
    """
    # Remove the quantity from the line
    line_parts = line.split()
    material_parts = []
    
    for part in line_parts:
        # Skip numbers, prices, and common non-material words
        if (not re.match(r'^\d+(?:\.\d+)?$', part) and 
            not re.match(r'^\d+\.\d+$', part) and
            not part.lower() in ['qty', 'rate', 'amount', 'total', 'tax', 'vat', 'k', 'tpin', 'user', 'time', 'hrs']):
            material_parts.append(part)
    
    if material_parts:
        material_name = ' '.join(material_parts[:4])  # Take first 4 words max
        # Clean up the material name
        material_name = re.sub(r'[^\w\s]', ' ', material_name)
        material_name = ' '.join(material_name.split())  # Remove extra spaces
        return material_name.title()
    
    return None

def determine_unit(line, material_name):
    """
    Determine the unit of measurement based on material name and context
    """
    line_lower = line.lower()
    material_lower = material_name.lower()
    
    # Check for explicit units in the line
    if any(unit in line_lower for unit in ['kg', 'kgs', 'kilogram']):
        return 'kg'
    elif any(unit in line_lower for unit in ['bag', 'bags']):
        return 'bags'
    elif any(unit in line_lower for unit in ['ton', 'tons', 'tonne', 'tonnes']):
        return 'tons'
    elif any(unit in line_lower for unit in ['meter', 'metres', 'meters', 'm']):
        return 'meters'
    elif any(unit in line_lower for unit in ['liter', 'liters', 'litres', 'l']):
        return 'liters'
    elif any(unit in line_lower for unit in ['piece', 'pieces', 'pcs', 'pc']):
        return 'pieces'
    
    # Infer unit based on material type
    if any(keyword in material_lower for keyword in ['cement', 'concrete', 'sand', 'gravel']):
        return 'bags'
    elif any(keyword in material_lower for keyword in ['steel', 'rebar', 'iron']):
        return 'kg'
    elif any(keyword in material_lower for keyword in ['pipe', 'cable', 'wire', 'timber', 'wood']):
        return 'meters'
    elif any(keyword in material_lower for keyword in ['brick', 'block', 'tile']):
        return 'pieces'
    elif any(keyword in material_lower for keyword in ['trap', 'valve', 'shower', 'head', 'arm']):
        return 'pieces'
    
    # Default unit
    return 'units'
