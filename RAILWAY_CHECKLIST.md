# 🚂 Railway Deployment Checklist

## Quick Start Guide

### 1. Commit Your Code
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy to Railway

**Option: Railway Dashboard (Recommended)**
1. Go to https://railway.app
2. Sign up/login with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose `stocks-alert` repository
6. Railway auto-detects Dockerfile ✅

### 3. Set Environment Variables

In Railway Dashboard → Variables, paste this and update values:

```env
DATABASE_URL=postgresql://postgres.kizbfvvpxwaabhzulaxe:YOUR_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=generate-with-openssl-rand-hex-32
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
PYTHONUNBUFFERED=1
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 4. Wait for Build & Deploy
- Takes 2-5 minutes first time
- Watch the logs for any errors

### 5. Get Your Railway URL
Railway gives you: `https://your-app-xxxxx.up.railway.app`

### 6. Test Your API
```bash
curl https://your-app-xxxxx.up.railway.app/
# Should return: {"message":"Welcome to the Stock Alert Application!"}

# Check API docs
open https://your-app-xxxxx.up.railway.app/docs
```

### 7. Update CORS (Important!)

Add your Railway URL to `app/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8082",
    "https://your-app-xxxxx.up.railway.app",  # Add this
],
```

Then commit and push:
```bash
git add app/main.py
git commit -m "Add Railway URL to CORS"
git push origin main
```

Railway will auto-redeploy! 🚀

### 8. Update Frontend

Update your frontend `.env`:
```env
VITE_API_URL=https://your-app-xxxxx.up.railway.app
```

## Verification Steps

✅ Check deployment logs - no errors  
✅ Access `/` endpoint - returns welcome message  
✅ Access `/docs` - Swagger UI loads  
✅ Test `/register` - creates user  
✅ Test `/login/json` - returns token  
✅ Check PSX scraper logs - scheduler started  
✅ Database migrations completed  

## Common Issues & Fixes

### ❌ Port binding error
**Solution:** Updated Dockerfile to use `${PORT:-8000}` ✅

### ❌ Chrome not found
**Solution:** Dockerfile installs chromium ✅

### ❌ Database connection timeout
**Solution:** Using Supabase pooler URL ✅

### ❌ Frontend CORS error
**Solution:** Add Railway domain to CORS allowed origins

## Monitoring

**View Logs:**
- Railway Dashboard → Your Project → Deployments → Logs

**Key things to watch:**
- Database connection successful
- PSX Scraper started
- No migration errors

## Cost

**Free Tier:**
- 500 execution hours/month
- Perfect for testing
- Sleeps after 30 min inactivity

**Paid Tier ($5-10/month):**
- No sleep
- Better for 24/7 scraping
- More resources

## Next Steps After Deployment

1. ✅ Backend deployed to Railway
2. 🎯 Deploy frontend (Vercel/Netlify/Railway)
3. 🎯 Update frontend VITE_API_URL
4. 🎯 Test complete user flow
5. 🎯 Monitor logs for first few days
6. 🎯 Set up custom domain (optional)

---

**That's it! Your backend is live! 🎉**

