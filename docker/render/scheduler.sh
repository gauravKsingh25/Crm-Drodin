#!/bin/bash
set -e

echo "Starting Frappe CRM Scheduler..."

# Wait for main site to be configured
sleep 45

# Set current site  
echo $FRAPPE_SITE_NAME > sites/currentsite.txt

# Start scheduler
echo "Starting scheduler..."
exec bench schedule