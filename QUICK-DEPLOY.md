# 🚀 Quick Deployment Guide

## Choose Your Deployment Method:

### 1. 🌟 Easiest: Frappe Cloud (Recommended)
**Perfect for business use, zero maintenance**

1. Visit: https://frappecloud.com/crm/signup
2. Create account and choose plan
3. Your CRM is ready in 5 minutes!
4. Access at: `yoursite.frappecloud.com`

**Benefits**: SSL included, automatic backups, 99.9% uptime, no server management

---

### 2. 🐳 Docker Production (Self-Hosted)
**Best balance of control and simplicity**

#### Prerequisites:
- Server with Docker installed
- Domain name pointing to server
- 2GB+ RAM, 20GB+ storage

#### Quick Steps:
```bash
# 1. Clone or download files
git clone https://github.com/frappe/crm.git
cd crm

# 2. Make deployment script executable
chmod +x deploy.sh

# 3. Run deployment (follows interactive setup)
./deploy.sh
```

The script will:
- ✅ Check system requirements
- ✅ Guide you through .env configuration
- ✅ Set up SSL certificates (Let's Encrypt)
- ✅ Deploy with production optimizations
- ✅ Provide management commands

**Access**: `https://yourdomain.com`
**Login**: Administrator / your_admin_password

---

### 3. ☁️ Cloud Platforms

#### AWS/DigitalOcean/GCP:
```bash
wget https://frappe.io/easy-install.py

python3 ./easy-install.py deploy \
    --project=crm_production \
    --email=your-email@domain.com \
    --image=ghcr.io/frappe/crm \
    --version=stable \
    --app=crm \
    --sitename=crm.yourdomain.com
```

---

## 🔧 Post-Deployment:

### Essential Steps:
1. **Change passwords**: Update admin password after first login
2. **Configure email**: Set up SMTP for notifications
3. **Enable backups**: Regular database + file backups
4. **Monitor logs**: Check application and system logs
5. **Update regularly**: Keep CRM updated with latest security patches

### Management Commands:
```bash
# View logs
./deploy.sh --logs

# Create backup  
./deploy.sh --backup

# Update application
./deploy.sh --update

# Restart services
./deploy.sh --restart
```

### Backup & Restore:
```bash
# Automated daily backups included
# Manual backup:
docker-compose -f docker-compose.production.yml exec frappe bench --site yourdomain.com backup --with-files

# Restore:
docker-compose -f docker-compose.production.yml exec frappe bench --site yourdomain.com restore backup-file.sql.gz
```

---

## 📊 Monitoring:

### Key Metrics:
- **Database**: Monitor MariaDB performance
- **Memory**: Keep usage under 80%
- **Disk**: Regular cleanup of old logs/backups
- **SSL**: Certificate auto-renewal (Let's Encrypt)

### Log Locations:
- Application: `docker-compose logs frappe`
- Web server: `docker-compose logs traefik`
- Database: `docker-compose logs mariadb`

---

## 🔒 Security Checklist:

- ✅ Strong passwords (admin, database)
- ✅ SSL certificate (automatic via Let's Encrypt)
- ✅ Firewall configured (ports 80, 443 only)
- ✅ Regular updates applied
- ✅ Backup strategy implemented
- ✅ Monitoring alerts configured

---

## 🆘 Need Help?

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Community**: https://discuss.erpnext.com/c/frappecrm  
- **Issues**: https://github.com/frappe/crm/issues
- **Telegram**: https://t.me/frappecrm

---

## 🎯 Production-Ready Features:

✅ **Load balancing** (multiple workers)  
✅ **SSL termination** (automatic certificates)  
✅ **Database optimization** (production tuning)  
✅ **Redis caching** (performance)  
✅ **Health checks** (automatic recovery)  
✅ **Backup automation** (daily backups)  
✅ **Log management** (structured logging)  
✅ **Security headers** (HTTPS, security policies)

Your Frappe CRM deployment will be production-ready with enterprise-grade features!