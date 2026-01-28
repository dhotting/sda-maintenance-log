#!/usr/bin/env python3
import sys, os

try:
    from flask import Flask, request, send_file, jsonify, send_from_directory
    from flask_cors import CORS
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.dialects.postgresql import JSON
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    import io, base64, requests
    from datetime import datetime
except ImportError as e:
    print(f"Missing: {e}")
    sys.exit(1)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print("✓ Using PostgreSQL database (data persists across restarts)")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maintenance_logs.db'
    print("⚠️  WARNING: Using SQLite fallback - DATA WILL BE LOST ON RESTART!")
    print("⚠️  Please set DATABASE_URL environment variable in Render")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'
    
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)
    images = db.Column(JSON, default=list)
    logo_url = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'location': self.location,
            'description': self.description,
            'createdBy': self.created_by,
            'timestamp': self.timestamp,
            'images': self.images or [],
            'logoUrl': self.logo_url
        }

# Create tables
with app.app_context():
    db.create_all()
    print("✓ Database tables created")

def download_logo(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'image/*'}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        return io.BytesIO(r.content)
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
    return jsonify({'status': 'ok', 'database': 'connected' if database_url else 'local'})

# ========== LOG API ENDPOINTS ==========

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get all logs"""
    try:
        logs = MaintenanceLog.query.order_by(MaintenanceLog.timestamp.desc()).all()
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['POST'])
def create_log():
    """Create a new log"""
    try:
        data = request.json
        
        required = ['id', 'title', 'category', 'location', 'description', 'createdBy', 'timestamp']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        existing = MaintenanceLog.query.get(data['id'])
        if existing:
            return jsonify({'error': 'Log with this ID already exists'}), 409
        
        log = MaintenanceLog(
            id=data['id'],
            title=data['title'],
            category=data['category'],
            location=data['location'],
            description=data['description'],
            created_by=data['createdBy'],
            timestamp=data['timestamp'],
            images=data.get('images', []),
            logo_url=data.get('logoUrl')
        )
        
        db.session.add(log)
        db.session.commit()
        
        print(f"✓ Created log: {log.id}")
        return jsonify(log.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/<log_id>', methods=['DELETE'])
def delete_log(log_id):
    """Delete a log"""
    try:
        log = MaintenanceLog.query.get(log_id)
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        db.session.delete(log)
        db.session.commit()
        
        print(f"✓ Deleted log: {log_id}")
        return jsonify({'message': 'Log deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting log: {e}")
        return jsonify({'error': str(e)}), 500

# ========== PDF GENERATION ==========

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data'}), 400
        
        print(f"\n✓ Generating PDF for: {data.get('title')}")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.6*inch, leftMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        primary_blue = colors.HexColor('#003366')
        secondary_blue = colors.HexColor('#0066cc')
        light_gray = colors.HexColor('#f5f5f5')
        medium_gray = colors.HexColor('#e0e0e0')
        dark_gray = colors.HexColor('#333333')
        
        logo_url = data.get('logoUrl')
        if logo_url and 'YOUR_LOGO' not in logo_url:
            try:
                logo_buffer = download_logo(logo_url)
                if logo_buffer:
                    logo_img = Image(logo_buffer, width=1*inch, height=1*inch)
                    company_info = Paragraph('<para align="right"><font size="16" color="#003366"><b>SOUTH DADE ACADEMY</b></font><br/><font size="9" color="#666666">Facilities Management Department</font><br/><font size="8" color="#666666">Maintenance & Repair Services</font></para>', styles['Normal'])
                    header_table = Table([[logo_img, company_info]], colWidths=[1.5*inch, 5.5*inch])
                    header_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
                    elements.append(header_table)
            except:
                pass
        
        elements.append(Spacer(1, 0.2*inch))
        
        title_para = Paragraph('<para align="center"><font size="18" color="white"><b>MAINTENANCE SERVICE REPORT</b></font></para>', styles['Normal'])
        title_table = Table([[title_para]], colWidths=[7*inch])
        title_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.25*inch))
        
        doc_id = data.get('id', 'N/A')
        category = data.get('category', 'N/A').upper()
        
        doc_info_data = [[
            Paragraph(f'<para align="center"><font size="8" color="#666666">DOCUMENT ID</font><br/><font size="10" color="#003366"><b>{doc_id}</b></font></para>', styles['Normal']),
            Paragraph(f'<para align="center"><font size="8" color="#666666">CATEGORY</font><br/><font size="10" color="#0066cc"><b>{category}</b></font></para>', styles['Normal'])
        ]]
        
        doc_info_table = Table(doc_info_data, colWidths=[3.5*inch, 3.5*inch])
        doc_info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), light_gray), ('GRID', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        elements.append(doc_info_table)
        elements.append(Spacer(1, 0.15*inch))
        
        meta_label_style = ParagraphStyle('MetaLabel', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#666666'), fontName='Helvetica-Bold')
        meta_value_style = ParagraphStyle('MetaValue', parent=styles['Normal'], fontSize=9, textColor=dark_gray)
        
        meta_data = [
            [Paragraph('Date:', meta_label_style), Paragraph(data.get('timestamp', 'N/A'), meta_value_style), 
             Paragraph('Time:', meta_label_style), Paragraph(datetime.now().strftime('%I:%M %p'), meta_value_style)],
            [Paragraph('Reported By:', meta_label_style), Paragraph(data.get('createdBy', 'N/A'), meta_value_style),
             Paragraph('Status:', meta_label_style), Paragraph('<font color="green"><b>SUBMITTED</b></font>', meta_value_style)]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        meta_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.2*inch))
        
        section_header_style = ParagraphStyle('SectionHeader', parent=styles['Normal'], fontSize=11, textColor=colors.white, fontName='Helvetica-Bold')
        content_style = ParagraphStyle('Content', parent=styles['Normal'], fontSize=10, textColor=dark_gray, leading=14)
        
        issue_header = Paragraph('ISSUE SUMMARY', section_header_style)
        issue_header_table = Table([[issue_header]], colWidths=[7*inch])
        issue_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(issue_header_table)
        
        issue_content = Paragraph(data.get('title', 'N/A'), content_style)
        issue_table = Table([[issue_content]], colWidths=[7*inch])
        issue_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(issue_table)
        elements.append(Spacer(1, 0.15*inch))
        
        loc_header = Paragraph('LOCATION / EQUIPMENT', section_header_style)
        loc_header_table = Table([[loc_header]], colWidths=[7*inch])
        loc_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(loc_header_table)
        
        loc_content = Paragraph(data.get('location', 'N/A'), content_style)
        loc_table = Table([[loc_content]], colWidths=[7*inch])
        loc_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(loc_table)
        elements.append(Spacer(1, 0.15*inch))
        
        desc_header = Paragraph('DETAILED DESCRIPTION', section_header_style)
        desc_header_table = Table([[desc_header]], colWidths=[7*inch])
        desc_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(desc_header_table)
        
        desc_text = data.get('description', 'N/A').replace('\n', '<br/>')
        desc_content = Paragraph(desc_text, content_style)
        desc_table = Table([[desc_content]], colWidths=[7*inch])
        desc_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('LEFTPADDING', (0, 0), (-1, -1), 12), ('RIGHTPADDING', (0, 0), (-1, -1), 12)]))
        elements.append(desc_table)
        
        if data.get('images'):
            elements.append(Spacer(1, 0.2*inch))
            photo_header = Paragraph('PHOTOGRAPHIC DOCUMENTATION', section_header_style)
            photo_header_table = Table([[photo_header]], colWidths=[7*inch])
            photo_header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), primary_blue), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LEFTPADDING', (0, 0), (-1, -1), 12)]))
            elements.append(photo_header_table)
            elements.append(Spacer(1, 0.1*inch))
            
            for i, img_data in enumerate(data['images']):
                try:
                    if ',' in img_data:
                        img_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=5*inch, height=5*inch)
                    caption = Paragraph(f'<para align="center"><font size="9" color="#666666">Photo {i+1} of {len(data["images"])}</font></para>', styles['Normal'])
                    img_table = Table([[img], [caption]], colWidths=[7*inch])
                    img_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (0, 0), 15), ('BOTTOMPADDING', (0, 1), (0, 1), 10)]))
                    elements.append(img_table)
                    elements.append(Spacer(1, 0.15*inch))
                    if (i + 1) % 2 == 0 and i < len(data['images']) - 1:
                        elements.append(PageBreak())
                except Exception as e:
                    print(f"Image error: {e}")
        
        elements.append(Spacer(1, 0.3*inch))
        gen_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        footer_text = f'<para align="center"><font size="7" color="#999999">Generated on {gen_time}<br/>South Dade Academy | Facilities Management<br/><b>CONFIDENTIAL</b><br/>ID: {doc_id}</font></para>'
        footer_para = Paragraph(footer_text, styles['Normal'])
        footer_table = Table([[footer_para]], colWidths=[7*inch])
        footer_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), light_gray), ('BOX', (0, 0), (-1, -1), 1, medium_gray), ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
        elements.append(footer_table)
        
        doc.build(elements)
        buffer.seek(0)
        
        print("✓ PDF generated!")
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'SDA-Report-{doc_id}.pdf')
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n✓ Server with PostgreSQL running on port {port}\n")
    app.run(debug=False, port=port, host='0.0.0.0')
