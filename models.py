from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'site_engineer' or 'storesperson'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class MaterialRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    recorded_by = db.Column(db.String(80), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'issued'
    
    def __repr__(self):
        return f'<MaterialRecord {self.material_name}: {self.quantity} {self.unit}>'

class IssuanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    requested_by = db.Column(db.String(80), nullable=False)  # storesperson
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'denied'
    reviewed_by = db.Column(db.String(80), nullable=True)  # site engineer
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<IssuanceRequest {self.material_name}: {self.quantity_requested} {self.unit}>'

class BatchIssuance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), unique=True, nullable=False)  # Unique serial ID
    issued_to = db.Column(db.String(200), nullable=False)  # Who materials are issued to
    truck_number = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(100), nullable=True)
    driver_contact = db.Column(db.String(20), nullable=True)
    gtv_image = db.Column(db.String(200), nullable=True)  # GTV image filename
    requested_by = db.Column(db.String(80), nullable=False)  # storesperson
    approved_by = db.Column(db.String(80), nullable=True)  # site engineer
    status = db.Column(db.String(20), default='pending')  # pending, approved, denied, issued
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    issued_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<BatchIssuance {self.batch_id}: {self.issued_to}>'

class BatchIssuanceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), db.ForeignKey('batch_issuance.batch_id'), nullable=False)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<BatchIssuanceItem {self.material_name}: {self.quantity_requested} {self.unit}>'

class IssuanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('issuance_request.id'), nullable=True)
    batch_id = db.Column(db.String(20), db.ForeignKey('batch_issuance.batch_id'), nullable=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_issued = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    issued_by = db.Column(db.String(80), nullable=False)
    authorized_by = db.Column(db.String(80), nullable=True)  # site engineer who approved
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<IssuanceLog {self.material_name}: {self.quantity_issued} {self.unit}>'
