# 🚀 Complete Deployment Strategy

## Recommended Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   (Vercel)      │────────▶│   (Railway)     │
│   Vue 3 + Vite  │  HTTPS  │   FastAPI       │
│   Static Files  │         │   + Chrome      │
└─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │    Database     │
                            │   (Supabase)    │
                            │   PostgreSQL    │
                            └─────────────────┘
```

## Why This Setup?

### Backend on Railway ✅
- **Needs:** Docker for Chrome/Chromium (PSX scraper)
- **Cost:** ~$5-10/month (or free tier for testing)
- **Perfect for:** Python + Docker + scheduled tasks

### Frontend on Vercel/Netlify ✅
- **Needs:** Just static file hosting + CDN
- **Cost:** FREE (generous free tier)
- **Perfect for:** Vue/React/Static sites

### Database on Supabase ✅
- **Already set up!**
- **Cost:** FREE tier is generous
- **Benefits:** Managed, backed up, scalable

---

## Part 1: Deploy Backend to Railway

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Deploy Backend

```bash
cd /Users/saudsaleem/Documents/stocks-alert

# Login
railway login

# Initialize project (links your directory to Railway)
railway init

# Deploy (builds Docker image and deploys)
railway up
```

### Step 3: Set Environment Variables

**Option A: Use Dashboard (Easier)**
1. Go to https://railway.app/dashboard
2. Select your project
3. Go to Variables tab
4. Add all variables from your `.env` file

**Option B: Use CLI Script (Faster)**
```bash
# Edit the script first with your actual values
nano set_railway_vars.sh

# Run the script
./set_railway_vars.sh
```

**Option C: Manual CLI (Most Control)**
```bash
railway variables set DATABASE_URL="your-supabase-url"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set MAIL_USERNAME="your-email@gmail.com"
# ... etc
```

### Step 4: Get Your Backend URL

After deployment:
```bash
railway domain
```

Output: `https://stocks-alert-production-xxxx.up.railway.app`

### Step 5: Test Backend

```bash
curl https://your-backend-url.railway.app/
# Should return: {"message":"Welcome to the Stock Alert Application!"}

# Check API docs
open https://your-backend-url.railway.app/docs
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend

Update `frontend/.env.production`:

```bash
cd frontend
cat > .env.production << EOF
VITE_API_URL=https://your-backend-url.railway.app
EOF
```

### Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 3: Deploy Frontend

```bash
cd frontend

# Login to Vercel
vercel login

# Deploy (first time will ask questions)
vercel

# Or deploy to production directly
vercel --prod
```

**Vercel will ask:**
- Project name: `stocks-alert-frontend`
- Framework: Detected automatically (Vite)
- Build command: `npm run build`
- Output directory: `dist`

### Step 4: Set Environment Variable on Vercel

```bash
# Set via CLI
vercel env add VITE_API_URL

# Or via Vercel Dashboard
# Settings → Environment Variables → Add
# Name: VITE_API_URL
# Value: https://your-backend-url.railway.app
```

### Step 5: Redeploy with Env Var

```bash
vercel --prod
```

Your frontend URL: `https://stocks-alert-frontend.vercel.app`

---

## Part 3: Update CORS on Backend

Your backend needs to allow requests from your Vercel frontend.

### Update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8082",
        "https://your-backend-url.railway.app",
        "https://stocks-alert-frontend.vercel.app",  # Add this!
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

### Commit and Push:

```bash
git add app/main.py
git commit -m "Add Vercel frontend to CORS"
git push origin main

# Railway auto-deploys on push!
```

---

## Alternative: Deploy Frontend to Netlify

If you prefer Netlify over Vercel:

```bash
cd frontend

# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy

# Deploy to production
netlify deploy --prod
```

**Set environment variable:**
```bash
netlify env:set VITE_API_URL https://your-backend-url.railway.app
```

---

## Deployment Comparison

| Platform | Best For | Free Tier | Deploy Time |
|----------|----------|-----------|-------------|
| **Railway** | Backend (Docker) | 500 hrs/month | 3-5 min |
| **Vercel** | Frontend (Vue/React) | Unlimited | 30 sec |
| **Netlify** | Frontend (Static) | 100 GB/month | 1 min |
| **Supabase** | PostgreSQL Database | 500 MB | Instant |

---

## Complete Deployment Commands

### Backend (Railway)
```bash
# One-time setup
npm install -g @railway/cli
railway login
railway init

# Deploy
railway up

# Set variables (use dashboard or script)
./set_railway_vars.sh

# View logs
railway logs
```

### Frontend (Vercel)
```bash
# One-time setup
npm install -g vercel
cd frontend
vercel login

# Deploy to production
vercel --prod

# Set env var
vercel env add VITE_API_URL
# Enter: https://your-backend-url.railway.app

# Redeploy with new env
vercel --prod
```

---

## Environment Variables Checklist

### ❌ NOT Transferred Automatically
Your local `.env` file is **NOT uploaded** to Railway/Vercel.

### ✅ You Must Set Manually

**Backend (Railway):**
- DATABASE_URL
- SECRET_KEY
- MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_SERVER, MAIL_PORT, MAIL_STARTTLS
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM
- CHROME_BIN, CHROMEDRIVER_PATH, PYTHONUNBUFFERED

**Frontend (Vercel/Netlify):**
- VITE_API_URL (your Railway backend URL)

---

## Post-Deployment Testing

### 1. Test Backend
```bash
# Health check
curl https://your-backend.railway.app/

# Register user
curl -X POST https://your-backend.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### 2. Test Frontend
- Open `https://your-frontend.vercel.app`
- Try to register
- Try to login
- Create an alert
- Check browser console for CORS errors

### 3. Check Logs
```bash
# Backend logs
railway logs

# Frontend logs (if issues)
vercel logs
```

---

## Automatic Deployments

### Backend (Railway)
✅ **Auto-deploys on every push to `main` branch**

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway automatically deploys!
```

### Frontend (Vercel)
✅ **Auto-deploys on every push to `main` branch**

```bash
cd frontend
git add .
git commit -m "Update UI"
git push origin main
# Vercel automatically deploys!
```

---

## Cost Breakdown

### Free Tier (Perfect for Starting)

| Service | Free Tier | Cost if Exceed |
|---------|-----------|----------------|
| Railway | 500 hrs/month | $5/month (Hobby) |
| Vercel | Unlimited deploys | $20/month (Pro) |
| Supabase | 500 MB DB | $25/month (Pro) |
| **Total** | **FREE** | ~$50/month if needed |

### Recommended Starting Plan

✅ **Use free tiers** for all three services  
✅ **Monitor usage** for first month  
✅ **Upgrade Railway** first (~$5/month for 24/7 uptime)  
✅ **Frontend stays free** (Vercel/Netlify generous free tier)

---

## Monitoring & Maintenance

### Backend (Railway)
```bash
# View logs in real-time
railway logs --follow

# Check deployments
railway status

# SSH into container (if needed)
railway run bash
```

### Frontend (Vercel)
- Dashboard shows deployment status
- Analytics (free tier)
- Logs for each deployment

### Database (Supabase)
- Dashboard shows connection stats
- Query performance
- Storage usage

---

## Summary: Your Deployment Strategy

1. ✅ **Backend on Railway** (Docker + Chrome needed)
2. ✅ **Frontend on Vercel/Netlify** (Free + Fast + CDN)
3. ✅ **Database on Supabase** (Already set up)
4. ✅ **Environment variables set manually** (via dashboard or CLI)
5. ✅ **Auto-deploy on push** (both platforms)

This gives you the best of all worlds: cost-effective, performant, and easy to manage! 🚀

