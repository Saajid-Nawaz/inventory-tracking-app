"""
Enhanced Professional Report Generator with Company Branding
Uses the same styling as receipts for consistency
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import pandas as pd
from io import BytesIO
import logging

class ProfessionalReportGenerator:
    """Enhanced report generator with professional styling and company branding"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for professional reports"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        self.company_style = ParagraphStyle(
            'CompanyTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_CENTER,
            spaceAfter=20,
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
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def format_currency(self, amount, currency='ZMW'):
        """Format currency based on type"""
        if currency == 'ZMW':
            return f"K{amount:,.2f}"
        elif currency == 'USD':
            return f"${amount:,.2f}"
        elif currency == 'EUR':
            return f"€{amount:,.2f}"
        elif currency == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"
    
    def add_company_header(self, story, company_name, report_title):
        """Add professional company header to report"""
        story.append(Paragraph(company_name, self.company_style))
        story.append(Paragraph(report_title, self.title_style))
        story.append(Spacer(1, 20))
    
    def add_report_info_section(self, story, info_data):
        """Add report information section with professional styling"""
        info_table_data = []
        for key, value in info_data.items():
            info_table_data.append([key + ':', str(value)])
        
        info_table = Table(info_table_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
    
    def create_professional_table(self, data, headers, currency='ZMW'):
        """Create professional styled table"""
        if not data:
            return None
        
        table_data = [headers]
        table_data.extend(data)
        
        # Calculate column widths based on content
        num_cols = len(headers)
        col_width = (7.5 * inch) / num_cols
        col_widths = [col_width] * num_cols
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        return table
    
    def add_footer(self, story, report_type, generation_time=None):
        """Add professional footer to report"""
        if generation_time is None:
            generation_time = datetime.now()
        
        footer_text = f"Generated on {generation_time.strftime('%d/%m/%Y at %H:%M')} | {report_type} Report"
        story.append(Spacer(1, 30))
        story.append(Paragraph(footer_text, self.right_align_style))
    
    def generate_daily_issues_report(self, company_name, site_name, report_date, issues_data, currency='ZMW'):
        """Generate professional daily issues report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Company header
        self.add_company_header(story, company_name, "DAILY MATERIAL ISSUES REPORT")
        
        # Report information
        info_data = {
            'Site': site_name,
            'Report Date': report_date.strftime('%d/%m/%Y'),
            'Generated By': 'Inventory Management System',
            'Total Transactions': len(issues_data) if issues_data else 0
        }
        self.add_report_info_section(story, info_data)
        
        if issues_data:
            # Transactions table
            story.append(Paragraph("MATERIAL ISSUES DETAILS", self.header_style))
            
            headers = ['Serial Number', 'Time', 'Material', 'Quantity', 'Unit Cost', 'Total Value', 'Project Code']
            table_data = []
            total_value = 0
            
            for issue in issues_data:
                table_data.append([
                    issue.serial_number,
                    issue.created_at.strftime('%H:%M'),
                    issue.material_name,
                    f"{abs(issue.quantity)} {issue.unit}",
                    self.format_currency(issue.unit_cost, currency),
                    self.format_currency(abs(issue.total_value), currency),
                    issue.issued_to_project_code or 'N/A'
                ])
                total_value += abs(issue.total_value)
            
            # Add total row
            table_data.append(['', '', '', '', 'TOTAL:', self.format_currency(total_value, currency), ''])
            
            table = self.create_professional_table(table_data, headers, currency)
            if table:
                story.append(table)
                
            # Summary section
            story.append(Spacer(1, 30))
            story.append(Paragraph("SUMMARY", self.header_style))
            
            summary_data = {
                'Total Issues': len(issues_data),
                'Total Value': self.format_currency(total_value, currency),
                'Average Value per Issue': self.format_currency(total_value / len(issues_data) if issues_data else 0, currency)
            }
            self.add_report_info_section(story, summary_data)
            
        else:
            story.append(Paragraph("No material issues recorded for this date.", self.normal_style))
        
        # Footer
        self.add_footer(story, "Daily Issues")
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_stock_summary_report(self, company_name, site_name, stock_data, currency='ZMW'):
        """Generate professional stock summary report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Company header
        self.add_company_header(story, company_name, "STOCK SUMMARY REPORT")
        
        # Report information
        total_items = len(stock_data) if stock_data else 0
        total_value = sum(item.total_value for item in stock_data) if stock_data else 0
        low_stock_items = sum(1 for item in stock_data if item.quantity < item.minimum_level) if stock_data else 0
        
        info_data = {
            'Site': site_name,
            'Report Date': datetime.now().strftime('%d/%m/%Y'),
            'Total Materials': total_items,
            'Total Stock Value': self.format_currency(total_value, currency),
            'Low Stock Items': low_stock_items
        }
        self.add_report_info_section(story, info_data)
        
        if stock_data:
            # Stock details table
            story.append(Paragraph("CURRENT STOCK LEVELS", self.header_style))
            
            headers = ['Material', 'Category', 'Current Stock', 'Unit', 'Unit Cost', 'Total Value', 'Min Level', 'Status']
            table_data = []
            
            for item in stock_data:
                status = 'LOW STOCK' if item.quantity < item.minimum_level else 'OK'
                table_data.append([
                    item.material_name,
                    item.category or 'N/A',
                    f"{item.quantity:,.2f}",
                    item.unit,
                    self.format_currency(item.total_value / item.quantity if item.quantity > 0 else 0, currency),
                    self.format_currency(item.total_value, currency),
                    f"{item.minimum_level:,.2f}",
                    status
                ])
            
            table = self.create_professional_table(table_data, headers, currency)
            if table:
                story.append(table)
                
            # Summary section
            story.append(Spacer(1, 30))
            story.append(Paragraph("SUMMARY", self.header_style))
            
            summary_data = {
                'Total Materials': total_items,
                'Total Stock Value': self.format_currency(total_value, currency),
                'Low Stock Items': low_stock_items,
                'Average Value per Material': self.format_currency(total_value / total_items if total_items > 0 else 0, currency)
            }
            self.add_report_info_section(story, summary_data)
            
        else:
            story.append(Paragraph("No stock data available for this site.", self.normal_style))
        
        # Footer
        self.add_footer(story, "Stock Summary")
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_transaction_history_report(self, company_name, site_name, transactions_data, start_date=None, end_date=None, currency='ZMW'):
        """Generate professional transaction history report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Company header
        self.add_company_header(story, company_name, "TRANSACTION HISTORY REPORT")
        
        # Report information
        date_range = ""
        if start_date and end_date:
            date_range = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
        elif start_date:
            date_range = f"From {start_date.strftime('%d/%m/%Y')}"
        elif end_date:
            date_range = f"Until {end_date.strftime('%d/%m/%Y')}"
        else:
            date_range = "All Time"
        
        total_transactions = len(transactions_data) if transactions_data else 0
        receive_count = sum(1 for txn in transactions_data if txn.type == 'receive') if transactions_data else 0
        issue_count = sum(1 for txn in transactions_data if txn.type == 'issue') if transactions_data else 0
        adjustment_count = sum(1 for txn in transactions_data if txn.type == 'adjustment') if transactions_data else 0
        
        info_data = {
            'Site': site_name,
            'Date Range': date_range,
            'Total Transactions': total_transactions,
            'Receive Transactions': receive_count,
            'Issue Transactions': issue_count,
            'Adjustment Transactions': adjustment_count
        }
        self.add_report_info_section(story, info_data)
        
        if transactions_data:
            # Transaction details table
            story.append(Paragraph("TRANSACTION DETAILS", self.header_style))
            
            headers = ['Serial Number', 'Date', 'Material', 'Type', 'Quantity', 'Unit Cost', 'Total Value', 'Project Code']
            table_data = []
            
            for txn in transactions_data:
                table_data.append([
                    txn.serial_number,
                    txn.created_at.strftime('%d/%m/%Y'),
                    txn.material_name,
                    txn.type.upper(),
                    f"{txn.quantity:,.2f} {txn.unit}",
                    self.format_currency(txn.unit_cost, currency),
                    self.format_currency(abs(txn.total_value), currency),
                    txn.issued_to_project_code or 'N/A'
                ])
            
            table = self.create_professional_table(table_data, headers, currency)
            if table:
                story.append(table)
                
            # Summary section
            story.append(Spacer(1, 30))
            story.append(Paragraph("TRANSACTION SUMMARY", self.header_style))
            
            total_received_value = sum(txn.total_value for txn in transactions_data if txn.type == 'receive' and txn.total_value > 0) if transactions_data else 0
            total_issued_value = sum(abs(txn.total_value) for txn in transactions_data if txn.type == 'issue') if transactions_data else 0
            
            summary_data = {
                'Total Transactions': total_transactions,
                'Materials Received (Value)': self.format_currency(total_received_value, currency),
                'Materials Issued (Value)': self.format_currency(total_issued_value, currency),
                'Net Stock Change (Value)': self.format_currency(total_received_value - total_issued_value, currency)
            }
            self.add_report_info_section(story, summary_data)
            
        else:
            story.append(Paragraph("No transactions found for the specified criteria.", self.normal_style))
        
        # Footer
        self.add_footer(story, "Transaction History")
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer


class EnhancedExcelReportGenerator:
    """Enhanced Excel report generator with professional styling"""
    
    def __init__(self):
        pass
    
    def format_currency(self, amount, currency='ZMW'):
        """Format currency for Excel"""
        if currency == 'ZMW':
            return f"K{amount:,.2f}"
        elif currency == 'USD':
            return f"${amount:,.2f}"
        elif currency == 'EUR':
            return f"€{amount:,.2f}"
        elif currency == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"
    
    def generate_comprehensive_excel_report(self, company_name, report_data, currency='ZMW'):
        """Generate comprehensive Excel report with multiple sheets"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Company information sheet
            company_info = pd.DataFrame({
                'Information': ['Company Name', 'Report Generated', 'Currency', 'System'],
                'Value': [company_name, datetime.now().strftime('%d/%m/%Y %H:%M'), currency, 'Inventory Management System']
            })
            company_info.to_excel(writer, sheet_name='Company Info', index=False)
            
            # Sites summary
            if 'sites' in report_data:
                sites_df = pd.DataFrame(report_data['sites'])
                sites_df.to_excel(writer, sheet_name='Sites Summary', index=False)
            
            # Materials summary
            if 'materials' in report_data:
                materials_df = pd.DataFrame(report_data['materials'])
                materials_df.to_excel(writer, sheet_name='Materials Catalog', index=False)
            
            # Stock levels
            if 'stock_levels' in report_data:
                stock_df = pd.DataFrame(report_data['stock_levels'])
                if not stock_df.empty:
                    stock_df['Total Value Formatted'] = stock_df['total_value'].apply(lambda x: self.format_currency(x, currency))
                stock_df.to_excel(writer, sheet_name='Stock Levels', index=False)
            
            # Recent transactions
            if 'transactions' in report_data:
                trans_df = pd.DataFrame(report_data['transactions'])
                if not trans_df.empty:
                    trans_df['Total Value Formatted'] = trans_df['total_value'].apply(lambda x: self.format_currency(abs(x), currency))
                trans_df.to_excel(writer, sheet_name='Transactions', index=False)
        
        buffer.seek(0)
        return buffer