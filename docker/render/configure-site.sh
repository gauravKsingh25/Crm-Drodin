#!/bin/bash
set -e

echo "Starting Frappe CRM configuration..."

# Wait for database to be ready
echo "Waiting for database connection..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done

echo "Database is ready!"

# Set database configuration
bench set-config -g db_type postgres
bench set-config -g db_host $DB_HOST
bench set-config -g db_port $DB_PORT

# Configure Redis
bench set-config -g redis_cache $REDIS_CACHE_URL
bench set-config -g redis_queue $REDIS_QUEUE_URL  
bench set-config -g redis_socketio $REDIS_SOCKETIO_URL

# Create site if it doesn't exist
if [ ! -d "sites/$FRAPPE_SITE_NAME" ]; then
    echo "Creating new site: $FRAPPE_SITE_NAME"
    bench new-site $FRAPPE_SITE_NAME \
        --db-type postgres \
        --db-host $DB_HOST \
        --db-port $DB_PORT \
        --db-name $DB_NAME \
        --db-user $DB_USER \
        --db-password $DB_PASSWORD \
        --admin-password $ADMIN_PASSWORD \
        --no-mariadb-socket
        
    echo "Installing CRM app on site..."
    bench --site $FRAPPE_SITE_NAME install-app crm
else
    echo "Site $FRAPPE_SITE_NAME already exists"
fi

# Set current site
echo $FRAPPE_SITE_NAME > sites/currentsite.txt

# Migrate database
echo "Running database migrations..."
bench --site $FRAPPE_SITE_NAME migrate

# Build assets
echo "Building assets..."
bench --site $FRAPPE_SITE_NAME build --production

echo "Site configuration completed!"