# 🚀 Deployment Guide - Render + Google Cloud OAuth

## Complete Production Deployment for South Dade Academy

This guide will help you deploy your Maintenance Log System with:
- ✅ Professional Google OAuth login
- ✅ Backend on Render
- ✅ Frontend on Render (or GitHub Pages)
- ✅ Proper domain restrictions
- ✅ Production-ready setup

---

## 📋 Prerequisites

- [x] Google Cloud Console access for your organization
- [x] Render account (you mentioned you have this)
- [x] GitHub account (for code repository)
- [x] Your organization's domain: southdadeacademy.com

---

## Part 1: Set Up Google Cloud OAuth

### Step 1: Create OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Sign in with your organization account

2. **Create/Select a Project**
   - Click "Select a project" → "New Project"
   - Name: "SDA Maintenance System"
   - Click "Create"

3. **Enable Google Sign-In API**
   - Navigate to: APIs & Services → Library
   - Search for "Google Identity Services"
   - Click "Enable"

4. **Configure OAuth Consent Screen**
   - Go to: APIs & Services → OAuth consent screen
   - Select "Internal" (only for your organization)
   - App name: "South Dade Academy Maintenance Log"
   - User support email: your IT email
   - Developer contact: your IT email
   - Click "Save and Continue"
   - Skip scopes (default is fine)
   - Click "Save and Continue"

5. **Create OAuth Client ID**
   - Go to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "Maintenance Log Web Client"
   
   **Authorized JavaScript origins:**
   ```
   http://localhost:8000
   https://[YOUR-APP-NAME].onrender.com
   ```
   
   **Authorized redirect URIs:**
   ```
   http://localhost:8000
   https://[YOUR-APP-NAME].onrender.com
   ```
   
   - Click "Create"
   - **SAVE YOUR CLIENT ID** - you'll need this!

### Step 2: Configure Domain Restriction

In OAuth consent screen:
- Under "Authorized domains" add: `southdadeacademy.com`
- This ensures only your organization's Google accounts can log in

---

## Part 2: Prepare Code for Deployment

### Step 1: Update index.html with OAuth Client ID

Open `index.html` and update line ~640:

```javascript
// Replace this with YOUR actual Google Client ID from Step 1.5
const GOOGLE_CLIENT_ID = 'YOUR_CLIENT_ID_HERE.apps.googleusercontent.com';
```

### Step 2: Create Production HTML File

Create a new file `index_production.html` (copy of index.html with these changes):

**Replace the handleGoogleLogin function (around line 680) with:**

```javascript
function handleGoogleLogin() {
    google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true
    });
    
    google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // Fallback to One Tap if prompt fails
            google.accounts.id.renderButton(
                document.getElementById("googleSignInButton"),
                { 
                    theme: "outline", 
                    size: "large",
                    width: "100%",
                    text: "signin_with"
                }
            );
        }
    });
}

function handleCredentialResponse(response) {
    try {
        // Decode JWT token
        const credential = parseJwt(response.credential);
        
        console.log('User info:', credential);
        
        // Validate email domain
        if (!isValidEmail(credential.email)) {
            showToast('Access denied. Only @southdadeacademy.com emails are allowed.', 'error');
            return;
        }
        
        currentUser = {
            email: credential.email,
            name: credential.name,
            picture: credential.picture
        };
        
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showApp();
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    }
}

function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}
```

**Update the login button HTML (around line 465):**

```html
<button class="google-signin-btn" id="googleSignInButton" onclick="handleGoogleLogin()">
    <svg class="google-icon" viewBox="0 0 24 24">
        <!-- Google icon SVG -->
    </svg>
    Sign in with Google
</button>
```

### Step 3: Update PDF Server for Production

Create `pdf_server_production.py`:

```python
import os

# ... (keep all the existing code)

# At the bottom, change:
if __name__ == '__main__':
    print_banner()
    
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    try:
        app.run(
            debug=debug, 
            port=port, 
            host='0.0.0.0'  # Important for Render
        )
    except OSError as e:
        # ... (keep existing error handling)
```

---

## Part 3: Deploy Backend to Render

### Step 1: Create GitHub Repository

1. **Create a new GitHub repository:**
   - Go to github.com
   - Create new repo: "sda-maintenance-system"
   - Make it private

2. **Push your code:**

