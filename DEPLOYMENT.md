# 🚀 Deployment Guide

## Overview
This guide covers multiple deployment options for the E-Commerce Database Administration Project.

## Prerequisites
- Docker & Docker Compose
- Node.js 18+
- PostgreSQL 14+
- Python 3.9+

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose

1. **Clone and Setup**
```bash
git clone <repository-url>
cd project_db
```

2. **Environment Configuration**
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your settings
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=admin
DB_PASSWORD=admin123
JWT_SECRET=your-super-secret-jwt-key-here
```

3. **Start Services**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Access Applications**
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001
- PostgreSQL: localhost:5432

5. **Initialize Data (Optional)**
```bash
# Generate sample data
docker-compose exec backend python scripts/data_generator.py
```

### Docker Commands Reference

```bash
# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Remove volumes (careful - deletes data!)
docker-compose down -v

# Scale services
docker-compose up --scale backend=2

# Execute commands in containers
docker-compose exec postgres psql -U admin -d ecommerce_db
docker-compose exec backend npm test
```

## 🌐 Manual Deployment

### Database Setup

1. **Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download and install from https://www.postgresql.org/download/windows/
```

2. **Create Database and User**
```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE ecommerce_db;
CREATE USER admin WITH ENCRYPTED PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO admin;
ALTER USER admin CREATEDB;

-- Exit
\q
```

3. **Initialize Schema**
```bash
psql -h localhost -U admin -d ecommerce_db -f db/schema.sql
```

### Backend Deployment

1. **Install Dependencies**
```bash
cd backend
npm install --production
```

2. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with production values
```

3. **Start Application**
```bash
# Development
npm run dev

# Production
npm start

# With PM2 (recommended for production)
npm install -g pm2
pm2 start server.js --name "ecommerce-api"
pm2 save
pm2 startup
```

### Frontend Deployment

1. **Build Application**
```bash
cd frontend
npm install
npm run build
```

2. **Serve with Nginx**
```bash
# Install nginx
sudo apt install nginx  # Ubuntu/Debian
brew install nginx      # macOS

# Copy build files
sudo cp -r build/* /var/www/html/

# Configure nginx (see nginx.conf in repo)
sudo cp nginx.conf /etc/nginx/sites-available/ecommerce
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

3. **Serve with PM2 (Alternative)**
```bash
npm install -g serve
pm2 serve build 3000 --name "ecommerce-frontend"
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS RDS + EC2

1. **Database Setup (RDS)**
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier ecommerce-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password admin123 \
  --allocated-storage 20 \
  --storage-type gp2 \
  --publicly-accessible
```

2. **Application Deployment (EC2)**
```bash
# Connect to EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Deploy with Docker Compose
git clone <repository-url>
cd project_db
# Update docker-compose.yml with RDS endpoint
docker-compose up -d
```

#### Using ECS + Fargate

```yaml
# ecs-task-definition.json
{
  "family": "ecommerce-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ecommerce-backend:latest",
      "portMappings": [{"containerPort": 3001}],
      "environment": [
        {"name": "DB_HOST", "value": "your-rds-endpoint"}
      ]
    },
    {
      "name": "frontend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ecommerce-frontend:latest",
      "portMappings": [{"containerPort": 3000}]
    }
  ]
}
```

### Digital Ocean Deployment

1. **Create Droplet**
```bash
# Create Ubuntu 20.04 droplet
doctl compute droplet create ecommerce-app \
  --size s-2vcpu-2gb \
  --image ubuntu-20-04-x64 \
  --region nyc1 \
  --ssh-keys your-ssh-key-id
```

2. **Setup Application**
```bash
# Connect to droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Deploy application
git clone <repository-url>
cd project_db
docker-compose up -d
```

### Heroku Deployment

1. **Prepare for Heroku**
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create apps
heroku create ecommerce-api
heroku create ecommerce-frontend
```

2. **Deploy Backend**
```bash
cd backend

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set JWT_SECRET=your-secret-key

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a ecommerce-api
git push heroku main
```

3. **Deploy Frontend**
```bash
cd frontend

# Add build script to package.json
# "heroku-postbuild": "npm run build"

# Set API URL
heroku config:set REACT_APP_API_URL=https://ecommerce-api.herokuapp.com/api

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a ecommerce-frontend
git push heroku main
```

## 🔧 Production Configuration

### Environment Variables

**Backend (.env)**
```env
NODE_ENV=production
PORT=3001
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=admin
DB_PASSWORD=secure_password_here
JWT_SECRET=very-secure-jwt-secret-key
FRONTEND_URL=https://your-domain.com
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

**Frontend (.env)**
```env
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_ENVIRONMENT=production
```

### Security Considerations

1. **SSL/TLS Setup**
```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d your-domain.com
```

2. **Firewall Configuration**
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

3. **Database Security**
```sql
-- Create restricted users
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ecommerce_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

### Monitoring Setup

1. **Application Monitoring**
```bash
# Install monitoring tools
npm install -g pm2
pm2 install pm2-logrotate

# Monitor applications
pm2 monit
```

2. **Database Monitoring**
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Test connection
psql -h localhost -U admin -d ecommerce_db -c "SELECT 1;"
```

2. **Docker Issues**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart services
docker-compose restart

# Clean build
docker-compose build --no-cache
```

3. **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER project_db/

# Database permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
```

### Performance Optimization

1. **Database Optimization**
```sql
-- Update statistics
ANALYZE;

-- Reindex tables
REINDEX DATABASE ecommerce_db;

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

2. **Application Optimization**
```bash
# Enable gzip compression
# Add to nginx.conf or Express app

# Use CDN for static assets
# Configure CloudFlare or AWS CloudFront
```

## 📊 Health Checks

### Application Health
```bash
# Backend health check
curl http://localhost:3001/health

# Database health check
curl http://localhost:3001/api/health
```

### Monitoring Commands
```bash
# Check system resources
htop
df -h
free -m

# Check application logs
pm2 logs
tail -f /var/log/nginx/access.log
```

## 🔄 Backup Strategy

### Automated Backups
```bash
# Setup cron job for daily backups
echo "0 2 * * * cd /path/to/project && python db/backup.py" | crontab -

# Manual backup
python db/backup.py

# Restore from backup
python db/restore.py backup_2024_01_15.sql
```

This deployment guide provides comprehensive instructions for various deployment scenarios. Choose the method that best fits your infrastructure and requirements.
