#!/usr/bin/env python3
"""
Maintenance Log System - PDF Server
South Dade Academy
"""

import sys
import subprocess
import os
import os

def check_and_install_dependencies():
    """Check if required packages are installed, install if missing"""
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    print("\n" + "="*70)
    print("  CHECKING DEPENDENCIES")
    print("="*70 + "\n")
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            missing_packages.append(package_name)
    
    if missing_packages:
        print("\n" + "="*70)
        print("  INSTALLING MISSING PACKAGES")
        print("="*70 + "\n")
        
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--user", "--quiet"
                ])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                print("\nPlease install manually:")
                print(f"  {sys.executable} -m pip install {package}")
                return False
        
        print("\n✓ All dependencies installed!\n")
    
    return True

# Check dependencies before importing
if not check_and_install_dependencies():
    print("\n❌ Dependency installation failed. Exiting...")
    sys.exit(1)

# Now import the packages
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import base64
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

def print_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print("  MAINTENANCE LOG SYSTEM - PDF SERVER")
    print("  South Dade Academy")
    print("="*70)
    print("\n✓ Server is ready to generate PDF reports")
    print("✓ CORS enabled for browser access")
    print("\n" + "="*70)
    print("  SERVER INFORMATION")
    print("="*70)
    print("\n📡 Server URL: http://localhost:5000")
    print("📄 PDF endpoint: http://localhost:5000/generate-pdf")
    print("💚 Health check: http://localhost:5000/health")
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    print("\n1. Keep this terminal window open")
    print("2. Open index.html in your web browser")
    print("3. Sign in with your @southdadeacademy.com email")
    print("4. Create a log and click 'Export to PDF'")
    print("\n⚠️  IMPORTANT: Don't close this window while using the system!")
    print("="*70 + "\n")

