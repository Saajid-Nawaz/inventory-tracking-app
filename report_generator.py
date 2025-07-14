"""
Report Generator Service
Handles PDF and Excel export functionality
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import pandas as pd
from datetime import datetime
import os


class PDFReportGenerator:
    """Generate PDF reports for various inventory data"""
    
    @staticmethod
    def generate_daily_issues_report(site_name, report_date, issues_data):
        """
        Generate PDF report for daily material issues
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Title
        title = Paragraph(f"Daily Material Issues Report", title_style)
        story.append(title)
        
        # Site and date info
        site_info = Paragraph(f"<b>Site:</b> {site_name}<br/><b>Date:</b> {report_date.strftime('%B %d, %Y')}", styles['Normal'])
        story.append(site_info)
        story.append(Spacer(1, 20))
        
        if issues_data:
            # Create table data
            table_data = [
                ['Serial Number', 'Time', 'Material', 'Quantity', 'Unit Cost', 'Total Value', 'Project Code']
            ]
            
            total_value = 0
            for issue in issues_data:
                table_data.append([
                    issue.serial_number,
                    issue.created_at.strftime('%H:%M'),
                    issue.material_name,
                    f"{abs(issue.quantity)} {issue.unit}",
                    f"${issue.unit_cost:.2f}",
                    f"${abs(issue.total_value):.2f}",
                    issue.issued_to_project_code or 'N/A'
                ])
                total_value += abs(issue.total_value)
            
            # Add total row
            table_data.append(['', '', '', '', '', f"${total_value:.2f}", 'TOTAL'])
            
            # Create table
            table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No material issues recorded for this date.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    @staticmethod
    def generate_stock_summary_report(site_name, stock_data):
        """
        Generate PDF report for stock summary
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Title
        title = Paragraph(f"Stock Summary Report", title_style)
        story.append(title)
        
        # Site and date info
        site_info = Paragraph(f"<b>Site:</b> {site_name}<br/><b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
        story.append(site_info)
        story.append(Spacer(1, 20))
        
        if stock_data:
            # Create table data
            table_data = [
                ['Material Name', 'Unit', 'Quantity', 'Total Value', 'Avg Cost', 'Min Level', 'Status']
            ]
            
            total_inventory_value = 0
            low_stock_count = 0
            
            for item in stock_data:
                avg_cost = item.total_value / item.quantity if item.quantity > 0 else 0
                status = "LOW STOCK" if item.quantity < item.minimum_level else "OK"
                if item.quantity < item.minimum_level:
                    low_stock_count += 1
                
                table_data.append([
                    item.material_name,
                    item.unit,
                    f"{item.quantity:.2f}",
                    f"${item.total_value:.2f}",
                    f"${avg_cost:.2f}",
                    f"{item.minimum_level:.2f}",
                    status
                ])
                total_inventory_value += item.total_value
            
            # Create table
            table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            # Color code low stock items
            for i, item in enumerate(stock_data, 1):
                if item.quantity < item.minimum_level:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.lightcoral),
                    ]))
            
            story.append(table)
            
            # Summary
            story.append(Spacer(1, 20))
            summary_text = f"""
            <b>Summary:</b><br/>
            Total Inventory Value: ${total_inventory_value:.2f}<br/>
            Total Materials: {len(stock_data)}<br/>
            Low Stock Items: {low_stock_count}
            """
            story.append(Paragraph(summary_text, styles['Normal']))
        else:
            story.append(Paragraph("No stock data available.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data


class ExcelReportGenerator:
    """Generate Excel reports for various inventory data"""
    
    @staticmethod
    def generate_stock_summary_excel(site_name, stock_data):
        """
        Generate Excel report for stock summary
        """
        buffer = BytesIO()
        
        # Create DataFrame
        data = []
        for item in stock_data:
            avg_cost = item.total_value / item.quantity if item.quantity > 0 else 0
            status = "LOW STOCK" if item.quantity < item.minimum_level else "OK"
            
            data.append({
                'Material Name': item.material_name,
                'Unit': item.unit,
                'Quantity': item.quantity,
                'Total Value': item.total_value,
                'Average Cost': avg_cost,
                'Minimum Level': item.minimum_level,
                'Status': status
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Stock Summary', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': ['Total Inventory Value', 'Total Materials', 'Low Stock Items'],
                'Value': [
                    df['Total Value'].sum(),
                    len(df),
                    len(df[df['Status'] == 'LOW STOCK'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format the sheets
            workbook = writer.book
            
            # Format stock summary sheet
            worksheet = writer.sheets['Stock Summary']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_data = buffer.getvalue()
        buffer.close()
        
        return excel_data
    
    @staticmethod
    def generate_transaction_history_excel(site_name, transactions_data):
        """
        Generate Excel report for transaction history
        """
        buffer = BytesIO()
        
        # Create DataFrame
        data = []
        for txn in transactions_data:
            data.append({
                'Serial Number': txn.serial_number,
                'Date': txn.created_at.strftime('%Y-%m-%d'),
                'Time': txn.created_at.strftime('%H:%M:%S'),
                'Material': txn.material_name,
                'Unit': txn.unit,
                'Quantity': txn.quantity,
                'Unit Cost': txn.unit_cost,
                'Total Value': txn.total_value,
                'Type': txn.type.title(),
                'Project Code': txn.issued_to_project_code or 'N/A',
                'Notes': txn.notes or 'N/A'
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transaction History', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Transaction History']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_data = buffer.getvalue()
        buffer.close()
        
        return excel_data