# Render Backend Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. **Dependencies Check**
- [x] `requirements-prod.txt` includes all necessary packages
- [x] `reportlab` added for PDF export
- [x] Heavy dependencies (opencv, deepface, whisper) excluded from prod
- [x] All imports are conditional based on environment variables

### 2. **Configuration Files**
- [x] `render.yaml` properly configured
- [x] Python version set to 3.11
- [x] Build command: `pip install -r requirements-prod.txt`
- [x] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [x] Health check endpoint: `/health`

### 3. **Environment Variables to Set in Render Dashboard**

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key (set in Render Secrets)

**Optional (already set in render.yaml):**
- `OPENAI_MODEL` = `gpt-4o-mini`
- `ENABLE_RESUME_ROUTER` = `false` (disable heavy resume parser)
- `ENABLE_IMPROVEMENT` = `false` (disable improvement features)
- `ENABLE_VIDEO_INTERVIEW` = `false` (disable video features)
- `ENABLE_LIVE_STREAMING` = `false` (disable opencv features)

### 4. **Static Files**
- [x] `static/` directory exists with `.gitkeep`
- [x] FastAPI mounts static files at `/static`

### 5. **Database**
- [x] SQLite database will be created automatically
- [x] `Base.metadata.create_all(bind=engine)` in main.py
- ⚠️ **Note:** Render's free tier has ephemeral storage - database resets on restart
- 💡 **Recommendation:** Consider upgrading to persistent disk or use external DB

### 6. **CORS Configuration**
- [x] CORS middleware configured to allow all origins (`allow_origins=["*"]`)
- [x] Allows credentials, all methods, and all headers
- ✅ Ready for Bubble.io integration

### 7. **API Endpoints**

**Always Enabled:**
- `/` - Root endpoint
- `/health` - Health check
- `/api/auth/*` - Authentication
- `/api/interview/*` - Interview (database-backed)
- `/api/interview_nodb/*` - Interview (no database)
- `/api/guidance/*` - Guidance
- `/api/mock/*` - Mock interview
- `/api/posts/*` - Posts
- `/api/stt/*` - Speech-to-text
- `/api/cv/*` - CV operations
- `/api/resume-builder/*` - Resume builder (includes PDF/DOCX export)
- `/api/bubble/*` - Bubble.io integration

**Conditionally Enabled (disabled by default):**
- `/api/live_streaming/*` - Requires opencv (ENABLE_LIVE_STREAMING=true)
- `/api/improvement/*` - Resume improvement (ENABLE_IMPROVEMENT=true)
- `/api/resume/*` - Resume parser (ENABLE_RESUME_ROUTER=true)
- `/api/video-interview/*` - Video interview (ENABLE_VIDEO_INTERVIEW=true)

---

## 🚀 Deployment Steps

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `jialekhooo/interviewbot`
4. Render will auto-detect `render.yaml`

### Step 3: Configure Environment Variables
In Render Dashboard → Environment:
1. Add **Secret File** or **Environment Variable**:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
2. Other variables are already set in `render.yaml`

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Render will automatically:
   - Install dependencies from `requirements-prod.txt`
   - Start the app with uvicorn
   - Run health checks on `/health`

### Step 5: Verify Deployment
Once deployed, test these endpoints:
- `https://your-app.onrender.com/` - Should return welcome message
- `https://your-app.onrender.com/health` - Should return `{"status": "ok"}`
- `https://your-app.onrender.com/docs` - FastAPI auto-generated docs

---

## 🔧 Troubleshooting

### Build Fails
**Issue:** Missing dependencies
- **Solution:** Check `requirements-prod.txt` has all needed packages

**Issue:** Python version mismatch
- **Solution:** Verify `PYTHON_VERSION=3.11` in render.yaml

### Runtime Errors
**Issue:** Import errors for opencv/deepface/whisper
- **Solution:** Ensure `ENABLE_LIVE_STREAMING=false` in environment

**Issue:** OpenAI API errors
- **Solution:** Verify `OPENAI_API_KEY` is set in Render Secrets

**Issue:** Static files not found
- **Solution:** Ensure `static/` directory exists in repo

### Database Issues
**Issue:** Database resets on restart
- **Solution:** This is expected on free tier. Upgrade to persistent disk or use PostgreSQL

### CORS Errors
**Issue:** Bubble.io can't connect
- **Solution:** CORS is already configured for `*`. Check Render logs for actual error

---

## 📊 Monitoring

### Logs
- View real-time logs in Render Dashboard
- Check for startup errors
- Monitor API request/response

### Health Checks
- Render automatically pings `/health` endpoint
- Service restarts if health check fails

### Performance
- Free tier: 512MB RAM, shared CPU
- Cold starts after 15 minutes of inactivity
- Consider upgrading for production use

---

## 🔗 Integration with Bubble.io

Your backend URL will be:
```
https://your-app-name.onrender.com
```

Update your Bubble.io API Connector with this base URL:
- Resume PDF: `https://your-app-name.onrender.com/api/resume-builder/generate-pdf`
- Resume DOCX: `https://your-app-name.onrender.com/api/resume-builder/generate-docx`
- Other endpoints: See `/docs` for full API documentation

---

## ✅ Current Status

**Ready for Deployment:** ✅

All configurations are correct. Your backend is ready to deploy on Render!

**Key Features Enabled:**
- ✅ Resume Builder with PDF/DOCX export
- ✅ Interview chatbot (with and without database)
- ✅ Authentication
- ✅ Mock interviews
- ✅ Bubble.io integration endpoints
- ✅ Health monitoring

**Heavy Features Disabled (for free tier):**
- ❌ Live streaming (opencv)
- ❌ Video interview (ffmpeg)
- ❌ Resume improvement (heavy processing)
- ❌ Resume parser (heavy processing)

To enable these, set the corresponding environment variables to `true` and upgrade your Render plan.