def download_image_from_url(url):
    """Download image from URL and return as BytesIO"""
    try:
        # Add headers to avoid 406 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except Exception as e:
        print(f"⚠️  Warning: Could not download logo - {e}")
        return None

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        print("\n📝 PDF Generation Request")
        print("-" * 50)
        
        log_data = request.json
        print(f"Log ID: {log_data.get('id')}")
        print(f"Title: {log_data.get('title')}")
        print(f"Category: {log_data.get('category', '').upper()}")
        
        # Create PDF in memory with custom page template
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Professional color scheme
        primary_blue = colors.HexColor('#003366')
        secondary_blue = colors.HexColor('#0066cc')
        light_gray = colors.HexColor('#f5f5f5')
        medium_gray = colors.HexColor('#e0e0e0')
        dark_gray = colors.HexColor('#333333')
        
        # === HEADER SECTION ===
        logo_url = log_data.get('logoUrl')
        
        # Create professional header with logo and company info
        header_data = []
        if logo_url and 'YOUR_LOGO' not in logo_url:
            try:
                print("Downloading logo...")
                logo_buffer = download_image_from_url(logo_url)
                if logo_buffer:
                    logo_img = Image(logo_buffer, width=1*inch, height=1*inch)
                    
                    # Company info paragraph
                    company_info = Paragraph('''
                        <para align="right">
                            <font size="16" color="#003366"><b>SOUTH DADE ACADEMY</b></font><br/>
                            <font size="9" color="#666666">Facilities Management Department</font><br/>
                            <font size="8" color="#666666">Maintenance & Repair Services</font>
                        </para>
                    ''', styles['Normal'])
                    
                    header_data = [[logo_img, company_info]]
                    header_table = Table(header_data, colWidths=[1.5*inch, 5.5*inch])
                    header_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elements.append(header_table)
                    print("✓ Logo added")
            except Exception as e:
                print(f"⚠️  Could not add logo: {e}")
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Title banner - better centered
        doc_title = Paragraph(
            '<para align="center" spaceBefore="2" spaceAfter="2"><font size="22" color="white"><b>MAINTENANCE SERVICE REPORT</b></font></para>',
            styles['Normal']
        )
        title_table = Table([[doc_title]], colWidths=[7*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Document reference number box - better formatting
        category_color = secondary_blue if log_data['category'] == 'it' else colors.HexColor('#cc6600')
        category_text = 'IT MAINTENANCE REQUEST' if log_data['category'] == 'it' else 'BUILDING MAINTENANCE REQUEST'
        
        ref_left = Paragraph(
            f'<para align="center" spaceBefore="4" spaceAfter="4">'
            f'<font size="9" color="#666666"><b>DOCUMENT REFERENCE</b></font><br/>'
            f'<font size="18" color="#003366"><b>#{log_data["id"]}</b></font>'
            f'</para>', 
            styles['Normal']
        )
        
        ref_right = Paragraph(
            f'<para align="center" spaceBefore="4" spaceAfter="4">'
            f'<font size="9" color="#666666"><b>CATEGORY</b></font><br/>'
            f'<font size="12" color="{category_color.hexval()}"><b>{category_text}</b></font>'
            f'</para>', 
            styles['Normal']
        )
        
        ref_data = [[ref_left, ref_right]]
        
        ref_table = Table(ref_data, colWidths=[3.5*inch, 3.5*inch])
        ref_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_gray),
            ('GRID', (0, 0), (-1, -1), 1.5, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(ref_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Report information grid
        info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=10, leading=14)
        
        info_grid_data = [
            [
                Paragraph('<b>Date Reported:</b>', info_style),
                Paragraph(log_data['date'], info_style),
                Paragraph('<b>Time Reported:</b>', info_style),
                Paragraph(log_data['time'], info_style)
            ],
            [
                Paragraph('<b>Reported By:</b>', info_style),
                Paragraph(log_data.get('author', 'Unknown'), info_style),
                Paragraph('<b>Status:</b>', info_style),
                Paragraph('<font color="green"><b>SUBMITTED</b></font>', info_style)
            ]
        ]
        
        info_grid = Table(info_grid_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        info_grid.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(info_grid)
        elements.append(Spacer(1, 0.25*inch))
        
        # Section style
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            leading=14
        )
        
        content_text_style = ParagraphStyle(
            'ContentText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=dark_gray,
            leading=16,
            spaceAfter=0
        )
        
        # ISSUE SUMMARY Section
        issue_header = Paragraph('ISSUE SUMMARY', section_header_style)
        issue_header_table = Table([[issue_header]], colWidths=[7*inch])
        issue_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(issue_header_table)
        
        issue_content = Paragraph(f'<b>{log_data["title"]}</b>', content_text_style)
        issue_content_table = Table([[issue_content]], colWidths=[7*inch])
        issue_content_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(issue_content_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # LOCATION Section
        location_header = Paragraph('LOCATION / EQUIPMENT IDENTIFICATION', section_header_style)
        location_header_table = Table([[location_header]], colWidths=[7*inch])
        location_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(location_header_table)
        
        location_content = Paragraph(log_data['location'], content_text_style)
        location_content_table = Table([[location_content]], colWidths=[7*inch])
        location_content_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(location_content_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # DETAILED DESCRIPTION Section
        desc_header = Paragraph('DETAILED DESCRIPTION', section_header_style)
        desc_header_table = Table([[desc_header]], colWidths=[7*inch])
        desc_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(desc_header_table)
        
        description_text = log_data['description'].replace('\n', '<br/>')
        desc_content = Paragraph(description_text, content_text_style)
        desc_content_table = Table([[desc_content]], colWidths=[7*inch])
        desc_content_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(desc_content_table)
        
        # PHOTOGRAPHIC DOCUMENTATION Section
        if log_data.get('images') and len(log_data['images']) > 0:
            print(f"Processing {len(log_data['images'])} images...")
            elements.append(Spacer(1, 0.2*inch))
            
            photo_header = Paragraph('PHOTOGRAPHIC DOCUMENTATION', section_header_style)
            photo_header_table = Table([[photo_header]], colWidths=[7*inch])
            photo_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(photo_header_table)
            elements.append(Spacer(1, 0.1*inch))
            
            for i, img_data in enumerate(log_data['images']):
                try:
                    if ',' in img_data:
                        img_data = img_data.split(',')[1]
                    
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    
                    # Image with caption
                    img = Image(img_buffer, width=5*inch, height=5*inch)
                    caption = Paragraph(
                        f'<para align="center"><font size="9" color="#666666">Photo {i+1} of {len(log_data["images"])}</font></para>',
                        styles['Normal']
                    )
                    
                    img_table = Table([[img], [caption]], colWidths=[7*inch])
                    img_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                        ('BOX', (0, 0), (-1, -1), 1, medium_gray),
                        ('TOPPADDING', (0, 0), (0, 0), 15),
                        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
                        ('TOPPADDING', (0, 1), (0, 1), 8),
                        ('BOTTOMPADDING', (0, 1), (0, 1), 10),
                    ]))
                    elements.append(img_table)
                    elements.append(Spacer(1, 0.15*inch))
                    
                    if (i + 1) % 2 == 0 and i < len(log_data['images']) - 1:
                        elements.append(PageBreak())
                        
                except Exception as e:
                    print(f"⚠️  Error with image {i+1}: {e}")
        
        # Footer section
        elements.append(Spacer(1, 0.3*inch))
        
        generation_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        footer_content = f'''
            <para align="center" spaceAfter="4">
                <font size="7" color="#999999">
                    This document was electronically generated on {generation_time}<br/>
                    South Dade Academy | Facilities Management Department<br/>
                    <b>CONFIDENTIAL — FOR INTERNAL USE ONLY</b><br/>
                    Document ID: {log_data["id"]}
                </font>
            </para>
        '''
        
        footer_para = Paragraph(footer_content, styles['Normal'])
        footer_table = Table([[footer_para]], colWidths=[7*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_gray),
            ('BOX', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(footer_table)
        
        # Build PDF
        print("Building PDF...")
        doc.build(elements)
        buffer.seek(0)
        
        print("✓ PDF generated successfully!")
        print("-" * 50 + "\n")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'SDA-MaintenanceReport-{log_data["id"]}.pdf'
        )
        
    except Exception as e:
        print(f"\n❌ ERROR generating PDF:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        print("-" * 50 + "\n")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'PDF server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Maintenance Log System - PDF Server',
        'school': 'South Dade Academy',
        'status': 'running',
        'endpoints': {
            '/health': 'GET - Health check',
            '/generate-pdf': 'POST - Generate PDF from log data'
        }
    })

if __name__ == '__main__':
    print_banner()
    
    # Get port from environment (Render uses PORT environment variable)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    try:
        # Use 0.0.0.0 to allow external connections (required for Render)
        app.run(debug=debug_mode, port=port, host='0.0.0.0')
    except OSError as e:
        if "Address already in use" in str(e):
            print("\n" + "="*70)
            print("  ERROR: PORT IS ALREADY IN USE")
            print("="*70)
            print(f"\n❌ Another application is using port {port}")
            print("\n" + "="*70 + "\n")
        else:
            print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
