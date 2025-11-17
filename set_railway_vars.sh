#!/bin/bash
# Script to set Railway environment variables
# Usage: ./set_railway_vars.sh

echo "🚂 Setting Railway Environment Variables..."
echo "⚠️  Make sure you've run 'railway login' and 'railway init' first!"
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Database
echo "Setting DATABASE_URL..."
railway variables set DATABASE_URL="postgresql://postgres.kizbfvvpxwaabhzulaxe:YOUR_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

# Generate or use existing SECRET_KEY
echo "Setting SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
railway variables set SECRET_KEY="$SECRET_KEY"
echo "Generated SECRET_KEY: $SECRET_KEY"

# Email
echo "Setting Email configuration..."
railway variables set MAIL_USERNAME="your-email@gmail.com"
railway variables set MAIL_PASSWORD="your-app-password"
railway variables set MAIL_FROM="your-email@gmail.com"
railway variables set MAIL_SERVER="smtp.gmail.com"
railway variables set MAIL_PORT="587"
railway variables set MAIL_STARTTLS="True"

# Twilio
echo "Setting Twilio configuration..."
railway variables set TWILIO_ACCOUNT_SID="your-twilio-sid"
railway variables set TWILIO_AUTH_TOKEN="your-twilio-token"
railway variables set TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"

# Chrome (already in Dockerfile, but setting for completeness)
railway variables set CHROME_BIN="/usr/bin/chromium"
railway variables set CHROMEDRIVER_PATH="/usr/bin/chromedriver"
railway variables set PYTHONUNBUFFERED="1"

echo ""
echo "✅ Environment variables set!"
echo ""
echo "⚠️  IMPORTANT: Update the following with your actual values:"
echo "   - DATABASE_URL (Replace YOUR_PASSWORD)"
echo "   - MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM"
echo "   - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"
echo ""
echo "Run 'railway variables' to view all variables"

