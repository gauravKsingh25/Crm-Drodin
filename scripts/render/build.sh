#!/bin/bash
set -e

echo "Building Frappe CRM for Render deployment..."

# Install Python dependencies
pip install --user -e .

# Build frontend
cd frontend
npm ci
npm run build
cd ..

echo "Build completed successfully!"