```bash
cd ~/Documents/projects/audit_log
git init
git add .
git commit -m "Initial commit - Production ready"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sda-maintenance-system.git
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select "sda-maintenance-system"

3. **Configure the service:**

   **Name:** `sda-maintenance-server`
   
   **Environment:** `Python 3`
   
   **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```bash
   python pdf_server_production.py
   ```
   
   **Instance Type:** `Free` (or paid for better performance)

4. **Environment Variables:**
   
   Click "Advanced" → Add environment variables:
   
   ```
   FLASK_ENV=production
   PORT=10000
   ```

5. **Click "Create Web Service"**

6. **Wait for deployment** (takes 2-3 minutes)

7. **Copy your backend URL:**
   ```
   https://sda-maintenance-server.onrender.com
   ```

### Step 3: Update Frontend with Backend URL

In `index_production.html`, update line ~638:

```javascript
const PDF_SERVER_URL = 'https://sda-maintenance-server.onrender.com';
```

---

## Part 4: Deploy Frontend to Render

### Option A: Deploy Frontend to Render (Recommended)

1. **Create New Static Site**
   - In Render Dashboard: "New +" → "Static Site"
   - Connect same GitHub repository

2. **Configure:**
   
   **Name:** `sda-maintenance-system`
   
   **Build Command:**
   ```bash
   # Leave empty or use: echo "No build needed"
   ```
   
   **Publish Directory:**
   ```
   .
   ```

3. **Click "Create Static Site"**

4. **Your frontend URL:**
   ```
   https://sda-maintenance-system.onrender.com
   ```

### Option B: Deploy to GitHub Pages (Alternative)

1. **Create `docs` folder** in your repo
2. **Copy `index_production.html` to `docs/index.html`**
3. **Push to GitHub**
4. **Enable GitHub Pages:**
   - Repo Settings → Pages
   - Source: "Deploy from branch"
   - Branch: `main` / `docs`
   - Save

5. **Your URL:**
   ```
   https://YOUR_USERNAME.github.io/sda-maintenance-system
   ```

---

## Part 5: Update Google OAuth with Production URLs

1. **Go back to Google Cloud Console**
   - APIs & Services → Credentials
   - Click your OAuth Client ID

2. **Update Authorized JavaScript origins:**
   ```
   https://sda-maintenance-server.onrender.com
   https://sda-maintenance-system.onrender.com
   ```

3. **Update Authorized redirect URIs:**
   ```
   https://sda-maintenance-system.onrender.com
   ```

4. **Click "Save"**

---

## Part 6: Test Your Deployment

1. **Visit your frontend URL:**
   ```
   https://sda-maintenance-system.onrender.com
   ```

2. **Test login:**
   - Click "Sign in with Google"
   - Use your @southdadeacademy.com email
   - Should redirect and show the app

3. **Test creating a log**

4. **Test PDF export:**
   - Create a log with images
   - Click "Export to PDF"
   - PDF should download

---

## Part 7: Custom Domain (Optional)

If you want to use a custom domain like `maintenance.southdadeacademy.com`:

### On Render:

1. **Add custom domain:**
   - Go to your static site settings
   - Click "Custom Domains"
   - Add: `maintenance.southdadeacademy.com`

2. **Update DNS:**
   - In your domain registrar, add CNAME record:
   ```
   maintenance.southdadeacademy.com → sda-maintenance-system.onrender.com
   ```

3. **Update Google OAuth:**
   - Add custom domain to authorized origins and redirects

---

## 🔒 Security Checklist

- [x] OAuth set to "Internal" (organization only)
- [x] Domain restriction: `southdadeacademy.com`
- [x] Email validation in code
- [x] HTTPS enabled (automatic on Render)
- [x] Environment variables for sensitive data
- [x] CORS properly configured

---

## 📁 Final File Structure

```
sda-maintenance-system/
├── index.html (production version)
├── pdf_server.py
├── requirements.txt
├── README.md
└── .gitignore
```

**Create `.gitignore`:**
```
venv/
*.pyc
__pycache__/
.DS_Store
.env
```

---

## 🐛 Troubleshooting

### "OAuth Error: redirect_uri_mismatch"
- Make sure your Render URL is added to authorized redirect URIs in Google Cloud Console

### "Access denied" when logging in
- Check that email ends with @southdadeacademy.com
- Verify domain restriction is set correctly

### PDF export not working
- Check that PDF_SERVER_URL points to your Render backend
- Verify backend is running: visit `https://your-backend.onrender.com/health`

### Backend sleeping (Free tier)
- Render free tier sleeps after 15 minutes
- First request takes ~30 seconds to wake up
- Upgrade to paid tier for always-on service

---

## 💰 Cost Breakdown

**Free Option:**
- Render Free Tier: $0
- GitHub: $0
- Google Cloud: $0
- **Total: $0/month**

**Paid Option (Recommended for production):**
- Render Starter (backend): $7/month
- Render Static (frontend): Free
- **Total: $7/month**

---

## 🎯 Next Steps

1. ✅ Get Google Client ID from Cloud Console
2. ✅ Update index.html with Client ID
3. ✅ Push code to GitHub
4. ✅ Deploy backend to Render
5. ✅ Deploy frontend to Render
6. ✅ Update OAuth settings
7. ✅ Test everything
8. ✅ Share with staff!

---

## 📞 Support

If you run into issues:

1. Check Render logs (Dashboard → Your Service → Logs)
2. Check browser console (F12)
3. Verify OAuth settings match deployment URLs
4. Test backend health endpoint

---

**Ready to deploy? Let's go! 🚀**

Questions? Let me know which step you're on and I can help troubleshoot.
