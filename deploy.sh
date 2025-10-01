#!/bin/bash

# 🚀 Frappe CRM Production Deployment Script
# This script helps you deploy Frappe CRM in production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check available memory (minimum 2GB)
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $mem_gb -lt 2 ]]; then
        warning "System has less than 2GB RAM. Consider upgrading for better performance."
    fi
    
    # Check available disk space (minimum 20GB)
    local disk_gb=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $disk_gb -lt 20 ]]; then
        warning "Less than 20GB disk space available. Consider freeing up space."
    fi
    
    success "System requirements check completed"
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        log "Creating .env file from template..."
        cp .env.example .env
        
        echo ""
        echo "🔧 Please edit the .env file with your configuration:"
        echo "   - DOMAIN_NAME: Your domain (e.g., crm.yourdomain.com)"
        echo "   - ACME_EMAIL: Your email for Let's Encrypt"
        echo "   - Database passwords (use strong passwords)"
        echo "   - Admin password for CRM"
        echo "   - Encryption key (32 characters)"
        echo ""
        echo "Example encryption key generation:"
        echo "   openssl rand -hex 16"
        echo ""
        read -p "Press Enter after editing the .env file to continue..."
        
        # Validate .env file
        if ! grep -q "DOMAIN_NAME=crm.yourdomain.com" .env; then
            success "Environment file appears to be configured"
        else
            error "Please edit the .env file with your actual values"
        fi
    else
        success "Environment file already exists"
    fi
}

# Setup directories
setup_directories() {
    log "Setting up directories and permissions..."
    
    # Create mysql directory if it doesn't exist
    mkdir -p mysql
    
    # Make scripts executable
    chmod +x production-init.sh
    
    success "Directories and permissions configured"
}

# Deploy application
deploy_application() {
    log "Deploying Frappe CRM..."
    
    # Pull latest images
    log "Pulling Docker images..."
    docker-compose -f docker-compose.production.yml pull
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.production.yml up -d
    
    success "Services started successfully"
}

# Monitor deployment
monitor_deployment() {
    log "Monitoring deployment progress..."
    
    echo "📊 Container Status:"
    docker-compose -f docker-compose.production.yml ps
    
    echo ""
    echo "📝 Following logs (Ctrl+C to exit):"
    echo "   You can also run: docker-compose -f docker-compose.production.yml logs -f"
    echo ""
    
    # Follow logs for a bit
    timeout 60 docker-compose -f docker-compose.production.yml logs -f frappe || true
    
    echo ""
    success "Deployment monitoring completed"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for services to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log "Health check attempt $attempt/$max_attempts..."
        
        if curl -f -s http://localhost:80/api/method/ping > /dev/null 2>&1; then
            success "Application is responding correctly!"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "Application failed to respond after $max_attempts attempts"
        fi
        
        sleep 10
        ((attempt++))
    done
}

# Show deployment info
show_deployment_info() {
    log "Deployment completed successfully! 🎉"
    
    echo ""
    echo "📋 Deployment Information:"
    echo "========================="
    
    # Get domain from .env
    local domain=$(grep DOMAIN_NAME .env | cut -d'=' -f2)
    
    echo "🌐 URL: https://$domain"
    echo "👤 Default Login: Administrator"
    echo "🔑 Password: $(grep ADMIN_PASSWORD .env | cut -d'=' -f2)"
    echo ""
    echo "📊 Management Commands:"
    echo "   View logs:     docker-compose -f docker-compose.production.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.production.yml down"
    echo "   Restart:       docker-compose -f docker-compose.production.yml restart"
    echo "   Update:        docker-compose -f docker-compose.production.yml pull && docker-compose -f docker-compose.production.yml up -d"
    echo ""
    echo "🔧 Backup Commands:"
    echo "   Create backup: docker-compose -f docker-compose.production.yml exec frappe bench --site $domain backup --with-files"
    echo "   List backups:  docker-compose -f docker-compose.production.yml exec frappe ls sites/$domain/private/backups/"
    echo ""
    echo "⚠️  Security Notes:"
    echo "   - SSL certificate will be automatically obtained from Let's Encrypt"
    echo "   - Change default passwords immediately after first login"
    echo "   - Regular backups are recommended"
    echo "   - Monitor logs for any issues"
    echo ""
    
    success "Frappe CRM is now running in production mode!"
}

# Main deployment function
main() {
    echo ""
    echo "🚀 Frappe CRM Production Deployment"
    echo "=================================="
    echo ""
    
    check_root
    check_requirements
    setup_environment
    setup_directories
    deploy_application
    monitor_deployment
    health_check
    show_deployment_info
}

# Script options
case "${1:-}" in
    --health-check)
        health_check
        ;;
    --logs)
        docker-compose -f docker-compose.production.yml logs -f
        ;;
    --stop)
        log "Stopping services..."
        docker-compose -f docker-compose.production.yml down
        success "Services stopped"
        ;;
    --restart)
        log "Restarting services..."
        docker-compose -f docker-compose.production.yml restart
        success "Services restarted"
        ;;
    --update)
        log "Updating application..."
        docker-compose -f docker-compose.production.yml pull
        docker-compose -f docker-compose.production.yml up -d
        success "Application updated"
        ;;
    --backup)
        log "Creating backup..."
        domain=$(grep DOMAIN_NAME .env | cut -d'=' -f2)
        docker-compose -f docker-compose.production.yml exec frappe bench --site $domain backup --with-files
        success "Backup created"
        ;;
    --help)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no args)      Run full deployment"
        echo "  --health-check Health check only"
        echo "  --logs         View logs"
        echo "  --stop         Stop services"
        echo "  --restart      Restart services"
        echo "  --update       Update application"
        echo "  --backup       Create backup"
        echo "  --help         Show this help"
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1. Use --help for usage information."
        ;;
esac