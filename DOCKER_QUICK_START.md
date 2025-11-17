# 🚀 Docker Quick Start Guide

Get your Stock Alert app running with Docker in under 5 minutes!

## Prerequisites

- Docker and Docker Compose installed ([Install Docker](https://docs.docker.com/get-docker/))
- Your environment variables ready

## Step 1: Set Up Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your actual credentials
nano .env  # or use any text editor
```

**Required variables to change:**
- `DATABASE_URL` - Your Supabase connection string (see SUPABASE_MIGRATION.md)
- `MAIL_USERNAME` - Your email
- `MAIL_PASSWORD` - Your email app password
- `MAIL_FROM` - Your email
- `TWILIO_ACCOUNT_SID` - Your Twilio SID
- `TWILIO_AUTH_TOKEN` - Your Twilio auth token
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

## Step 2: Build and Run

```bash
# Build the Docker images
docker-compose build

# Start the services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

## Step 3: Verify It's Working

Open your browser:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

Check logs:
```bash
docker-compose logs -f backend
```

You should see:
```
PSX Scraper scheduler started
...
```

## Step 4: Test the Scraper

The scraper only runs during Pakistan trading hours (9:20 AM - 4:40 PM, Mon-Fri).

To test immediately, you can temporarily modify `app/psx_scrapper.py`:

```python
def is_trading_hours():
    # Temporarily return True for testing
    return True
```

Then restart:
```bash
docker-compose restart backend
```

## Common Commands

```bash
# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Restart after code changes
docker-compose restart backend

# Shell into backend container
docker-compose exec backend bash

# Stop and remove everything (clean slate)
docker-compose down -v
```

## Troubleshooting

### Container won't start?
```bash
# Check logs for errors
docker-compose logs backend

# Common issue: Port 8000 already in use
# Change port in docker-compose.yml: "8001:8000"
```

### Database connection error?
```bash
# Verify your DATABASE_URL is correct in .env file
# Make sure you replaced [YOUR_PASSWORD] with your actual Supabase password
# Check Supabase dashboard to ensure your database is active

# Restart backend after fixing .env
docker-compose restart backend
```

### Chrome/Selenium not working?
```bash
# Check if Chrome is installed in container
docker-compose exec backend which chromium

# Should output: /usr/bin/chromium
```

## Next Steps

- ✅ Test your API endpoints at http://localhost:8000/docs
- ✅ Deploy to production (see `DOCKER_DEPLOYMENT.md`)
- ✅ Set up your frontend to connect to the backend

---

**Need detailed deployment instructions?** See `DOCKER_DEPLOYMENT.md`

**Questions?** Check the main `README.md`

