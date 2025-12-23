# Docker Deployment Guide

This guide covers deploying Diabeateeze using Docker on a Raspberry Pi or any other platform.

## Prerequisites

- Docker and Docker Compose installed on your target machine
- GitHub account with packages enabled
- Repository secrets configured (automatic with `GITHUB_TOKEN`)

## Building Images

Images are automatically built and published to GitHub Container Registry (GHCR) when you:
- Push to the `main` branch
- Create a version tag (e.g., `v1.0.0`)

The GitHub Action builds multi-architecture images supporting:
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit, including Raspberry Pi 4/5)

## Deployment Steps

### 1. Prepare Your Server

```bash
# Install Docker and Docker Compose on Raspberry Pi
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

### 2. Create Deployment Directory

```bash
mkdir -p ~/diabeateeze
cd ~/diabeateeze
```

### 3. Download docker-compose.yml

Download the `docker-compose.yml` file from your repository or create it manually.

### 4. Configure Environment Variables

Edit the `docker-compose.yml` file and update:

- **Image name**: Replace `ghcr.io/user/diabeateeze:latest` with your actual GitHub username/repo
- **SECRET_KEY**: Generate with:
  ```bash
  python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(50))'
  ```
- **POSTGRES_PASSWORD**: Choose a secure database password
- **DATABASE_URL**: Update with the same password
- **ALLOWED_HOSTS**: Add your domain or IP address

### 5. Authenticate to GHCR (if image is private)

```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME
# Use a Personal Access Token (PAT) with `read:packages` scope as password
```

### 6. Deploy

```bash
# Pull the latest image
docker-compose pull

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### 7. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 8. Access Your Application

Open your browser and navigate to:
- `http://your-raspberry-pi-ip:8000`
- Admin panel: `http://your-raspberry-pi-ip:8000/admin`

## Management Commands

### View Logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Update to Latest Version
```bash
docker-compose pull
docker-compose up -d
```

### Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Backup Database
```bash
docker-compose exec db pg_dump -U diabeateeze diabeateeze > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
cat backup_file.sql | docker-compose exec -T db psql -U diabeateeze diabeateeze
```

## Production Considerations

### Reverse Proxy (Recommended)

For production, use Nginx or Caddy as a reverse proxy:
- Serve static files efficiently
- SSL/TLS termination
- Rate limiting
- Better performance

Uncomment the nginx service in `docker-compose.yml` and configure accordingly.

### SSL/TLS Certificates

Use Let's Encrypt with Certbot or Caddy for automatic HTTPS:

```bash
# With Certbot
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com
```

### Monitoring

Consider adding:
- Health checks
- Log aggregation (e.g., Loki)
- Metrics (e.g., Prometheus)
- Uptime monitoring

### Backups

Set up automated database backups:

```bash
# Add to crontab
0 2 * * * cd ~/diabeateeze && docker-compose exec -T db pg_dump -U diabeateeze diabeateeze > /backups/diabeateeze_$(date +\%Y\%m\%d).sql
```

### Security

- Keep Docker and images updated
- Use strong passwords
- Restrict database access
- Enable firewall (ufw)
- Regular security updates
- Use secrets management for sensitive data

## Troubleshooting

### Container won't start
```bash
docker-compose logs web
docker-compose logs db
```

### Database connection issues
- Verify DATABASE_URL is correct
- Check if PostgreSQL container is healthy: `docker-compose ps`
- Ensure database container started before web: `docker-compose up -d db && sleep 10 && docker-compose up -d web`

### Static files not loading
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Out of memory (Raspberry Pi)
- Reduce gunicorn workers in docker-compose.yml: `--workers 1`
- Increase swap space
- Monitor with: `docker stats`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_ENVIRONMENT` | Yes | development | Environment mode (development/testing/production) |
| `DEBUG` | No | False (prod) | Django debug mode |
| `SECRET_KEY` | Yes | - | Django secret key (must be unique in production) |
| `ALLOWED_HOSTS` | Yes (prod) | [] | Comma-separated list of allowed hostnames |
| `DATABASE_URL` | Yes (prod) | - | PostgreSQL connection string |
| `EMAIL_HOST` | No | - | SMTP server hostname |
| `EMAIL_PORT` | No | 587 | SMTP server port |
| `EMAIL_USE_TLS` | No | True | Use TLS for email |
| `EMAIL_HOST_USER` | No | - | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | - | SMTP password |

## Support

For issues, please check:
1. Container logs: `docker-compose logs`
2. GitHub Actions build status
3. Repository issues
