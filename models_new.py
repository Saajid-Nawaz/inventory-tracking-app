from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
import uuid


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'storesman' or 'site_engineer'
    assigned_site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_site = db.relationship('Site', backref='assigned_users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Site(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_levels = db.relationship('StockLevel', backref='site', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='site', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Site {self.name}>'


class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)
    minimum_level = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_levels = db.relationship('StockLevel', backref='material', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='material', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Material {self.name}>'


class StockLevel(db.Model):
    __tablename__ = 'stock_levels'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    total_value = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (UniqueConstraint('site_id', 'material_id', name='uq_site_material'),)

    @property
    def average_cost(self):
        return self.total_value / self.quantity if self.quantity > 0 else 0.0

    @property
    def is_below_minimum(self):
        return self.quantity < self.material.minimum_level

    def __repr__(self):
        return f'<StockLevel {self.site.name} - {self.material.name}: {self.quantity}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(20), unique=True, nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'receive', 'issue', 'adjustment'
    issued_to_project_code = db.Column(db.String(50), nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    supporting_document_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_transactions')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_transactions')

    @staticmethod
    def generate_serial_number():
        """Generate a unique serial number for the transaction"""
        timestamp = datetime.now().strftime("%Y%m%d")
        counter = Transaction.query.filter(Transaction.serial_number.like(f"TXN-{timestamp}-%")).count() + 1
        return f"TXN-{timestamp}-{counter:04d}"

    def __repr__(self):
        return f'<Transaction {self.serial_number} - {self.type}>'


class IssueRequest(db.Model):
    __tablename__ = 'issue_requests'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    project_code = db.Column(db.String(50), nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    site = db.relationship('Site', backref='issue_requests')
    material = db.relationship('Material', backref='issue_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='requested_issues')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_issues')

    def __repr__(self):
        return f'<IssueRequest {self.material.name} - {self.quantity_requested}>'


class BatchIssueRequest(db.Model):
    __tablename__ = 'batch_issue_requests'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), unique=True, nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    project_code = db.Column(db.String(50), nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    site = db.relationship('Site', backref='batch_issue_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='requested_batch_issues')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_batch_issues')
    items = db.relationship('BatchIssueItem', backref='batch_request', cascade='all, delete-orphan')

    @staticmethod
    def generate_batch_id():
        """Generate a unique batch ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        counter = BatchIssueRequest.query.filter(BatchIssueRequest.batch_id.like(f"BTH-{timestamp}-%")).count() + 1
        return f"BTH-{timestamp}-{counter:04d}"

    def __repr__(self):
        return f'<BatchIssueRequest {self.batch_id}>'


class BatchIssueItem(db.Model):
    __tablename__ = 'batch_issue_items'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), db.ForeignKey('batch_issue_requests.batch_id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    
    # Relationships
    material = db.relationship('Material', backref='batch_issue_items')

    def __repr__(self):
        return f'<BatchIssueItem {self.batch_id} - {self.material.name}>'


class StockAdjustment(db.Model):
    __tablename__ = 'stock_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    expected_quantity = db.Column(db.Float, nullable=False)
    actual_quantity = db.Column(db.Float, nullable=False)
    discrepancy = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    adjusted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    adjusted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    site = db.relationship('Site', backref='stock_adjustments')
    material = db.relationship('Material', backref='stock_adjustments')
    adjuster = db.relationship('User', backref='stock_adjustments')

    def __repr__(self):
        return f'<StockAdjustment {self.site.name} - {self.material.name}: {self.discrepancy}>'


class FIFOBatch(db.Model):
    """Track FIFO batches for inventory valuation"""
    __tablename__ = 'fifo_batches'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity_remaining = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    
    # Relationships
    site = db.relationship('Site')
    material = db.relationship('Material')
    transaction = db.relationship('Transaction')

    def __repr__(self):
        return f'<FIFOBatch {self.material.name} - {self.quantity_remaining} @ {self.unit_cost}>'


# Legacy models for backward compatibility - with unique table names
class LegacyMaterialRecord(db.Model):
    __tablename__ = 'legacy_material_record'
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    recorded_by = db.Column(db.String(80), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f'<LegacyMaterialRecord {self.material_name}>'


class LegacyIssuanceRequest(db.Model):
    __tablename__ = 'legacy_issuance_request'
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    requested_by = db.Column(db.String(80), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.String(80), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<LegacyIssuanceRequest {self.material_name}>'


class LegacyBatchIssuance(db.Model):
    __tablename__ = 'legacy_batch_issuance'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), unique=True, nullable=False)
    issued_to = db.Column(db.String(200), nullable=False)
    truck_number = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(100), nullable=True)
    driver_contact = db.Column(db.String(20), nullable=True)
    gtv_image = db.Column(db.String(200), nullable=True)
    requested_by = db.Column(db.String(80), nullable=False)
    approved_by = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(20), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    issued_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<LegacyBatchIssuance {self.batch_id}>'


class LegacyBatchIssuanceItem(db.Model):
    __tablename__ = 'legacy_batch_issuance_item'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), db.ForeignKey('legacy_batch_issuance.batch_id'), nullable=False)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<LegacyBatchIssuanceItem {self.batch_id} - {self.material_name}>'


class LegacyIssuanceLog(db.Model):
    __tablename__ = 'legacy_issuance_log'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('legacy_issuance_request.id'), nullable=True)
    batch_id = db.Column(db.String(20), db.ForeignKey('legacy_batch_issuance.batch_id'), nullable=True)
    material_name = db.Column(db.String(200), nullable=False)
    quantity_issued = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    issued_by = db.Column(db.String(80), nullable=False)
    authorized_by = db.Column(db.String(80), nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<LegacyIssuanceLog {self.material_name}>'