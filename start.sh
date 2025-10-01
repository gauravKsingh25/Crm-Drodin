#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Set environment variables
export SITE_NAME=${RENDER_EXTERNAL_HOSTNAME:-localhost}

# Create site if it doesn't exist
if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Creating new site..."
    bench new-site $SITE_NAME \
        --admin-password ${ADMIN_PASSWORD:-admin} \
        --db-name ${DATABASE_URL##*/} \
        --install-app crm
else
    echo "Site already exists"
fi

# Start the application
exec bench start --no-dev-server