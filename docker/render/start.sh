#!/bin/bash
set -e

echo "Starting Frappe CRM Web Server..."

# Configure site
./configure-site.sh

# Start web server
echo "Starting Gunicorn web server..."
exec bench start --no-dev-server