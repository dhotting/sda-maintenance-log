#!/usr/bin/env python3
import sys, os

# Simple dependency check
try:
    from flask import Flask, request, send_file, jsonify, send_from_directory
    from flask_cors import CORS
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib import colors
    import io, base64, requests
    from datetime import datetime
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    try:
        return send_from_directory('.', 'start.html')
    except:
        return '<h1>Error: start.html not found</h1>', 404

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data'}), 400
        
        print(f"\nGenerating PDF for: {data.get('title', 'Unknown')}")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.6*inch, leftMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Simple title
        elements.append(Paragraph(f"<para align='center'><b>{data.get('title', 'Maintenance Report')}</b></para>", styles['Title']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Info
        elements.append(Paragraph(f"<b>Category:</b> {data.get('category', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Location:</b> {data.get('location', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Description:</b> {data.get('description', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Reported by:</b> {data.get('createdBy', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Date:</b> {data.get('timestamp', 'N/A')}", styles['Normal']))
        
        # Images
        if data.get('images'):
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("<b>Photos:</b>", styles['Heading2']))
            for i, img_data in enumerate(data['images']):
                try:
                    if ',' in img_data:
                        img_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    img = Image(img_buffer, width=4*inch, height=4*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    print(f"Image {i} error: {e}")
        
        doc.build(elements)
        buffer.seek(0)
        
        print("✓ PDF generated successfully")
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'Report-{data.get("id", "unknown")}.pdf')
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n✓ Server starting on port {port}\n")
    app.run(debug=False, port=port, host='0.0.0.0')
