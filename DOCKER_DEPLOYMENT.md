# 🐳 Docker Deployment Guide for Stock Alert App

This guide will help you deploy your Stock Alert application using Docker, both locally and on various cloud platforms.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development with Docker](#local-development-with-docker)
3. [Deploy to Fly.io (FREE)](#deploy-to-flyio-free)
4. [Deploy to Render.com (FREE)](#deploy-to-rendercom-free)
5. [Deploy to Railway (Paid)](#deploy-to-railway-paid)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Install Docker
- **macOS**: Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- **Windows**: Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- **Linux**: 
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

Verify installation:
```bash
docker --version
docker-compose --version
```

---

## 🏠 Local Development with Docker

### Step 1: Set Up Environment Variables

Copy the example env file and fill in your credentials:
```bash
cp env.example .env
```

Edit `.env` with your actual values:
```env
# Email credentials (Gmail example)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_FROM=your-email@gmail.com

# Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)
```

### Step 2: Build and Run with Docker Compose

```bash
# Build the Docker image
docker-compose build

# Start all services (backend + database)
docker-compose up
```

Your application will be available at:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Step 3: Run Database Migrations

In a new terminal:
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Or if container is not running yet
docker-compose run backend alembic upgrade head
```

### Step 4: Check Logs

```bash
# View logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f db
```

### Step 5: Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🚀 Deploy to Fly.io (FREE)

Fly.io offers a generous free tier perfect for your app.

### Step 1: Install Fly CLI

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Verify installation
fly version
```

### Step 2: Login to Fly.io

```bash
fly auth login
```

### Step 3: Create Fly.io Configuration

Create `fly.toml` in your project root:

```toml
app = "stocks-alert-app"
primary_region = "sin"  # Singapore - closest to Pakistan

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  PYTHONUNBUFFERED = "1"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Step 4: Create PostgreSQL Database

```bash
# Create a Postgres cluster
fly postgres create --name stocks-alert-db --region sin

# Attach database to your app
fly postgres attach stocks-alert-db
```

### Step 5: Set Environment Variables

```bash
# Set all required environment variables
fly secrets set MAIL_USERNAME="your-email@gmail.com"
fly secrets set MAIL_PASSWORD="your-app-password"
fly secrets set MAIL_FROM="your-email@gmail.com"
fly secrets set MAIL_SERVER="smtp.gmail.com"
fly secrets set MAIL_PORT="587"
fly secrets set MAIL_STARTTLS="True"
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
fly secrets set TWILIO_ACCOUNT_SID="your-sid"
fly secrets set TWILIO_AUTH_TOKEN="your-token"
fly secrets set TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
fly secrets set CHROME_BIN="/usr/bin/chromium"
fly secrets set CHROMEDRIVER_PATH="/usr/bin/chromedriver"
```

### Step 6: Deploy!

```bash
# Initialize and deploy
fly launch

# Or if already initialized
fly deploy

# Open your app
fly open
```

### Step 7: Monitor Your App

```bash
# View logs
fly logs

# Check status
fly status

# SSH into your container
fly ssh console
```

### Fly.io Costs
- **FREE TIER**: 3 shared-cpu VMs, 3GB storage
- Your app should fit comfortably in free tier!

---

## 🎨 Deploy to Render.com (FREE)

Render offers a free tier with some limitations but works great for your app.

### Step 1: Push Code to GitHub

Make sure your code is in a GitHub repository.

### Step 2: Create Render Account

Go to [render.com](https://render.com) and sign up.

### Step 3: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `stocks-alert-db`
3. Select **Free** tier
4. Click "Create Database"
5. Copy the **Internal Database URL**

### Step 4: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `stocks-alert`
   - **Region**: Singapore (closest to Pakistan)
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Instance Type**: Free

### Step 5: Set Environment Variables

In the web service settings, add:

```
DATABASE_URL=<your-internal-database-url>
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
SECRET_KEY=<generate-secure-key>
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### Step 6: Deploy

Click "Create Web Service" and Render will automatically deploy!

### Render.com Limitations (Free Tier)
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ Database expires after 90 days
- ✅ 750 hours/month free
- ✅ Perfect for your trading hours schedule!

**Workaround for Sleep**: Use [cron-job.org](https://cron-job.org) (free) to ping your health endpoint at 9:15 AM Pakistan time to wake it up before trading starts.

---

## 🚂 Deploy to Railway (Paid - ~$5/month)

Railway is super easy but requires payment.

### Step 1: Install Railway CLI

```bash
# macOS/Linux
npm install -g @railway/cli

# Or use brew
brew install railway
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
railway init
```

### Step 4: Add PostgreSQL

```bash
railway add --plugin postgresql
```

### Step 5: Set Environment Variables

```bash
railway variables set MAIL_USERNAME="your-email@gmail.com"
railway variables set MAIL_PASSWORD="your-app-password"
# ... set all other variables
```

### Step 6: Deploy

```bash
railway up
```

Railway automatically detects your Dockerfile and deploys!

---

## 🛠️ Troubleshooting

### Issue: Chrome/Selenium Not Working in Docker

**Solution**: Make sure you have these Chrome arguments in `psx_scrapper.py`:
```python
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
```

### Issue: Database Connection Failed

**Solution**: 
1. Check `DATABASE_URL` environment variable
2. Make sure PostgreSQL is running
3. Verify connection string format:
   ```
   postgresql://user:password@host:port/database
   ```

### Issue: Container Crashes on Startup

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Or on Fly.io
fly logs

# Common causes:
# - Missing environment variables
# - Database not ready (needs migration)
# - Port already in use locally
```

### Issue: Scraper Not Running

**Solution**:
1. Check if it's trading hours (9:20 AM - 4:40 PM Pakistan time)
2. Verify `is_trading_hours()` function in `psx_scrapper.py`
3. Check logs for scraper messages

### Issue: Build Takes Too Long

**Solution**:
```bash
# Use build cache
docker-compose build --no-cache

# Or for Fly.io
fly deploy --no-cache
```

---

## 📱 Frontend Deployment (Vue.js)

Your Vue.js frontend should be deployed separately.

### Option 1: Vercel (FREE, Recommended)

```bash
cd frontend
npm install -g vercel
vercel
```

### Option 2: Netlify (FREE)

```bash
cd frontend
npm install -g netlify-cli
netlify deploy
```

### Update CORS in Backend

Don't forget to update `app/main.py` with your frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend.vercel.app"  # Add your deployed URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 Recommended Stack (100% FREE)

```
Backend + Scraper:  Fly.io (Free tier)
Database:           Fly.io Postgres (Free tier)
Frontend:           Vercel (Free tier)
Monitoring:         UptimeRobot (Free)
```

**Total Monthly Cost: $0** 🎉

---

## 📊 Quick Command Reference

```bash
# Local Development
docker-compose up -d              # Start in background
docker-compose down               # Stop services
docker-compose logs -f backend    # View logs
docker-compose exec backend bash  # Shell into container

# Fly.io
fly deploy                        # Deploy
fly logs                          # View logs
fly ssh console                   # SSH into container
fly scale count 1                 # Scale to 1 instance

# Database Migrations
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic revision --autogenerate -m "message"
```

---

## 🆘 Need Help?

- **Docker Issues**: Check [Docker documentation](https://docs.docker.com)
- **Fly.io Issues**: Check [Fly.io documentation](https://fly.io/docs)
- **Selenium Issues**: Check container logs for Chrome errors

---

Good luck with your deployment! 🚀

