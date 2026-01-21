# Maintenance Log System - Quick Start

## 🚀 3-Step Setup

### Step 1: Add Your School Logo

1. Open `index.html` in any text editor
2. Find line 634 (search for `CUSTOM_LOGO_URL`)
3. Replace with your logo URL

**Example:**
```javascript
const CUSTOM_LOGO_URL = 'https://yourschool.edu/logo.png';
```

### Step 2: Start the PDF Server

**Mac/Linux:**
```bash
python3 pdf_server.py
```

**Windows:**
```bash
python pdf_server.py
```

The server will automatically install dependencies!

**Keep this window open!**

### Step 3: Open the Website

Double-click `index.html` to open in your browser.

---

## 🔧 Troubleshooting

### "pip: command not found"

**Mac/Linux:**
```bash
python3 -m pip install Flask flask-cors reportlab Pillow requests --user
python3 pdf_server.py
```

**Windows:**
```bash
py -m pip install Flask flask-cors reportlab Pillow requests
py pdf_server.py
```

### "Port 5000 already in use"

**Kill the process:**
```bash
# Mac/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
# Then: taskkill /PID [PID] /F
```

---

## 📝 Usage

1. Sign in with @southdadeacademy.com email
2. Create logs with title, category, location, description
3. Add images (optional, max 5MB each)
4. Export to PDF anytime

---

**Need more help?** See SETUP_GUIDE.md for deployment options.
