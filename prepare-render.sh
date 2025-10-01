#!/bin/bash
# Render deployment preparation script

set -e

echo "🚀 Preparing Frappe CRM for Render deployment..."

# Install frontend dependencies
cd frontend
echo "📦 Installing frontend dependencies..."
npm ci

# Build frontend
echo "🏗️ Building frontend assets..."
npm run build

echo "✅ Frontend build completed"

# Go back to root
cd ..

# Prepare for Docker build
echo "🐳 Preparing Docker environment..."

# Create production site config template
cat > render-site-config.json << EOF
{
  "db_host": "\${DB_HOST}",
  "db_port": \${DB_PORT},
  "db_name": "\${DB_NAME}",
  "db_user": "\${DB_USER}", 
  "db_password": "\${DB_PASSWORD}",
  "redis_cache": "\${REDIS_CACHE}",
  "redis_queue": "\${REDIS_QUEUE}",
  "redis_socketio": "\${REDIS_SOCKETIO}",
  "developer_mode": 0,
  "allow_tests": 0,
  "auto_update": 0,
  "serve_default_site": 1,
  "encryption_key": "\${ENCRYPTION_KEY}"
}
EOF

echo "✅ Render deployment preparation completed!"
echo ""
echo "Next steps:"
echo "1. Commit and push to GitHub"
echo "2. Deploy on Render using the render.yaml configuration"
echo "3. Set environment variables in Render dashboard"