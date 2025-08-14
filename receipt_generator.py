from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
import os

class ReceiptGenerator:
    """Generate professional goods received vouchers for material transactions"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the receipt"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        self.right_align_style = ParagraphStyle(
            'RightAlign',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def generate_receipt(self, transaction_data, site_data, user_data, company_settings=None):
        """Generate a goods received voucher PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the document content
        story = []
        
        # Company Header
        company_name = company_settings.get('company_name', 'Construction Company') if company_settings else 'Construction Company'
        currency = company_settings.get('currency', 'ZMW') if company_settings else 'ZMW'
        
        story.append(Paragraph(company_name, self.title_style))
        story.append(Paragraph("GOODS RECEIVED VOUCHER", self.header_style))
        story.append(Spacer(1, 20))
        
        # Receipt Header Information
        header_data = [
            ['Receipt No:', transaction_data['serial_number'], 'Date:', transaction_data['date'].strftime('%d/%m/%Y')],
            ['Site:', site_data['name'], 'Location:', site_data.get('location', 'N/A')],
            ['Received By:', user_data['username'], 'Role:', user_data['role'].title()]
        ]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 30))
        
        # Material Details Section
        story.append(Paragraph("MATERIAL DETAILS", self.header_style))
        
        material_data = [
            ['Material Name', 'SKU', 'Unit', 'Quantity', 'Unit Cost', 'Total Value'],
            [
                transaction_data['material_name'],
                transaction_data.get('material_sku', 'N/A'),
                transaction_data['material_unit'],
                f"{transaction_data['quantity']:,.2f}",
                f"{currency} {transaction_data['unit_cost']:,.2f}",
                f"{currency} {transaction_data['total_value']:,.2f}"
            ]
        ]
        
        material_table = Table(material_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch, 1.5*inch])
        material_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(material_table)
        story.append(Spacer(1, 30))
        
        # Supplier Information (if available)
        if transaction_data.get('supplier_info'):
            story.append(Paragraph("SUPPLIER INFORMATION", self.header_style))
            supplier_data = [
                ['Supplier Name:', transaction_data['supplier_info'].get('name', 'N/A')],
                ['Contact:', transaction_data['supplier_info'].get('contact', 'N/A')],
                ['Reference:', transaction_data['supplier_info'].get('reference', 'N/A')]
            ]
            
            supplier_table = Table(supplier_data, colWidths=[2*inch, 4.5*inch])
            supplier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(supplier_table)
            story.append(Spacer(1, 30))
        
        # Notes Section
        if transaction_data.get('notes'):
            story.append(Paragraph("ADDITIONAL NOTES", self.header_style))
            story.append(Paragraph(transaction_data['notes'], self.normal_style))
            story.append(Spacer(1, 30))
        
        # Signature Section
        story.append(Spacer(1, 40))
        signature_data = [
            ['Received By:', '', 'Authorized By:', ''],
            ['', '', '', ''],
            ['Name: ' + user_data['username'], '', 'Name: ________________', ''],
            ['Signature: ________________', '', 'Signature: ________________', ''],
            ['Date: ' + datetime.now().strftime('%d/%m/%Y'), '', 'Date: ________________', '']
        ]
        
        signature_table = Table(signature_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 3), (1, 3), 1, colors.HexColor('#2c3e50')),
            ('LINEBELOW', (2, 3), (3, 3), 1, colors.HexColor('#2c3e50'))
        ]))
        
        story.append(signature_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')} | Receipt ID: {transaction_data['serial_number']}"
        story.append(Paragraph(footer_text, self.right_align_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def extract_transaction_data(self, transaction):
        """Extract and format transaction data for receipt generation"""
        return {
            'serial_number': transaction.serial_number,
            'date': transaction.created_at,
            'material_name': transaction.material.name,
            'material_sku': transaction.material.sku,
            'material_unit': transaction.material.unit,
            'quantity': transaction.quantity,
            'unit_cost': transaction.unit_cost,
            'total_value': transaction.total_value,
            'notes': transaction.notes,
            'supplier_info': self._extract_supplier_info(transaction)
        }
    
    def _extract_supplier_info(self, transaction):
        """Extract supplier information from transaction notes or supporting documents"""
        # This could be enhanced to parse supplier info from notes or linked documents
        supplier_info = {}
        
        if transaction.notes:
            # Try to extract supplier info from notes using common patterns
            notes_lower = transaction.notes.lower()
            if 'supplier:' in notes_lower:
                # Extract supplier name after "supplier:" keyword
                start = notes_lower.find('supplier:') + 9
                end = notes_lower.find('\n', start) if '\n' in notes_lower[start:] else len(notes_lower)
                supplier_info['name'] = transaction.notes[start:end].strip()
            
            if 'contact:' in notes_lower:
                start = notes_lower.find('contact:') + 8
                end = notes_lower.find('\n', start) if '\n' in notes_lower[start:] else len(notes_lower)
                supplier_info['contact'] = transaction.notes[start:end].strip()
            
            if 'ref:' in notes_lower or 'reference:' in notes_lower:
                keyword = 'reference:' if 'reference:' in notes_lower else 'ref:'
                start = notes_lower.find(keyword) + len(keyword)
                end = notes_lower.find('\n', start) if '\n' in notes_lower[start:] else len(notes_lower)
                supplier_info['reference'] = transaction.notes[start:end].strip()
        
        return supplier_info if supplier_info else None