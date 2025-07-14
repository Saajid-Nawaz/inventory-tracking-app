"""
Inventory Management Service
Handles FIFO valuation, stock operations, and transaction processing
"""

from datetime import datetime
from app import db
from models_new import (
    Site, Material, StockLevel, Transaction, FIFOBatch, 
    IssueRequest, BatchIssueRequest, BatchIssueItem, StockAdjustment
)
from sqlalchemy import func
import logging


class InventoryService:
    """Service class for managing inventory operations with FIFO valuation"""
    
    @staticmethod
    def receive_material(site_id, material_id, quantity, unit_cost, project_code=None, created_by=None, notes=None):
        """
        Receive material into inventory using FIFO method
        """
        try:
            # Generate transaction serial number
            serial_number = Transaction.generate_serial_number()
            
            # Calculate total value
            total_value = quantity * unit_cost
            
            # Create transaction record
            transaction = Transaction(
                serial_number=serial_number,
                site_id=site_id,
                material_id=material_id,
                quantity=quantity,
                unit_cost=unit_cost,
                total_value=total_value,
                type='receive',
                issued_to_project_code=project_code,
                created_by=created_by,
                notes=notes
            )
            db.session.add(transaction)
            db.session.flush()  # Get the transaction ID
            
            # Create FIFO batch
            fifo_batch = FIFOBatch(
                site_id=site_id,
                material_id=material_id,
                quantity_remaining=quantity,
                unit_cost=unit_cost,
                transaction_id=transaction.id
            )
            db.session.add(fifo_batch)
            
            # Update stock levels
            InventoryService._update_stock_level(site_id, material_id, quantity, total_value)
            
            db.session.commit()
            
            logging.info(f"Material received: {serial_number} - {quantity} units at {unit_cost} each")
            return transaction
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error receiving material: {str(e)}")
            raise
    
    @staticmethod
    def issue_material(site_id, material_id, quantity, project_code=None, approved_by=None, created_by=None, notes=None):
        """
        Issue material from inventory using FIFO method
        """
        try:
            # Check if sufficient stock is available
            stock_level = StockLevel.query.filter_by(site_id=site_id, material_id=material_id).first()
            if not stock_level or stock_level.quantity < quantity:
                raise ValueError("Insufficient stock available")
            
            # Get FIFO batches to consume
            fifo_batches = FIFOBatch.query.filter_by(
                site_id=site_id, 
                material_id=material_id
            ).filter(FIFOBatch.quantity_remaining > 0).order_by(FIFOBatch.received_at).all()
            
            if not fifo_batches:
                raise ValueError("No FIFO batches available")
            
            # Calculate weighted average cost for the issue
            total_cost = 0
            remaining_quantity = quantity
            
            for batch in fifo_batches:
                if remaining_quantity <= 0:
                    break
                    
                quantity_to_consume = min(remaining_quantity, batch.quantity_remaining)
                batch_cost = quantity_to_consume * batch.unit_cost
                total_cost += batch_cost
                
                # Update batch remaining quantity
                batch.quantity_remaining -= quantity_to_consume
                remaining_quantity -= quantity_to_consume
            
            if remaining_quantity > 0:
                raise ValueError("Insufficient FIFO batches to fulfill request")
            
            # Generate transaction serial number
            serial_number = Transaction.generate_serial_number()
            
            # Create transaction record
            transaction = Transaction(
                serial_number=serial_number,
                site_id=site_id,
                material_id=material_id,
                quantity=-quantity,  # Negative for issue
                unit_cost=total_cost / quantity,  # Weighted average cost
                total_value=-total_cost,  # Negative for issue
                type='issue',
                issued_to_project_code=project_code,
                approved_by=approved_by,
                created_by=created_by,
                notes=notes
            )
            db.session.add(transaction)
            
            # Update stock levels
            InventoryService._update_stock_level(site_id, material_id, -quantity, -total_cost)
            
            db.session.commit()
            
            logging.info(f"Material issued: {serial_number} - {quantity} units at avg cost {total_cost / quantity}")
            return transaction
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error issuing material: {str(e)}")
            raise
    
    @staticmethod
    def adjust_stock(site_id, material_id, expected_quantity, actual_quantity, reason=None, adjusted_by=None):
        """
        Adjust stock levels due to physical count discrepancies
        """
        try:
            discrepancy = actual_quantity - expected_quantity
            
            # Create stock adjustment record
            adjustment = StockAdjustment(
                site_id=site_id,
                material_id=material_id,
                expected_quantity=expected_quantity,
                actual_quantity=actual_quantity,
                discrepancy=discrepancy,
                reason=reason,
                adjusted_by=adjusted_by
            )
            db.session.add(adjustment)
            
            if discrepancy != 0:
                # Get current stock level
                stock_level = StockLevel.query.filter_by(site_id=site_id, material_id=material_id).first()
                if not stock_level:
                    # Create new stock level if it doesn't exist
                    stock_level = StockLevel(
                        site_id=site_id,
                        material_id=material_id,
                        quantity=0,
                        total_value=0
                    )
                    db.session.add(stock_level)
                
                # Calculate adjustment value using average cost
                avg_cost = stock_level.average_cost if stock_level.quantity > 0 else 0
                adjustment_value = discrepancy * avg_cost
                
                # Generate transaction serial number
                serial_number = Transaction.generate_serial_number()
                
                # Create adjustment transaction
                transaction = Transaction(
                    serial_number=serial_number,
                    site_id=site_id,
                    material_id=material_id,
                    quantity=discrepancy,
                    unit_cost=avg_cost,
                    total_value=adjustment_value,
                    type='adjustment',
                    created_by=adjusted_by,
                    notes=f"Stock adjustment: {reason}" if reason else "Stock adjustment"
                )
                db.session.add(transaction)
                
                # Update stock levels
                InventoryService._update_stock_level(site_id, material_id, discrepancy, adjustment_value)
                
                # If positive adjustment, create FIFO batch
                if discrepancy > 0:
                    db.session.flush()  # Get transaction ID
                    fifo_batch = FIFOBatch(
                        site_id=site_id,
                        material_id=material_id,
                        quantity_remaining=discrepancy,
                        unit_cost=avg_cost,
                        transaction_id=transaction.id
                    )
                    db.session.add(fifo_batch)
            
            db.session.commit()
            
            logging.info(f"Stock adjusted: Site {site_id}, Material {material_id}, Discrepancy: {discrepancy}")
            return adjustment
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adjusting stock: {str(e)}")
            raise
    
    @staticmethod
    def _update_stock_level(site_id, material_id, quantity_change, value_change):
        """
        Update stock level quantities and values
        """
        stock_level = StockLevel.query.filter_by(site_id=site_id, material_id=material_id).first()
        
        if not stock_level:
            stock_level = StockLevel(
                site_id=site_id,
                material_id=material_id,
                quantity=0,
                total_value=0
            )
            db.session.add(stock_level)
        
        stock_level.quantity += quantity_change
        stock_level.total_value += value_change
        stock_level.updated_at = datetime.utcnow()
        
        # Ensure quantity and value don't go negative
        if stock_level.quantity < 0:
            stock_level.quantity = 0
        if stock_level.total_value < 0:
            stock_level.total_value = 0
    
    @staticmethod
    def get_stock_summary(site_id=None):
        """
        Get stock summary for a site or all sites
        """
        query = db.session.query(
            StockLevel.site_id,
            Site.name.label('site_name'),
            StockLevel.material_id,
            Material.name.label('material_name'),
            Material.unit,
            StockLevel.quantity,
            StockLevel.total_value,
            Material.minimum_level,
            StockLevel.updated_at
        ).join(Site).join(Material)
        
        if site_id:
            query = query.filter(StockLevel.site_id == site_id)
        
        return query.order_by(Site.name, Material.name).all()
    
    @staticmethod
    def get_low_stock_items(site_id=None):
        """
        Get items that are below minimum stock level
        """
        query = db.session.query(
            StockLevel.site_id,
            Site.name.label('site_name'),
            StockLevel.material_id,
            Material.name.label('material_name'),
            Material.unit,
            StockLevel.quantity,
            Material.minimum_level
        ).join(Site).join(Material).filter(StockLevel.quantity < Material.minimum_level)
        
        if site_id:
            query = query.filter(StockLevel.site_id == site_id)
        
        return query.all()
    
    @staticmethod
    def get_transaction_history(site_id=None, material_id=None, start_date=None, end_date=None):
        """
        Get transaction history with optional filters
        """
        from models_new import Transaction, Site, Material, User
        
        try:
            # Start with basic query
            query = db.session.query(Transaction)
            
            # Add joins with left outer joins to handle missing relationships
            query = query.join(Site, Transaction.site_id == Site.id)
            query = query.join(Material, Transaction.material_id == Material.id)
            query = query.outerjoin(User, Transaction.created_by == User.id)
            
            # Apply filters
            if site_id:
                query = query.filter(Transaction.site_id == site_id)
            if material_id:
                query = query.filter(Transaction.material_id == material_id)
            if start_date:
                query = query.filter(Transaction.created_at >= start_date)
            if end_date:
                query = query.filter(Transaction.created_at <= end_date)
            
            transactions = query.order_by(Transaction.created_at.desc()).all()
            
            # Add computed fields for template compatibility
            for txn in transactions:
                txn.site_name = txn.site.name if txn.site else 'Unknown Site'
                txn.material_name = txn.material.name if txn.material else 'Unknown Material'
                txn.unit = txn.material.unit if txn.material else 'Unknown'
            
            logging.info(f"Retrieved {len(transactions)} transactions for site_id={site_id}")
            return transactions
            
        except Exception as e:
            logging.error(f"Error retrieving transaction history: {str(e)}")
            return []
    
    @staticmethod
    def process_issue_request(request_id, approved_by, action='approve', review_notes=None):
        """
        Process an issue request (approve or reject)
        """
        try:
            issue_request = IssueRequest.query.get(request_id)
            if not issue_request:
                raise ValueError("Issue request not found")
            
            if issue_request.status != 'pending':
                raise ValueError("Request already processed")
            
            issue_request.status = 'approved' if action == 'approve' else 'rejected'
            issue_request.reviewed_by = approved_by
            issue_request.reviewed_at = datetime.utcnow()
            issue_request.review_notes = review_notes
            
            # If approved, create the issue transaction
            if action == 'approve':
                transaction = InventoryService.issue_material(
                    site_id=issue_request.site_id,
                    material_id=issue_request.material_id,
                    quantity=issue_request.quantity_requested,
                    project_code=issue_request.project_code,
                    approved_by=approved_by,
                    created_by=issue_request.requested_by,
                    notes=f"Issue request approved: {review_notes}" if review_notes else "Issue request approved"
                )
            
            db.session.commit()
            
            logging.info(f"Issue request {action}d: {issue_request.id}")
            return issue_request
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error processing issue request: {str(e)}")
            raise
    
    @staticmethod
    def process_batch_issue_request(batch_id, approved_by, action='approve', review_notes=None):
        """
        Process a batch issue request (approve or reject)
        """
        try:
            batch_request = BatchIssueRequest.query.filter_by(batch_id=batch_id).first()
            if not batch_request:
                raise ValueError("Batch request not found")
            
            if batch_request.status != 'pending':
                raise ValueError("Batch request already processed")
            
            batch_request.status = 'approved' if action == 'approve' else 'rejected'
            batch_request.reviewed_by = approved_by
            batch_request.reviewed_at = datetime.utcnow()
            batch_request.review_notes = review_notes
            
            # If approved, create issue transactions for all items
            if action == 'approve':
                for item in batch_request.items:
                    transaction = InventoryService.issue_material(
                        site_id=batch_request.site_id,
                        material_id=item.material_id,
                        quantity=item.quantity_requested,
                        project_code=batch_request.project_code,
                        approved_by=approved_by,
                        created_by=batch_request.requested_by,
                        notes=f"Batch {batch_id} approved: {review_notes}" if review_notes else f"Batch {batch_id} approved"
                    )
            
            db.session.commit()
            
            logging.info(f"Batch request {action}d: {batch_id}")
            return batch_request
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error processing batch request: {str(e)}")
            raise
    
    @staticmethod
    def create_stock_transfer_request(from_site_id, to_site_id, materials, requested_by, reason=None, priority='normal'):
        """
        Create a new stock transfer request
        """
        try:
            from models_new import StockTransferRequest, StockTransferItem
            
            # Generate unique transfer ID
            transfer_id = StockTransferRequest.generate_transfer_id()
            
            # Create transfer request
            transfer_request = StockTransferRequest(
                transfer_id=transfer_id,
                from_site_id=from_site_id,
                to_site_id=to_site_id,
                requested_by=requested_by,
                reason=reason,
                priority=priority
            )
            db.session.add(transfer_request)
            db.session.flush()  # Get the ID
            
            # Add transfer items
            for material_data in materials:
                transfer_item = StockTransferItem(
                    transfer_id=transfer_id,
                    material_id=material_data['material_id'],
                    quantity_requested=material_data['quantity']
                )
                db.session.add(transfer_item)
            
            db.session.commit()
            
            logging.info(f"Stock transfer request created: {transfer_id}")
            return transfer_request
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating stock transfer request: {str(e)}")
            raise
    
    @staticmethod
    def process_stock_transfer_request(transfer_id, approved_by, action='approve', review_notes=None):
        """
        Process a stock transfer request (approve or reject)
        """
        try:
            from models_new import StockTransferRequest
            
            transfer_request = StockTransferRequest.query.filter_by(transfer_id=transfer_id).first()
            if not transfer_request:
                raise ValueError("Transfer request not found")
            
            if transfer_request.status != 'pending':
                raise ValueError("Transfer request already processed")
            
            transfer_request.status = 'approved' if action == 'approve' else 'rejected'
            transfer_request.reviewed_by = approved_by
            transfer_request.reviewed_at = datetime.utcnow()
            transfer_request.review_notes = review_notes
            
            # If approved, process the stock transfers
            if action == 'approve':
                for item in transfer_request.items:
                    # Issue from source site
                    InventoryService.issue_material(
                        site_id=transfer_request.from_site_id,
                        material_id=item.material_id,
                        quantity=item.quantity_requested,
                        project_code=f"TRANSFER-{transfer_id}",
                        approved_by=approved_by,
                        created_by=transfer_request.requested_by,
                        notes=f"Stock transfer to {transfer_request.to_site.name}"
                    )
                    
                    # Receive at destination site - using average cost from source
                    source_stock = StockLevel.query.filter_by(
                        site_id=transfer_request.from_site_id,
                        material_id=item.material_id
                    ).first()
                    
                    avg_cost = source_stock.average_cost if source_stock and source_stock.quantity > 0 else 0
                    
                    InventoryService.receive_material(
                        site_id=transfer_request.to_site_id,
                        material_id=item.material_id,
                        quantity=item.quantity_requested,
                        unit_cost=avg_cost,
                        project_code=f"TRANSFER-{transfer_id}",
                        created_by=approved_by,
                        notes=f"Stock transfer from {transfer_request.from_site.name}"
                    )
            
            db.session.commit()
            
            logging.info(f"Stock transfer request {action}d: {transfer_id}")
            return transfer_request
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error processing stock transfer request: {str(e)}")
            raise


class ReportService:
    """Service class for generating reports"""
    
    @staticmethod
    def generate_daily_issues_report(site_id, report_date):
        """
        Generate daily issues report for a specific site
        """
        start_date = datetime.combine(report_date, datetime.min.time())
        end_date = datetime.combine(report_date, datetime.max.time())
        
        issues = db.session.query(
            Transaction.serial_number,
            Transaction.created_at,
            Material.name.label('material_name'),
            Material.unit,
            Transaction.quantity,
            Transaction.unit_cost,
            Transaction.total_value,
            Transaction.issued_to_project_code,
            Transaction.notes
        ).join(Material).filter(
            Transaction.site_id == site_id,
            Transaction.type == 'issue',
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        ).order_by(Transaction.created_at).all()
        
        return issues
    
    @staticmethod
    def generate_stock_summary_report(site_id):
        """
        Generate stock summary report for a specific site
        """
        return InventoryService.get_stock_summary(site_id)
    
    @staticmethod
    def generate_transaction_history_report(site_id, start_date=None, end_date=None):
        """
        Generate transaction history report
        """
        return InventoryService.get_transaction_history(site_id, start_date=start_date, end_date=end_date)