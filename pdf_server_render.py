#!/usr/bin/env python3
"""
Maintenance Log System - Complete Server
South Dade Academy  
"""

import sys
import subprocess
import os

def check_and_install_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
        'requests': 'requests'
    }
    
    missing_packages = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])
            except subprocess.CalledProcessError:
                return False
    return True

if not check_and_install_dependencies():
    sys.exit(1)

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
import io
import base64
from datetime import datetime
import requests

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

def download_image_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'image/*'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except:
        return None

@app.route('/')
def index():
    try:
        return send_from_directory('.', 'start.html')
    except:
        return '<h1>Error: start.html not found</h1>', 404

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        log_data = request.json
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.6*inch, leftMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        primary_blue = colors.HexColor('#003366')
        secondary_blue = colors.HexColor('#0066cc')
        light_gray = colors.HexColor('#f5f5f5')
        medium_gray = colors.HexColor('#e0e0e0')
        dark_gray = colors.HexColor('#333333')
        
        logo_url = log_data.get('logoUrl')
        if logo_url and 'YOUR_LOGO' not in logo_url:
            try:
                logo_buffer = download_image_from_url(logo_url)
                if logo_buffer:
                    logo_img = Image(logo_buffer, width=1*inch, height=1*inch)
                    company_info = Paragraph('<para align="right"><font size="16" color="#003366"><b>SOUTH DADE ACADEMY</b></font><br/><font size="9" color="#666666">Facilities Management Department</font></para>', styles['Normal'])
                    header_table = Table([[logo_img, company_info]], colWidths=[1.5*inch, 5.5*inch])
                    header_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
                    elements.append(header_table)
            except:
                pass
        
        elements.append(Spacer(1, 0.2*inch))
        doc_title = Paragraph('<para align="center"><font size="22" color="white"><b>MAINTENANCE SERVICE REPORT</b></font></para>', styles['Normal'])
        title_table = Table([[doc_title]], colWidths=[7*inch])
        title_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 16), ('BOTTOMPADDING', (0, 0), (-1, -1), 16)]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.3*inch))
        
        report_timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        info_data = [['Report ID:', log_data['id']], ['Generated:', report_timestamp], ['Category:', log_data['category'].upper()], ['Reported by:', log_data['createdBy']], ['Date Reported:', log_data['timestamp']]]
        label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=10, textColor=secondary_blue, fontName='Helvetica-Bold')
        value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=10, textColor=dark_gray)
        formatted_info = [[Paragraph(label, label_style), Paragraph(str(value), value_style)] for label, value in info_data]
        info_table = Table(formatted_info, colWidths=[2*inch, 5*inch])
        info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), light_gray), ('GRID', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.25*inch))
        
        section_header_style = ParagraphStyle('SectionHeader', parent=styles['Normal'], fontSize=12, textColor=colors.white, fontName='Helvetica-Bold')
        content_text_style = ParagraphStyle('ContentText', parent=styles['Normal'], fontSize=11, textColor=dark_gray, leading=16)
        
        issue_header = Paragraph('ISSUE / REQUEST SUMMARY', section_header_style)
        issue_header_table = Table([[issue_header]], colWidths=[7*inch])
        issue_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(issue_header_table)
        issue_content = Paragraph(log_data['title'], content_text_style)
        issue_content_table = Table([[issue_content]], colWidths=[7*inch])
        issue_content_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(issue_content_table)
        elements.append(Spacer(1, 0.15*inch))
        
        location_header = Paragraph('LOCATION / EQUIPMENT IDENTIFICATION', section_header_style)
        location_header_table = Table([[location_header]], colWidths=[7*inch])
        location_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(location_header_table)
        location_content = Paragraph(log_data['location'], content_text_style)
        location_content_table = Table([[location_content]], colWidths=[7*inch])
        location_content_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(location_content_table)
        elements.append(Spacer(1, 0.15*inch))
        
        desc_header = Paragraph('DETAILED DESCRIPTION', section_header_style)
        desc_header_table = Table([[desc_header]], colWidths=[7*inch])
        desc_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(desc_header_table)
        description_text = log_data['description'].replace('\n', '<br/>')
        desc_content = Paragraph(description_text, content_text_style)
        desc_content_table = Table([[desc_content]], colWidths=[7*inch])
        desc_content_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(desc_content_table)
        
        if log_data.get('images'):
            elements.append(Spacer(1, 0.2*inch))
            photo_header = Paragraph('PHOTOGRAPHIC DOCUMENTATION', section_header_style)
            photo_header_table = Table([[photo_header]], colWidths=[7*inch])
            photo_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
            elements.append(photo_header_table)
            elements.append(Spacer(1, 0.1*inch))
            for i, img_data in enumerate(log_data['images']):
                try:
                    if ',' in img_data:
                        img_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=5*inch, height=5*inch)
                    caption = Paragraph(f'<para align="center"><font size="9" color="#666666">Photo {i+1} of {len(log_data["images"])}</font></para>', styles['Normal'])
                    img_table = Table([[img], [caption]], colWidths=[7*inch])
                    img_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (0, 0), 15), ('BOTTOMPADDING', (0, 1), (0, 1), 10)]))
                    elements.append(img_table)
                    elements.append(Spacer(1, 0.15*inch))
                    if (i + 1) % 2 == 0 and i < len(log_data['images']) - 1:
                        elements.append(PageBreak())
                except:
                    pass
        
        elements.append(Spacer(1, 0.3*inch))
        generation_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        footer_content = f'<para align="center"><font size="7" color="#999999">Generated on {generation_time}<br/>South Dade Academy | Facilities Management<br/><b>CONFIDENTIAL</b><br/>Document ID: {log_data["id"]}</font></para>'
        footer_para = Paragraph(footer_content, styles['Normal'])
        footer_table = Table([[footer_para]], colWidths=[7*inch])
        footer_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), light_gray), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
        elements.append(footer_table)
        
        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'SDA-MaintenanceReport-{log_data["id"]}.pdf')
    except Exception as e:
        print(f"PDF Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"\n✓ Server running at port {port}\n")
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
