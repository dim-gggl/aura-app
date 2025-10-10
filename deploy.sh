#!/bin/bash
# Deployment script for Aura Art

set -e

echo "🚀 Starting Aura Art deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.example"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY is not set in .env file"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ POSTGRES_PASSWORD is not set in .env file"
    exit 1
fi

echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🗄️ Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🔍 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deployment completed!"
echo "🌐 Application should be available at: https://aura-art.org"
echo "📊 Health check: https://aura-art.org/health/"

# Show logs
echo "📋 Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20
