# Deployment Guide

## Deployment Fixed ✅

The deployment failures have been resolved by making optional features that require heavy dependencies disabled by default in production.

## Changes Made

### 1. Made Video Interview Feature Optional
The video interview router and model are now only loaded when `ENABLE_VIDEO_INTERVIEW=true` is set in environment variables.

**Why this was needed:**
- Video interview feature requires additional dependencies (ffmpeg, audio processing libraries)
- These dependencies are not in `requirements-prod.txt` to keep production deployment lightweight
- The feature is now opt-in rather than always enabled

### 2. Made Resume Improvement Feature Optional
The improvement router requires PyPDF2 and is now disabled by default in production.

### 3. Environment Variables

**Production (Render) - Current Settings:**
```bash
ENABLE_VIDEO_INTERVIEW=false  # Video interview disabled (requires ffmpeg)
ENABLE_RESUME_ROUTER=false    # Resume parser disabled (requires PyPDF2, spacy, etc.)
ENABLE_IMPROVEMENT=false      # Resume improvement disabled (requires PyPDF2)
ENABLE_LIVE_STREAMING=false   # Live streaming disabled (requires OpenCV)
```

**Local Development - To Enable All Features:**
```bash
ENABLE_VIDEO_INTERVIEW=true   # Enable video interview
ENABLE_RESUME_ROUTER=true     # Enable resume parser
ENABLE_IMPROVEMENT=true       # Enable resume improvement
ENABLE_LIVE_STREAMING=true    # Enable live streaming
```

## Deployment Instructions

### Render Deployment (Current Setup)

1. **Automatic Deployment:**
   - Push to main branch
   - Render automatically deploys using `render.yaml` configuration
   - Uses `requirements-prod.txt` (lightweight dependencies)

2. **To Enable Video Interview in Production:**
   ```bash
   # Add to Render Dashboard > Environment Variables
   ENABLE_VIDEO_INTERVIEW=true
   ```
   
   **Note:** You'll also need to:
   - Install ffmpeg on the Render instance (requires custom build)
   - Update to full `requirements.txt` instead of `requirements-prod.txt`
   - This may require upgrading from free tier

### Vercel Deployment (Frontend)

The frontend is configured for Vercel deployment via `vercel.json`.

**Deploy Frontend:**
```bash
cd frontend
npm run build
# Deploy to Vercel
```

### Local Development

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_api_key_here
   ENABLE_VIDEO_INTERVIEW=true
   ENABLE_RESUME_ROUTER=true
   ```

3. **Run Backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Feature Flags

### ENABLE_VIDEO_INTERVIEW
- **Default:** `false`
- **Requires:** ffmpeg, OpenAI API key
- **Endpoints:** `/api/video-interview/*`
- **Dependencies:** Not in `requirements-prod.txt`

### ENABLE_RESUME_ROUTER
- **Default:** `false` (in production)
- **Requires:** Heavy NLP libraries (spacy, tesseract, etc.)
- **Endpoints:** `/api/resume/*`
- **Dependencies:** Not in `requirements-prod.txt`

### ENABLE_LIVE_STREAMING
- **Default:** `false`
- **Requires:** OpenCV, camera access
- **Endpoints:** `/api/live_streaming/*`
- **Dependencies:** opencv-python (not in prod)

## Production Dependencies (requirements-prod.txt)

Lightweight dependencies for production:
- FastAPI & Uvicorn
- OpenAI SDK
- SQLAlchemy
- Authentication (python-jose, passlib)
- Basic utilities

## Full Dependencies (requirements.txt)

Includes all features:
- Everything in requirements-prod.txt
- OpenCV for video processing
- Whisper for speech-to-text
- Spacy for NLP
- PDF/Document parsers
- DeepFace for emotion detection

## Troubleshooting

### Deployment Fails with Import Error
**Solution:** Ensure optional features are disabled or add required dependencies to `requirements-prod.txt`

### Video Interview Not Working
**Check:**
1. `ENABLE_VIDEO_INTERVIEW=true` is set
2. ffmpeg is installed on the system
3. OpenAI API key is configured
4. Full `requirements.txt` is used

### Database Migration Issues
**Solution:** Optional models (like DBVideoInterview) are only imported when their feature flag is enabled, preventing migration errors

## Current Deployment Status

✅ **Backend:** Deployed on Render (lightweight mode)
- Interview simulation: ✅ Working
- Authentication: ✅ Working
- Posts/Forum: ✅ Working
- Resume Builder: ✅ Working (uses OpenAI, no heavy dependencies)
- Video Interview: ❌ Disabled (requires manual enable)
- Resume Parser: ❌ Disabled (requires manual enable)
- Resume Improvement: ❌ Disabled (requires manual enable)

✅ **Frontend:** Can be deployed on Vercel
- All pages accessible
- Video interview page exists but backend disabled
- Forum and posts working

## Enabling Video Interview in Production

If you want to enable video interview in production:

1. **Update render.yaml:**
   ```yaml
   buildCommand: pip install -r requirements.txt  # Use full requirements
   envVars:
     - key: ENABLE_VIDEO_INTERVIEW
       value: "true"
   ```

2. **Add ffmpeg to build:**
   Create `render-build.sh`:
   ```bash
   #!/bin/bash
   apt-get update
   apt-get install -y ffmpeg
   pip install -r requirements.txt
   ```
   
   Update render.yaml:
   ```yaml
   buildCommand: ./render-build.sh
   ```

3. **Note:** This will increase build time and may require paid tier

## Summary

The deployment is now fixed and working. The video interview feature is available for local development but disabled in production by default to keep the deployment lightweight and fast. You can enable it anytime by setting the environment variable and updating dependencies.
