# Deployment Guide

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Google Cloud Platform (GCP) Deployment](#google-cloud-platform-gcp-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Nginx Configuration](#nginx-configuration)
7. [SSL/HTTPS Setup](#sslhttps-setup)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites
- Python 3.8+
- pip
- virtualenv or venv
- Git

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd RealTimeDocumentSystem
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the project root:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Test WebSocket Connection**
   ```bash
   # Install wscat for testing
   npm install -g wscat
   
   # Test WebSocket
   wscat -c ws://localhost:8000/ws/document/1/
   ```

## Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- PostgreSQL (recommended) or MySQL
- Nginx
- Redis (optional, for session storage)

### Server Setup

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and Dependencies**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   sudo apt install postgresql postgresql-contrib
   sudo apt install nginx
   sudo apt install redis-server  # Optional
   ```

3. **Create Application User**
   ```bash
   sudo adduser doceditor
   sudo usermod -aG sudo doceditor
   ```

4. **Clone Application**
   ```bash
   sudo -u doceditor git clone <repository-url> /home/doceditor/realtime-doc-editor
   cd /home/doceditor/realtime-doc-editor
   ```

5. **Setup Virtual Environment**
   ```bash
   sudo -u doceditor python3 -m venv venv
   sudo -u doceditor /home/doceditor/realtime-doc-editor/venv/bin/pip install -r requirements.txt
   ```

### Database Configuration

1. **PostgreSQL Setup**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE doceditor;
   CREATE USER doceditor_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE doceditor TO doceditor_user;
   \q
   ```

2. **Update Django Settings**
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'doceditor',
           'USER': 'doceditor_user',
           'PASSWORD': 'secure_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### ASGI Server Setup

1. **Install Daphne**
   ```bash
   sudo -u doceditor /home/doceditor/realtime-doc-editor/venv/bin/pip install daphne
   ```

2. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/doceditor.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Real-Time Document Editor
   After=network.target

   [Service]
   Type=simple
   User=doceditor
   Group=doceditor
   WorkingDirectory=/home/doceditor/realtime-doc-editor
   Environment=PATH=/home/doceditor/realtime-doc-editor/venv/bin
   ExecStart=/home/doceditor/realtime-doc-editor/venv/bin/daphne -b 0.0.0.0 -p 8000 RealTimeDocumentSystem.asgi:application
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start and Enable Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start doceditor
   sudo systemctl enable doceditor
   sudo systemctl status doceditor
   ```

## Google Cloud Platform (GCP) Deployment

### 1. Create VM Instance

1. **Create Compute Engine Instance**
   ```bash
   gcloud compute instances create doceditor-instance \
     --zone=us-central1-a \
     --machine-type=e2-medium \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --tags=http-server,https-server
   ```

2. **Configure Firewall Rules**
   ```bash
   gcloud compute firewall-rules create allow-http \
     --allow tcp:80 \
     --target-tags=http-server \
     --description="Allow HTTP traffic"

   gcloud compute firewall-rules create allow-https \
     --allow tcp:443 \
     --target-tags=https-server \
     --description="Allow HTTPS traffic"

   gcloud compute firewall-rules create allow-websocket \
     --allow tcp:8000 \
     --target-tags=http-server \
     --description="Allow WebSocket traffic"
   ```

### 2. Connect to Instance
```bash
gcloud compute ssh doceditor-instance --zone=us-central1-a
```

### 3. Follow Production Deployment Steps
Use the production deployment steps above on your GCP instance.

### 4. Load Balancer Setup (Optional)
```bash
# Create health check
gcloud compute health-checks create http doceditor-health-check \
  --port=8000 \
  --request-path=/health/

# Create backend service
gcloud compute backend-services create doceditor-backend \
  --health-checks=doceditor-health-check \
  --global

# Create URL map
gcloud compute url-maps create doceditor-lb \
  --default-service=doceditor-backend

# Create HTTP proxy
gcloud compute target-http-proxies create doceditor-http-proxy \
  --url-map=doceditor-lb

# Create forwarding rule
gcloud compute forwarding-rules create doceditor-http-rule \
  --global \
  --target-http-proxy=doceditor-http-proxy \
  --ports=80
```

## AWS Deployment

### 1. EC2 Instance Setup

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Instance type: t3.medium or larger
   - Security Group: Allow ports 22, 80, 443, 8000

2. **Security Group Configuration**
   ```
   SSH (22): 0.0.0.0/0
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   Custom TCP (8000): 0.0.0.0/0
   ```

3. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

### 2. Application Deployment
Follow the production deployment steps above.

### 3. Load Balancer (Optional)
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name doceditor-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Run the application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "RealTimeDocumentSystem.asgi:application"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://doceditor:password@db:5432/doceditor
    depends_on:
      - db
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=doceditor
      - POSTGRES_USER=doceditor
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Nginx Configuration

### Basic Configuration
```nginx
upstream doceditor {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # WebSocket support
    location /ws/ {
        proxy_pass http://doceditor;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Static files
    location /static/ {
        alias /home/doceditor/realtime-doc-editor/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/doceditor/realtime-doc-editor/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://doceditor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # WebSocket support with SSL
    location /ws/ {
        proxy_pass http://doceditor;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Other locations same as above...
}
```

## SSL/HTTPS Setup

### Using Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Using Cloudflare
1. Add your domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS encryption mode: Full
4. Enable WebSocket support in Cloudflare settings

## Monitoring and Logging

### 1. Logging Configuration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/doceditor/app.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### 2. Health Check Endpoint
```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### 3. System Monitoring
```bash
# Monitor application logs
sudo journalctl -u doceditor -f

# Monitor system resources
htop
df -h
free -h

# Monitor WebSocket connections
netstat -an | grep :8000
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   ```bash
   # Check if ASGI server is running
   sudo systemctl status doceditor
   
   # Check firewall
   sudo ufw status
   
   # Test WebSocket manually
   wscat -c ws://yourdomain.com/ws/document/1/
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   sudo -u doceditor python manage.py dbshell
   
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

3. **Static Files Not Loading**
   ```bash
   # Collect static files
   sudo -u doceditor python manage.py collectstatic --noinput
   
   # Check Nginx configuration
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R doceditor:doceditor /home/doceditor/realtime-doc-editor
   sudo chmod -R 755 /home/doceditor/realtime-doc-editor
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes
   CREATE INDEX idx_document_owner ON app_document(owner_id);
   CREATE INDEX idx_document_created ON app_document(created_at);
   ```

2. **Caching Setup**
   ```python
   # settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Gunicorn Configuration**
   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   max_requests = 1000
   max_requests_jitter = 50
   ```

### Backup Strategy

1. **Database Backup**
   ```bash
   # Create backup script
   sudo nano /home/doceditor/backup.sh
   ```

   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   pg_dump doceditor > /home/doceditor/backups/db_backup_$DATE.sql
   tar -czf /home/doceditor/backups/files_backup_$DATE.tar.gz /home/doceditor/realtime-doc-editor/media/
   ```

2. **Automated Backups**
   ```bash
   # Add to crontab
   sudo crontab -e
   # Add: 0 2 * * * /home/doceditor/backup.sh
   ```

### Security Checklist

- [ ] Firewall configured
- [ ] SSL certificate installed
- [ ] Database password changed
- [ ] Django secret key updated
- [ ] Debug mode disabled
- [ ] Allowed hosts configured
- [ ] Static files collected
- [ ] Logs configured
- [ ] Backups scheduled
- [ ] Monitoring enabled

## Support

For deployment issues:
- Check application logs: `sudo journalctl -u doceditor -f`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Check system resources: `htop`, `df -h`
- Test WebSocket connection: `wscat -c ws://yourdomain.com/ws/document/1/`

For additional help:
- Create an issue on GitHub
- Check the troubleshooting section
- Review server logs for specific error messages 