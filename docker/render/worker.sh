#!/bin/bash
set -e

echo "Starting Frappe CRM Background Worker..."

# Wait for main site to be configured
sleep 30

# Set current site
echo $FRAPPE_SITE_NAME > sites/currentsite.txt

# Start worker
echo "Starting background worker..."
exec bench worker --queue default,long,short