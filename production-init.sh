#!/bin/bash

# Production initialization script for Frappe CRM
# This script runs inside the container to set up production configuration

set -e

echo "🚀 Starting Frappe CRM Production Setup..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! mysqladmin ping -h mariadb --silent; do
    sleep 2
done
echo "✅ Database is ready"

# Wait for Redis to be ready  
echo "⏳ Waiting for Redis connection..."
while ! redis-cli -h redis ping | grep -q PONG; do
    sleep 2
done
echo "✅ Redis is ready"

# Navigate to bench directory
cd /home/frappe/frappe-bench

# Check if site already exists
if [ -d "sites/${SITE_NAME}" ]; then
    echo "📍 Site ${SITE_NAME} already exists, starting services..."
    
    # Ensure site is set as current site
    echo "${SITE_NAME}" > sites/currentsite.txt
    
    # Update configuration if needed
    bench --site ${SITE_NAME} set-config db_host mariadb
    bench --site ${SITE_NAME} set-config redis_cache "redis://redis:6379/0"
    bench --site ${SITE_NAME} set-config redis_queue "redis://redis:6379/1" 
    bench --site ${SITE_NAME} set-config redis_socketio "redis://redis:6379/2"
    
    # Ensure production settings
    bench --site ${SITE_NAME} set-config developer_mode 0
    bench --site ${SITE_NAME} set-config mute_emails 0
    bench --site ${SITE_NAME} set-config disable_website_cache 0
    
    # Clear cache and build assets
    bench --site ${SITE_NAME} clear-cache
    bench build --app crm
    
else
    echo "🔧 Creating new site ${SITE_NAME}..."
    
    # Create new site
    bench new-site ${SITE_NAME} \
        --force \
        --mariadb-root-password ${DB_ROOT_PASSWORD} \
        --admin-password ${ADMIN_PASSWORD} \
        --db-name ${DB_NAME} \
        --db-user ${DB_USER} \
        --db-password ${DB_PASSWORD}
    
    # Set as current site
    echo "${SITE_NAME}" > sites/currentsite.txt
    
    # Install CRM app
    echo "📦 Installing CRM application..."
    bench --site ${SITE_NAME} install-app crm
    
    # Production configuration
    bench --site ${SITE_NAME} set-config developer_mode 0
    bench --site ${SITE_NAME} set-config mute_emails 0
    bench --site ${SITE_NAME} set-config disable_website_cache 0
    bench --site ${SITE_NAME} set-config encryption_key ${ENCRYPTION_KEY}
    
    # Enable scheduler
    bench --site ${SITE_NAME} enable-scheduler
    
    # Build assets
    bench build --app crm
    
    echo "✅ Site setup completed successfully!"
fi

# Start the application
echo "🎯 Starting Frappe CRM..."
exec bench start