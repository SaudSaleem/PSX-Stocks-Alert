#!/bin/bash

# Stocks Alert - Firebase Deployment Script

echo "🚀 Starting Stocks Alert deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Check if firebase-tools is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Error: Firebase CLI not found!"
    echo "Installing Firebase CLI..."
    npm install -g firebase-tools
fi

# Build the project
echo "📦 Building production bundle..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed! No dist directory found."
    exit 1
fi

echo "✅ Build successful!"

# Deploy to Firebase
echo "☁️  Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo "🎉 Deployment complete!"
echo "Your app should be live at your Firebase hosting URL" 