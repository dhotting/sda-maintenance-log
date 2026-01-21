#!/usr/bin/env python3
"""
Maintenance Log System - PDF Server with Frontend
South Dade Academy
"""

import sys
import subprocess
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
                    sys.executable, "-m", "pip", "install", package, "--break-system-packages"
                ])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                print("\nPlease install manually:")
                print(f"  {sys.executable} -m pip install {package} --break-system-packages")
                return False
        
        print("\n✓ All dependencies installed!\n")
    
    return True

# Check dependencies before importing
if not check_and_install_dependencies():
    print("\n❌ Dependency installation failed. Exiting...")
    sys.exit(1)

# Now import the packages
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import base64
from datetime import datetime
import requests

# Create Flask app - static_folder set to current directory to serve start.html
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

def print_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print("  MAINTENANCE LOG SYSTEM - FULL STACK SERVER")
    print("  South Dade Academy")
    print("="*70)
    print("\n✓ Server is ready!")
    print("✓ Serving both frontend and backend")
    print("\n" + "="*70)
    print("  ACCESS YOUR APP")
    print("="*70)
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    print(f"\n🌐 Website: {render_url}")
    print(f"📄 PDF API: {render_url}/generate-pdf")
    print(f"💚 Health: {render_url}/health")
    print("\n" + "="*70 + "\n")

def download_image_from_url(url):
    """Download image from URL and return as BytesIO"""
    try:
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

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        # Serve start.html from the current directory
        return send_from_directory('.', 'start.html')
    except Exception as e:
        print(f"Error serving start.html: {e}")
        # Fallback message if start.html doesn't exist
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SDA Maintenance Log</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 100px auto;
                    padding: 20px;
                    text-align: center;
                }
                h1 { color: #0066ff; }
                .error { color: #ef4444; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Maintenance Log System</h1>
            <p>Backend server is running!</p>
            <div class="error">
                <p><strong>Error:</strong> start.html file not found.</p>
                <p>Please make sure start.html is in the repository root.</p>
            </div>
        </body>
        </html>
        '''

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        print("\n📝 PDF Generation Request")
        print("-" * 50)
        
        log_data = request.json
        print(f"Log ID: {log_data.get('id')}")
        print(f"Title: {log_data.get('title')}")
        print(f"Category: {log_data.get('category', '').upper()}")
        
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
        
        header_data = []
        if logo_url and 'YOUR_LOGO' not in logo_url:
            try:
                print("Downloading logo...")
                logo_buffer = download_image_from_url(logo_url)
                if logo_buffer:
                    logo_img = Image(logo_buffer, width=1*inch, height=1*inch)
                    
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
        
        # Report Info Section
        report_timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        info_data = [
            ['Report ID:', log_data['id']],
            ['Generated:', report_timestamp],
            ['Category:', log_data['category'].upper()],
            ['Reported by:', log_data['createdBy']],
            ['Date Reported:', log_data['timestamp']]
        ]
        
        formatted_info_data = []
        label_style = ParagraphStyle(
            'LabelStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=secondary_blue,
            fontName='Helvetica-Bold',
            spaceAfter=2
        )
        value_style = ParagraphStyle(
            'ValueStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=dark_gray,
            spaceAfter=2
        )
        
        for label, value in info_data:
            label_para = Paragraph(label, label_style)
            value_para = Paragraph(str(value), value_style)
            formatted_info_data.append([label_para, value_para])
        
        info_table = Table(formatted_info_data, colWidths=[2*inch, 5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_gray),
            ('GRID', (0, 0), (-1, -1), 1, medium_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # ISSUE DESCRIPTION Section
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            leading=14
        )
        
        content_text_style = ParagraphStyle(
            'ContentText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=dark_gray,
            leading=16,
            spaceAfter=6
        )
        
        issue_header = Paragraph('ISSUE / REQUEST SUMMARY', section_header_style)
        issue_header_table = Table([[issue_header]], colWidths=[7*inch])
        issue_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(issue_header_table)
        
        issue_content = Paragraph(log_data['title'], content_text_style)
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

if __name__ == '__main__':
    print_banner()
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    try:
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
