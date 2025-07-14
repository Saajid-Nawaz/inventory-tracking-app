"""
Bulk import script for construction materials from the provided list
"""

import pandas as pd
from app import app, db
from models_new import Material

# Comprehensive materials list from the provided image
materials_data = [
    # AGGREGATES
    {'name': 'Quarry Sand', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 45.00, 'minimum_level': 20, 'description': 'Fine sand from quarry operations'},
    {'name': 'Quarry Stone', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 55.00, 'minimum_level': 25, 'description': 'Coarse stone aggregate'},
    {'name': 'Building Sand', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 42.00, 'minimum_level': 18, 'description': 'Construction grade sand'},
    {'name': 'River Sand', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 48.00, 'minimum_level': 15, 'description': 'Natural river sand'},
    {'name': 'Crusher Run', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 38.00, 'minimum_level': 30, 'description': 'Crushed stone base material'},
    {'name': 'Gravel 10mm', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 52.00, 'minimum_level': 20, 'description': '10mm gravel aggregate'},
    {'name': 'Gravel 19mm', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 55.00, 'minimum_level': 20, 'description': '19mm gravel aggregate'},
    {'name': 'Black Soil', 'unit': 'tonnes', 'category': 'Aggregates', 'cost_per_unit': 35.00, 'minimum_level': 10, 'description': 'Rich black soil for landscaping'},
    
    # MASONRY
    {'name': '8 Inch Blocks', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 3.50, 'minimum_level': 500, 'description': '8 inch concrete blocks'},
    {'name': '6 Inch Blocks', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 2.75, 'minimum_level': 750, 'description': '6 inch concrete blocks'},
    {'name': '4 Inch Blocks', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 2.25, 'minimum_level': 1000, 'description': '4 inch concrete blocks'},
    {'name': 'Bricks Common', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 0.65, 'minimum_level': 5000, 'description': 'Common construction bricks'},
    {'name': 'Bricks Face', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 0.85, 'minimum_level': 2000, 'description': 'Face bricks for exterior'},
    {'name': 'Cement Blocks', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 4.20, 'minimum_level': 300, 'description': 'Solid cement blocks'},
    {'name': 'Hollow Blocks', 'unit': 'EA', 'category': 'Masonry', 'cost_per_unit': 3.80, 'minimum_level': 400, 'description': 'Hollow concrete blocks'},
    
    # CONSTRUCTION
    {'name': 'Portland Cement', 'unit': 'bags', 'category': 'Construction', 'cost_per_unit': 12.50, 'minimum_level': 200, 'description': 'OPC 42.5 grade cement'},
    {'name': 'Rapid Set Cement', 'unit': 'bags', 'category': 'Construction', 'cost_per_unit': 18.75, 'minimum_level': 50, 'description': 'Quick setting cement'},
    {'name': 'Masonry Cement', 'unit': 'bags', 'category': 'Construction', 'cost_per_unit': 14.25, 'minimum_level': 100, 'description': 'Cement for masonry work'},
    {'name': 'Lime', 'unit': 'bags', 'category': 'Construction', 'cost_per_unit': 8.50, 'minimum_level': 75, 'description': 'Hydrated lime for mortar'},
    {'name': 'Ready Mix Concrete', 'unit': 'm3', 'category': 'Construction', 'cost_per_unit': 120.00, 'minimum_level': 5, 'description': 'Ready mixed concrete'},
    
    # REINFORCEMENT
    {'name': 'Rebar 8mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.85, 'minimum_level': 2000, 'description': '8mm reinforcement steel'},
    {'name': 'Rebar 10mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.82, 'minimum_level': 2500, 'description': '10mm reinforcement steel'},
    {'name': 'Rebar 12mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.80, 'minimum_level': 3000, 'description': '12mm reinforcement steel'},
    {'name': 'Rebar 16mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.78, 'minimum_level': 2000, 'description': '16mm reinforcement steel'},
    {'name': 'Rebar 20mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.75, 'minimum_level': 1500, 'description': '20mm reinforcement steel'},
    {'name': 'Rebar 25mm', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 0.72, 'minimum_level': 1000, 'description': '25mm reinforcement steel'},
    {'name': 'Binding Wire', 'unit': 'kg', 'category': 'Construction', 'cost_per_unit': 1.25, 'minimum_level': 500, 'description': 'Wire for binding rebar'},
    
    # TIMBER
    {'name': 'Timber 2x4', 'unit': 'pieces', 'category': 'Timber', 'cost_per_unit': 8.50, 'minimum_level': 200, 'description': '2x4 inch timber'},
    {'name': 'Timber 2x6', 'unit': 'pieces', 'category': 'Timber', 'cost_per_unit': 12.75, 'minimum_level': 150, 'description': '2x6 inch timber'},
    {'name': 'Timber 2x8', 'unit': 'pieces', 'category': 'Timber', 'cost_per_unit': 18.25, 'minimum_level': 100, 'description': '2x8 inch timber'},
    {'name': 'Timber 4x4', 'unit': 'pieces', 'category': 'Timber', 'cost_per_unit': 22.50, 'minimum_level': 75, 'description': '4x4 inch timber posts'},
    {'name': 'Plywood 12mm', 'unit': 'sheets', 'category': 'Timber', 'cost_per_unit': 35.00, 'minimum_level': 50, 'description': '12mm plywood sheets'},
    {'name': 'Plywood 18mm', 'unit': 'sheets', 'category': 'Timber', 'cost_per_unit': 52.00, 'minimum_level': 40, 'description': '18mm plywood sheets'},
    {'name': 'Plywood 25mm', 'unit': 'sheets', 'category': 'Timber', 'cost_per_unit': 72.00, 'minimum_level': 30, 'description': '25mm plywood sheets'},
    
    # ROOFING
    {'name': 'Roofing Sheets IBR', 'unit': 'sheets', 'category': 'Roofing', 'cost_per_unit': 28.50, 'minimum_level': 100, 'description': 'IBR roofing sheets'},
    {'name': 'Roofing Sheets Corrugated', 'unit': 'sheets', 'category': 'Roofing', 'cost_per_unit': 24.75, 'minimum_level': 120, 'description': 'Corrugated roofing sheets'},
    {'name': 'Ridge Tiles', 'unit': 'pieces', 'category': 'Roofing', 'cost_per_unit': 15.50, 'minimum_level': 50, 'description': 'Ridge tiles for roof'},
    {'name': 'Roof Screws', 'unit': 'boxes', 'category': 'Hardware', 'cost_per_unit': 12.25, 'minimum_level': 25, 'description': 'Self-drilling roof screws'},
    {'name': 'Gutters', 'unit': 'meters', 'category': 'Roofing', 'cost_per_unit': 18.75, 'minimum_level': 100, 'description': 'Rain gutters'},
    
    # ELECTRICAL
    {'name': 'Electrical Wire 1.5mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 2.15, 'minimum_level': 500, 'description': '1.5mm electrical wire'},
    {'name': 'Electrical Wire 2.5mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 3.25, 'minimum_level': 400, 'description': '2.5mm electrical wire'},
    {'name': 'Electrical Wire 4mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 4.85, 'minimum_level': 300, 'description': '4mm electrical wire'},
    {'name': 'Electrical Wire 6mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 6.50, 'minimum_level': 200, 'description': '6mm electrical wire'},
    {'name': 'Conduit 20mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 2.75, 'minimum_level': 200, 'description': '20mm electrical conduit'},
    {'name': 'Conduit 25mm', 'unit': 'meters', 'category': 'Electrical', 'cost_per_unit': 3.25, 'minimum_level': 150, 'description': '25mm electrical conduit'},
    {'name': 'Socket Outlets', 'unit': 'pieces', 'category': 'Electrical', 'cost_per_unit': 8.50, 'minimum_level': 50, 'description': 'Electrical socket outlets'},
    {'name': 'Light Switches', 'unit': 'pieces', 'category': 'Electrical', 'cost_per_unit': 6.25, 'minimum_level': 75, 'description': 'Light switches'},
    
    # PLUMBING
    {'name': 'PVC Pipe 110mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 15.75, 'minimum_level': 100, 'description': '110mm PVC drainage pipe'},
    {'name': 'PVC Pipe 160mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 28.50, 'minimum_level': 75, 'description': '160mm PVC drainage pipe'},
    {'name': 'PVC Pipe 75mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 12.25, 'minimum_level': 125, 'description': '75mm PVC pipe'},
    {'name': 'PVC Pipe 50mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 8.75, 'minimum_level': 150, 'description': '50mm PVC pipe'},
    {'name': 'Copper Pipes 15mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 12.50, 'minimum_level': 100, 'description': '15mm copper pipes'},
    {'name': 'Copper Pipes 22mm', 'unit': 'meters', 'category': 'Plumbing', 'cost_per_unit': 18.75, 'minimum_level': 75, 'description': '22mm copper pipes'},
    {'name': 'Pipe Fittings', 'unit': 'pieces', 'category': 'Plumbing', 'cost_per_unit': 5.25, 'minimum_level': 200, 'description': 'Various pipe fittings'},
    {'name': 'Pipe Joints', 'unit': 'pieces', 'category': 'Plumbing', 'cost_per_unit': 3.75, 'minimum_level': 300, 'description': 'Pipe joint connectors'},
    
    # FINISHING
    {'name': 'Wall Tiles', 'unit': 'square meters', 'category': 'Finishing', 'cost_per_unit': 28.50, 'minimum_level': 100, 'description': 'Ceramic wall tiles'},
    {'name': 'Floor Tiles', 'unit': 'square meters', 'category': 'Finishing', 'cost_per_unit': 32.75, 'minimum_level': 150, 'description': 'Floor tiles'},
    {'name': 'Tile Adhesive', 'unit': 'bags', 'category': 'Finishing', 'cost_per_unit': 18.25, 'minimum_level': 50, 'description': 'Tile adhesive'},
    {'name': 'Tile Grout', 'unit': 'bags', 'category': 'Finishing', 'cost_per_unit': 12.50, 'minimum_level': 30, 'description': 'Tile grout'},
    {'name': 'Paint Primer', 'unit': 'litres', 'category': 'Finishing', 'cost_per_unit': 25.00, 'minimum_level': 40, 'description': 'Paint primer'},
    {'name': 'Paint Emulsion', 'unit': 'litres', 'category': 'Finishing', 'cost_per_unit': 35.00, 'minimum_level': 60, 'description': 'Emulsion paint'},
    {'name': 'Paint Gloss', 'unit': 'litres', 'category': 'Finishing', 'cost_per_unit': 42.50, 'minimum_level': 30, 'description': 'Gloss paint'},
    {'name': 'Paint Brushes', 'unit': 'pieces', 'category': 'Finishing', 'cost_per_unit': 8.50, 'minimum_level': 25, 'description': 'Paint brushes'},
    {'name': 'Paint Rollers', 'unit': 'pieces', 'category': 'Finishing', 'cost_per_unit': 12.75, 'minimum_level': 20, 'description': 'Paint rollers'},
    
    # HARDWARE
    {'name': 'Nails 50mm', 'unit': 'kg', 'category': 'Hardware', 'cost_per_unit': 3.25, 'minimum_level': 50, 'description': '50mm construction nails'},
    {'name': 'Nails 75mm', 'unit': 'kg', 'category': 'Hardware', 'cost_per_unit': 3.50, 'minimum_level': 40, 'description': '75mm construction nails'},
    {'name': 'Nails 100mm', 'unit': 'kg', 'category': 'Hardware', 'cost_per_unit': 3.75, 'minimum_level': 30, 'description': '100mm construction nails'},
    {'name': 'Screws Wood 50mm', 'unit': 'boxes', 'category': 'Hardware', 'cost_per_unit': 8.50, 'minimum_level': 25, 'description': '50mm wood screws'},
    {'name': 'Screws Wood 75mm', 'unit': 'boxes', 'category': 'Hardware', 'cost_per_unit': 12.25, 'minimum_level': 20, 'description': '75mm wood screws'},
    {'name': 'Bolts M8', 'unit': 'pieces', 'category': 'Hardware', 'cost_per_unit': 1.25, 'minimum_level': 100, 'description': 'M8 bolts'},
    {'name': 'Bolts M10', 'unit': 'pieces', 'category': 'Hardware', 'cost_per_unit': 1.75, 'minimum_level': 75, 'description': 'M10 bolts'},
    {'name': 'Bolts M12', 'unit': 'pieces', 'category': 'Hardware', 'cost_per_unit': 2.25, 'minimum_level': 50, 'description': 'M12 bolts'},
    {'name': 'Washers', 'unit': 'pieces', 'category': 'Hardware', 'cost_per_unit': 0.15, 'minimum_level': 500, 'description': 'Metal washers'},
    {'name': 'Nuts', 'unit': 'pieces', 'category': 'Hardware', 'cost_per_unit': 0.25, 'minimum_level': 400, 'description': 'Metal nuts'},
    
    # GARDENING
    {'name': 'Grass Seed', 'unit': 'kg', 'category': 'Gardening', 'cost_per_unit': 25.00, 'minimum_level': 20, 'description': 'Lawn grass seed'},
    {'name': 'Fertilizer', 'unit': 'bags', 'category': 'Gardening', 'cost_per_unit': 18.50, 'minimum_level': 25, 'description': 'General purpose fertilizer'},
    {'name': 'Compost', 'unit': 'bags', 'category': 'Gardening', 'cost_per_unit': 15.00, 'minimum_level': 30, 'description': 'Organic compost'},
    {'name': 'Topsoil', 'unit': 'bags', 'category': 'Gardening', 'cost_per_unit': 12.50, 'minimum_level': 40, 'description': 'Quality topsoil'},
    
    # SAFETY
    {'name': 'Safety Helmets', 'unit': 'pieces', 'category': 'Safety', 'cost_per_unit': 15.00, 'minimum_level': 50, 'description': 'Construction safety helmets'},
    {'name': 'Safety Gloves', 'unit': 'pairs', 'category': 'Safety', 'cost_per_unit': 5.25, 'minimum_level': 100, 'description': 'Work gloves'},
    {'name': 'Safety Boots', 'unit': 'pairs', 'category': 'Safety', 'cost_per_unit': 45.00, 'minimum_level': 25, 'description': 'Steel toe safety boots'},
    {'name': 'Safety Vests', 'unit': 'pieces', 'category': 'Safety', 'cost_per_unit': 8.50, 'minimum_level': 75, 'description': 'High visibility vests'},
    {'name': 'Safety Glasses', 'unit': 'pieces', 'category': 'Safety', 'cost_per_unit': 6.25, 'minimum_level': 50, 'description': 'Safety glasses'},
    
    # INSULATION
    {'name': 'Insulation Boards', 'unit': 'sheets', 'category': 'Insulation', 'cost_per_unit': 22.50, 'minimum_level': 40, 'description': 'Insulation boards'},
    {'name': 'Insulation Rolls', 'unit': 'rolls', 'category': 'Insulation', 'cost_per_unit': 35.00, 'minimum_level': 20, 'description': 'Insulation rolls'},
    {'name': 'Vapor Barrier', 'unit': 'square meters', 'category': 'Insulation', 'cost_per_unit': 2.75, 'minimum_level': 200, 'description': 'Vapor barrier material'},
]

def import_materials():
    """Import all materials into the database"""
    with app.app_context():
        added_count = 0
        updated_count = 0
        error_count = 0
        
        for material_data in materials_data:
            try:
                # Check if material already exists
                existing_material = Material.query.filter_by(name=material_data['name']).first()
                
                if existing_material:
                    # Update existing material
                    existing_material.unit = material_data['unit']
                    existing_material.category = material_data['category']
                    existing_material.cost_per_unit = material_data['cost_per_unit']
                    existing_material.minimum_level = material_data['minimum_level']
                    existing_material.description = material_data['description']
                    updated_count += 1
                else:
                    # Create new material
                    new_material = Material(
                        name=material_data['name'],
                        unit=material_data['unit'],
                        category=material_data['category'],
                        cost_per_unit=material_data['cost_per_unit'],
                        minimum_level=material_data['minimum_level'],
                        description=material_data['description']
                    )
                    db.session.add(new_material)
                    added_count += 1
                    
            except Exception as e:
                print(f"Error processing {material_data['name']}: {str(e)}")
                error_count += 1
                continue
        
        try:
            db.session.commit()
            print(f"Import completed! Added: {added_count}, Updated: {updated_count}, Errors: {error_count}")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to database: {str(e)}")

if __name__ == '__main__':
    import_materials()