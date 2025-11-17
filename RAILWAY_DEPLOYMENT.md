# 🚂 Railway Deployment Guide

Deploy your Stock Alert backend to Railway using Docker.

## Prerequisites

- Railway account (free tier available)
- GitHub repository with your code
- Supabase database already set up

## Step 1: Prepare Your Repository

1. Make sure all changes are committed and pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Step 2: Update Dockerfile for Production

Your current Dockerfile is already production-ready! It includes:
- ✅ Chrome/Chromium for PSX scraper
- ✅ Python dependencies
- ✅ Alembic migrations
- ✅ Uvicorn server

The Dockerfile will automatically run migrations on startup.

## Step 3: Create Railway Project

### Option A: Deploy via Railway Dashboard

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `stocks-alert` repository
5. Railway will detect the Dockerfile automatically

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Step 4: Configure Environment Variables

In Railway Dashboard → Your Project → Variables, add:

```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres.kizbfvvpxwaabhzulaxe:YOUR_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# JWT Secret (generate a secure random key)
SECRET_KEY=your-secure-secret-key-change-this

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Chrome/Selenium (already set in Dockerfile, but can override)
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Python
PYTHONUNBUFFERED=1
```

### Generate SECRET_KEY:
```bash
openssl rand -hex 32
```

## Step 5: Update CORS for Production

After deployment, Railway will give you a URL like: `https://your-app.railway.app`

You need to update CORS in `app/main.py`:

```python
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8082",
        "https://your-app.railway.app",  # Add your Railway domain
        "https://your-frontend-domain.com",  # Add your frontend domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

## Step 6: Check Deployment

After deployment completes:

1. **Check Logs:**
   ```
   Railway Dashboard → Your Project → Deployments → View Logs
   ```

2. **Test Your API:**
   ```bash
   curl https://your-app.railway.app/
   # Should return: {"message":"Welcome to the Stock Alert Application!"}
   ```

3. **Check API Documentation:**
   ```
   https://your-app.railway.app/docs
   ```

## Step 7: Database Migrations

Migrations run automatically on startup (configured in Dockerfile CMD).

Check logs to verify:
```
INFO  [alembic.runtime.migration] Running upgrade -> ec1551aec86f
✅ Database initialized successfully!
```

## Railway Configuration Tips

### 1. Health Check (Optional)

Railway can monitor your app's health. Add this to `railway.toml` (create in root):

```toml
[deploy]
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 2. Resource Allocation

Free tier limits:
- 500 MB RAM
- 500 hours/month
- Shared CPU

For production, consider upgrading to:
- 1GB+ RAM (for Chrome/Selenium)
- More CPU for better scraping performance

### 3. Custom Domain (Optional)

Railway Dashboard → Your Project → Settings → Domain
- Add custom domain
- Update CORS accordingly

## Frontend Connection

Update your frontend `.env` to point to Railway:

```bash
VITE_API_URL=https://your-app.railway.app
```

Then rebuild and deploy your frontend.

## Monitoring & Logs

### View Logs:
```bash
# Via CLI
railway logs

# Via Dashboard
Dashboard → Your Project → Deployments → View Logs
```

### Key Things to Monitor:
- PSX Scraper running during trading hours
- Database connection health
- Alert evaluations
- Email sending

## Troubleshooting

### Issue: Chrome/Selenium Not Working

**Check logs for:**
```
selenium.common.exceptions.WebDriverException
```

**Solution:** Your Dockerfile already installs Chromium. If issues persist:
1. Check logs for Chrome binary location
2. Verify CHROME_BIN and CHROMEDRIVER_PATH env vars

### Issue: Database Connection Timeout

**Error:** `connection timeout` or `pool timeout`

**Solution:**
1. Verify DATABASE_URL is correct
2. Check Supabase connection pooler is used (not direct connection)
3. Increase timeout in `database.py` if needed

### Issue: Migrations Failing

**Check logs for migration errors.**

**Solution:**
1. If tables already exist, migrations might fail
2. SSH into Railway container (if needed) and run:
   ```bash
   railway run alembic stamp head
   ```

### Issue: Port Binding

Railway automatically sets `PORT` environment variable.

If app doesn't start, update `Dockerfile` CMD:
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

## Cost Estimation

### Free Tier:
- ✅ Perfect for testing
- ✅ 500 hours/month (20+ days)
- ✅ Sleeps after inactivity

### Paid Tier (~$5-10/month):
- ✅ No sleep
- ✅ Better resources for Chrome
- ✅ Custom domain
- ✅ More hours

## Deployment Checklist

Before going live:

- [ ] All environment variables configured
- [ ] SECRET_KEY is secure (not default)
- [ ] Database migrations tested
- [ ] CORS includes production domains
- [ ] Email/Twilio credentials tested
- [ ] PSX scraper tested during market hours
- [ ] Health check endpoint working (`/`)
- [ ] API docs accessible at `/docs`

## Alternative: GitHub Auto-Deploy

Once set up, every push to `main` branch will auto-deploy:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway automatically detects and deploys!
```

## Backup Strategy

Your data is in Supabase, so:
- ✅ Database is already backed up by Supabase
- ✅ No data stored in Railway container
- ✅ Stateless backend = easy to redeploy

## Next Steps

1. Deploy backend to Railway
2. Test all endpoints
3. Update frontend to use Railway URL
4. Deploy frontend (Vercel, Netlify, or Railway)
5. Monitor logs for the first few days
6. Set up Supabase backups

## Support

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** For quick help
- **Check logs first:** Most issues are visible in logs

---

**Good luck with your deployment! 🚀**

