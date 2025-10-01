# 🚀 Frappe CRM Deployment Guide

## Deployment Options Overview

1. **Frappe Cloud (Managed Hosting)** - Easiest, production-ready
2. **Self-Hosted Production** - Full control, custom domain
3. **Docker Production** - Containerized deployment
4. **Traditional VPS/Server** - Manual setup on Linux server
5. **Local Development** - For testing and development

---

## 🌟 Option 1: Frappe Cloud (Recommended for Production)

**Best for**: Business use, hassle-free deployment, automatic updates

### Steps:
1. Visit [Frappe Cloud CRM Signup](https://frappecloud.com/crm/signup)
2. Create an account
3. Choose your plan (Free tier available)
4. Your CRM will be ready in minutes at `yoursite.frappecloud.com`

**Benefits**:
- ✅ SSL certificate included
- ✅ Automatic backups
- ✅ 99.9% uptime SLA
- ✅ No server maintenance
- ✅ Automatic updates

---

## 🐳 Option 2: Docker Production Deployment

**Best for**: Self-hosting with containers, scalable infrastructure

### Prerequisites:
- Docker and Docker Compose installed
- Domain name pointing to your server
- Server with at least 2GB RAM

### Production Docker Setup:

#### Step 1: Create Production Docker Compose
```yaml
# docker-compose.prod.yml
version: "3.8"
name: crm-prod

services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@domain.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - crm_network

  mariadb:
    image: mariadb:10.8
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --skip-character-set-client-handshake
      - --skip-innodb-read-only-compressed
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: crm_prod
      MYSQL_USER: crm_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - crm_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - crm_network
    restart: unless-stopped

  frappe:
    image: ghcr.io/frappe/crm:latest
    environment:
      - DB_HOST=mariadb
      - DB_PORT=3306
      - REDIS_CACHE=redis://redis:6379/0
      - REDIS_QUEUE=redis://redis:6379/1
      - REDIS_SOCKETIO=redis://redis:6379/2
      - SITE_NAME=${DOMAIN_NAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    volumes:
      - frappe_data:/home/frappe/frappe-bench/sites
      - frappe_logs:/home/frappe/frappe-bench/logs
    networks:
      - crm_network
    depends_on:
      - mariadb
      - redis
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.crm.rule=Host(`${DOMAIN_NAME}`)"
      - "traefik.http.routers.crm.entrypoints=websecure"
      - "traefik.http.routers.crm.tls.certresolver=myresolver"
      - "traefik.http.services.crm.loadbalancer.server.port=8000"

volumes:
  mariadb_data:
  redis_data:
  frappe_data:
  frappe_logs:

networks:
  crm_network:
    driver: bridge
```

#### Step 2: Environment Configuration
```bash
# .env
DOMAIN_NAME=crm.yourdomain.com
DB_ROOT_PASSWORD=secure_root_password_here
DB_PASSWORD=secure_db_password_here
ADMIN_PASSWORD=secure_admin_password_here
```

#### Step 3: Deploy
```bash
# Create directories
mkdir -p crm-production
cd crm-production

# Create the files above
nano docker-compose.prod.yml
nano .env

# Start the stack
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🖥️ Option 3: VPS/Server Deployment (Ubuntu)

**Best for**: Full control, custom configurations

### Prerequisites:
- Ubuntu 20.04+ server
- 2GB+ RAM, 20GB+ storage
- Domain name pointing to server IP

### Installation Script:
```bash
#!/bin/bash
# save as deploy-crm.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget nginx python3 python3-pip nodejs npm git

# Install Frappe Bench
pip3 install frappe-bench

# Create bench user
sudo adduser --disabled-password --gecos "" frappe
sudo usermod -aG sudo frappe
su - frappe

# Create bench
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# Configure production settings
bench set-config -g db_host localhost
bench set-config -g redis_cache redis://localhost:6379
bench set-config -g redis_queue redis://localhost:6379
bench set-config -g redis_socketio redis://localhost:6379

# Install CRM
bench get-app crm https://github.com/frappe/crm.git
bench new-site yourdomain.com --admin-password admin123 --db-root-password root123
bench --site yourdomain.com install-app crm

# Setup production
sudo bench setup production frappe
sudo bench setup nginx
sudo bench setup supervisor
sudo supervisorctl reload

# SSL Certificate
sudo snap install --classic certbot
sudo certbot --nginx -d yourdomain.com

# Start services
sudo service nginx restart
sudo supervisorctl restart all
```

### Run Deployment:
```bash
chmod +x deploy-crm.sh
./deploy-crm.sh
```

---

## ☁️ Option 4: Cloud Platforms

### AWS ECS Deployment
```bash
# Use the official easy install script
wget https://frappe.io/easy-install.py

python3 ./easy-install.py deploy \
    --project=crm_production \
    --email=your-email@domain.com \
    --image=ghcr.io/frappe/crm \
    --version=stable \
    --app=crm \
    --sitename=crm.yourdomain.com
```

### DigitalOcean App Platform
```yaml
# app.yaml
name: frappe-crm
services:
- name: crm
  source_dir: /
  github:
    repo: your-username/crm
    branch: main
  run_command: bench start
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DB_HOST
    value: ${db.HOSTNAME}
  - key: DB_PASSWORD
    value: ${db.PASSWORD}
  
databases:
- name: crm-db
  engine: MYSQL
  version: "8"
```

---

## 🔧 Option 5: Manual Server Setup

### Step-by-Step Production Setup:

#### 1. Install System Dependencies
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python dependencies
sudo apt install -y python3-pip python3-venv mariadb-server redis-server
```

#### 2. Setup Database
```bash
sudo mysql_secure_installation
sudo mysql -u root -p

# In MySQL prompt:
CREATE DATABASE crm_production;
CREATE USER 'crm_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON crm_production.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Install Frappe CRM
```bash
pip3 install frappe-bench
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# Get CRM app
bench get-app crm
bench new-site production.localhost --db-name crm_production --admin-password admin123
bench --site production.localhost install-app crm

# Build assets
bench build --app crm
```

#### 4. Production Configuration
```bash
# Setup nginx and supervisor
sudo bench setup production $(whoami)
sudo bench setup nginx
sudo bench setup supervisor

# Enable site
bench --site production.localhost enable-scheduler
bench --site production.localhost set-maintenance-mode off
```

---

## 📱 Mobile App Deployment (PWA)

The CRM includes a PWA (Progressive Web App). After deployment:

1. **Enable PWA**: The frontend automatically builds as a PWA
2. **Install on mobile**: Visit your CRM URL on mobile browser
3. **Add to home screen**: Browser will prompt to install as app

---

## 🔒 Security Configuration

### SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Firewall Setup
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct access to Frappe
```

### Environment Variables
```bash
# Production environment variables
export FRAPPE_SITE_NAME_HEADER=yourdomain.com
export DEVELOPER_MODE=0
export ALLOW_TESTS=0
export DB_QUERY_LOG_SIZE=0
```

---

## 📊 Monitoring & Maintenance

### Log Files:
- **Frappe logs**: `/home/frappe/frappe-bench/logs/`
- **Nginx logs**: `/var/log/nginx/`
- **Supervisor logs**: `/var/log/supervisor/`

### Backup Commands:
```bash
# Database backup
bench --site yourdomain.com backup --with-files

# Restore backup
bench --site yourdomain.com restore [backup-file]
```

### Update Commands:
```bash
# Update apps
bench update --build

# Update specific app
bench update --app crm
```

---

## 🎯 Performance Optimization

### Database Optimization
```sql
-- Add these to MySQL config (/etc/mysql/mysql.conf.d/mysqld.cnf)
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 256M
```

### Redis Configuration
```bash
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## 🆘 Troubleshooting

### Common Issues:

1. **Port already in use**: Kill process on port 8000
   ```bash
   sudo lsof -t -i tcp:8000 | xargs kill -9
   ```

2. **Database connection error**: Check MariaDB service
   ```bash
   sudo systemctl status mariadb
   sudo systemctl restart mariadb
   ```

3. **Build failures**: Clear cache and rebuild
   ```bash
   bench clear-cache
   bench build --app crm
   ```

4. **Permission errors**: Fix file permissions
   ```bash
   sudo chown -R frappe:frappe /home/frappe/frappe-bench
   ```

---

## 📞 Support Resources

- **Documentation**: https://docs.frappe.io/crm
- **Community**: https://discuss.erpnext.com/c/frappecrm
- **Telegram**: https://t.me/frappecrm
- **GitHub Issues**: https://github.com/frappe/crm/issues

Choose the deployment option that best fits your needs and technical expertise!