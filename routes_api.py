"""
API Routes for external access to inventory system
Provides simple REST API endpoints while maintaining full system functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import MaterialRecord as Material, Site, StockLevel, User
import logging

api_bp = Blueprint("api", __name__, url_prefix="/api")

def check_api_access():
    """Check if current user has API access permissions"""
    if not current_user.is_authenticated:
        return False, {"error": "Authentication required"}, 401
    
    if current_user.role not in ['site_engineer', 'storesman']:
        return False, {"error": "Access denied"}, 403
    
    return True, None, None

@api_bp.route("/health", methods=["GET"])
def health():
    """API health check endpoint"""
    return {"status": "ok", "service": "Construction Material Tracker API"}

@api_bp.route("/materials", methods=["GET"])
@login_required
def get_materials():
    """Get all materials with current stock levels"""
    access_ok, error_response, status_code = check_api_access()
    if not access_ok:
        return error_response, status_code
    
    try:
        # For storesmen, only show materials from their assigned site
        if current_user.role == 'storesman' and current_user.assigned_site_id:
            stock_levels = StockLevel.query.filter_by(site_id=current_user.assigned_site_id).all()
            materials_data = []
            
            for stock in stock_levels:
                materials_data.append({
                    "id": stock.material.id,
                    "name": stock.material.name,
                    "quantity": float(stock.quantity),
                    "unit": stock.material.unit,
                    "category": stock.material.category,
                    "minimum_level": float(stock.material.minimum_level),
                    "site_id": stock.site_id,
                    "site_name": stock.site.name if stock.site else None
                })
        else:
            # Site engineers can see all materials
            materials = Material.query.all()
            materials_data = []
            
            for material in materials:
                # Get total stock across all sites
                total_stock = sum([float(sl.quantity) for sl in material.stock_levels])
                materials_data.append({
                    "id": material.id,
                    "name": material.name,
                    "total_quantity": total_stock,
                    "unit": material.unit,
                    "category": material.category,
                    "minimum_level": float(material.minimum_level),
                    "cost_per_unit": float(material.cost_per_unit) if material.cost_per_unit else None
                })
        
        return {"materials": materials_data, "count": len(materials_data)}
        
    except Exception as e:
        logging.error(f"Error getting materials: {str(e)}")
        return {"error": "Failed to retrieve materials"}, 500

@api_bp.route("/materials/<int:material_id>", methods=["GET"])
@login_required
def get_material_details(material_id):
    """Get detailed information about a specific material"""
    access_ok, error_response, status_code = check_api_access()
    if not access_ok:
        return error_response, status_code
    
    try:
        material = Material.query.get_or_404(material_id)
        
        # Get stock levels by site
        stock_by_site = []
        for stock_level in material.stock_levels:
            # For storesmen, only show their assigned site
            if current_user.role == 'storesman' and current_user.assigned_site_id:
                if stock_level.site_id != current_user.assigned_site_id:
                    continue
            
            stock_by_site.append({
                "site_id": stock_level.site_id,
                "site_name": stock_level.site.name,
                "quantity": float(stock_level.quantity),
                "last_updated": stock_level.last_updated.isoformat() if stock_level.last_updated else None
            })
        
        material_data = {
            "id": material.id,
            "name": material.name,
            "unit": material.unit,
            "category": material.category,
            "minimum_level": float(material.minimum_level),
            "stock_by_site": stock_by_site,
            "total_quantity": sum([float(sl.quantity) for sl in material.stock_levels])
        }
        
        # Only include cost for site engineers
        if current_user.role == 'site_engineer':
            material_data["cost_per_unit"] = float(material.cost_per_unit) if material.cost_per_unit else None
        
        return material_data
        
    except Exception as e:
        logging.error(f"Error getting material details: {str(e)}")
        return {"error": "Failed to retrieve material details"}, 500

@api_bp.route("/low-stock", methods=["GET"])
@login_required
def low_stock():
    """Get materials with stock levels below minimum threshold"""
    access_ok, error_response, status_code = check_api_access()
    if not access_ok:
        return error_response, status_code
    
    try:
        low_stock_items = []
        
        if current_user.role == 'storesman' and current_user.assigned_site_id:
            # For storesmen, only check their assigned site
            stock_levels = StockLevel.query.filter_by(site_id=current_user.assigned_site_id).all()
            
            for stock in stock_levels:
                if stock.quantity <= stock.material.minimum_level:
                    low_stock_items.append({
                        "material_id": stock.material.id,
                        "name": stock.material.name,
                        "current_quantity": float(stock.quantity),
                        "minimum_level": float(stock.material.minimum_level),
                        "unit": stock.material.unit,
                        "site_id": stock.site_id,
                        "site_name": stock.site.name
                    })
        else:
            # For site engineers, check all sites
            materials = Material.query.all()
            
            for material in materials:
                for stock_level in material.stock_levels:
                    if stock_level.quantity <= material.minimum_level:
                        low_stock_items.append({
                            "material_id": material.id,
                            "name": material.name,
                            "current_quantity": float(stock_level.quantity),
                            "minimum_level": float(material.minimum_level),
                            "unit": material.unit,
                            "site_id": stock_level.site_id,
                            "site_name": stock_level.site.name if stock_level.site else None
                        })
        
        return {"low_stock_items": low_stock_items, "count": len(low_stock_items)}
        
    except Exception as e:
        logging.error(f"Error getting low stock items: {str(e)}")
        return {"error": "Failed to retrieve low stock items"}, 500

@api_bp.route("/sites", methods=["GET"])
@login_required
def get_sites():
    """Get list of sites based on user permissions"""
    access_ok, error_response, status_code = check_api_access()
    if not access_ok:
        return error_response, status_code
    
    try:
        if current_user.role == 'storesman' and current_user.assigned_site_id:
            # Storesmen can only see their assigned site
            site = Site.query.get(current_user.assigned_site_id)
            if site:
                sites_data = [{
                    "id": site.id,
                    "name": site.name,
                    "code": site.code,
                    "location": site.location
                }]
            else:
                sites_data = []
        else:
            # Site engineers can see all active sites
            sites = Site.query.filter_by(is_active=True).all()
            sites_data = [{
                "id": site.id,
                "name": site.name,
                "code": site.code,
                "location": site.location
            } for site in sites]
        
        return {"sites": sites_data, "count": len(sites_data)}
        
    except Exception as e:
        logging.error(f"Error getting sites: {str(e)}")
        return {"error": "Failed to retrieve sites"}, 500

@api_bp.route("/materials/search", methods=["GET"])
@login_required
def search_materials():
    """Search materials by name or category"""
    access_ok, error_response, status_code = check_api_access()
    if not access_ok:
        return error_response, status_code
    
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        
        if not query and not category:
            return {"error": "Query parameter 'q' or 'category' required"}, 400
        
        materials_query = Material.query
        
        if query:
            materials_query = materials_query.filter(Material.name.ilike(f'%{query}%'))
        
        if category:
            materials_query = materials_query.filter_by(category=category)
        
        materials = materials_query.all()
        
        materials_data = []
        for material in materials:
            # Get stock levels based on user permissions
            if current_user.role == 'storesman' and current_user.assigned_site_id:
                stock_levels = [sl for sl in material.stock_levels if sl.site_id == current_user.assigned_site_id]
                total_stock = sum([float(sl.quantity) for sl in stock_levels])
            else:
                total_stock = sum([float(sl.quantity) for sl in material.stock_levels])
            
            material_data = {
                "id": material.id,
                "name": material.name,
                "quantity": total_stock,
                "unit": material.unit,
                "category": material.category,
                "minimum_level": float(material.minimum_level)
            }
            
            # Only include cost for site engineers
            if current_user.role == 'site_engineer':
                material_data["cost_per_unit"] = float(material.cost_per_unit) if material.cost_per_unit else None
            
            materials_data.append(material_data)
        
        return {"materials": materials_data, "count": len(materials_data), "search_query": query, "category": category}
        
    except Exception as e:
        logging.error(f"Error searching materials: {str(e)}")
        return {"error": "Failed to search materials"}, 500