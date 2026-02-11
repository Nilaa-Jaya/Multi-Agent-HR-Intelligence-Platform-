# Multi-Agent HR Intelligence Platform - Docker Deployment Guide

## Overview

This guide covers deploying Multi-Agent HR Intelligence Platform using Docker and Docker Compose for both development and production environments.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- API Keys (Groq, OpenAI)

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

### 2. Build and Run (Development)

```bash
# Build the Docker image
./scripts/docker-build.sh

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Main UI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health

## Architecture

### Services

The application runs with the following services:

1. **fastapi_app** - Main application (Port 8000)
2. **postgres** - PostgreSQL database (Port 5432)
3. **redis** - Cache and session store (Port 6379)
4. **nginx** - Reverse proxy (Ports 80, 443)

### Volumes

- `postgres_data` - PostgreSQL data persistence
- `redis_data` - Redis data persistence
- `app_data` - Application data (KB, uploads)
- `app_logs` - Application logs

### Networks

- `smartsupport_network` - Bridge network for service communication

## Development Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d fastapi_app

# View logs
docker-compose logs -f fastapi_app

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Scripts

```bash
# Build image
./scripts/docker-build.sh latest development

# Run containers
./scripts/docker-run.sh dev

# View status
docker-compose ps
```

## Production Deployment

### 1. Configure Production Environment

```bash
# Update .env with production values
ENVIRONMENT=production
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://smartsupport_user:SECURE_PASSWORD@postgres:5432/smartsupport
SECRET_KEY=your-very-secure-secret-key-min-32-chars
ALLOWED_HOSTS=yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

### 2. Deploy to Production

```bash
# Deploy using script
./scripts/docker-deploy.sh production latest

# Or manually with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Production Configuration

The `docker-compose.prod.yml` includes:
- Resource limits (CPU, Memory)
- Production logging (JSON, rotation)
- PostgreSQL instead of SQLite
- Redis for caching
- Nginx reverse proxy
- Health checks
- Auto-restart policies

## Docker Commands Reference

### Building

```bash
# Build development image
docker build -t smartsupport-ai:dev .

# Build production image
docker build --build-arg BUILD_ENV=production -t smartsupport-ai:prod .

# Build with no cache
docker build --no-cache -t smartsupport-ai:latest .
```

### Running

```bash
# Run single container
docker run -d \
  --name smartsupport \
  -p 8000:8000 \
  --env-file .env \
  smartsupport-ai:latest

# Run with volume mounts
docker run -d \
  --name smartsupport \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  smartsupport-ai:latest

# Run in interactive mode
docker run -it --rm \
  --env-file .env \
  smartsupport-ai:latest \
  /bin/bash
```

### Debugging

```bash
# View logs
docker logs smartsupport_app -f

# Execute commands in running container
docker exec -it smartsupport_app bash

# Inspect container
docker inspect smartsupport_app

# Check resource usage
docker stats smartsupport_app

# View container processes
docker top smartsupport_app
```

### Maintenance

```bash
# Restart service
docker-compose restart fastapi_app

# Rebuild and restart
docker-compose up -d --build fastapi_app

# Remove stopped containers
docker-compose rm

# Prune unused images
docker image prune -a

# View disk usage
docker system df
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | `gsk_xxx` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | `sk-xxx` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Secret key for sessions | `your-secret-key` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `WORKERS` | Gunicorn workers | `4` |
| `TIMEOUT` | Request timeout | `120` |

## Health Checks

### Application Health

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# Expected response
{
  "status": "healthy",
  "version": "2.2.0",
  "timestamp": "2025-11-24T00:00:00Z"
}
```

### Service Health

```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps postgres

# View health status
docker inspect --format='{{json .State.Health}}' smartsupport_app | jq
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs smartsupport_app --tail 100

# Check docker-compose logs
docker-compose logs fastapi_app
```

### Database Connection Issues

```bash
# Check if postgres is running
docker-compose ps postgres

# Test postgres connection
docker exec -it smartsupport_postgres psql -U smartsupport_user -d smartsupport

# Check database logs
docker logs smartsupport_postgres
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R 1000:1000 data logs

# Rebuild with correct permissions
docker-compose down
docker-compose up -d --build
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

## Backup and Restore

### Backup

```bash
# Backup database
docker exec smartsupport_postgres pg_dump -U smartsupport_user smartsupport > backup.sql

# Backup volumes
docker run --rm -v smartsupport_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data

# Backup application data
tar czf app_data_backup.tar.gz data/
```

### Restore

```bash
# Restore database
docker exec -i smartsupport_postgres psql -U smartsupport_user smartsupport < backup.sql

# Restore volumes
docker run --rm -v smartsupport_postgres_data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/postgres_backup.tar.gz --strip 1"

# Restore application data
tar xzf app_data_backup.tar.gz
```

## Scaling

### Horizontal Scaling

```bash
# Scale FastAPI app to 3 instances
docker-compose up -d --scale fastapi_app=3

# With load balancer (nginx)
# Update nginx.conf with multiple upstream servers
```

### Resource Limits

Edit `docker-compose.prod.yml`:

```yaml
services:
  fastapi_app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Security Best Practices

1. **Use secrets management**
   - Never commit `.env` to git
   - Use Docker secrets or vault in production

2. **Non-root user**
   - Containers run as `appuser` (UID 1000)

3. **Network isolation**
   - Services communicate via internal network
   - Only necessary ports exposed

4. **Regular updates**
   ```bash
   # Update base images
   docker-compose pull
   docker-compose up -d
   ```

5. **Enable HTTPS**
   - Configure SSL certificates in `docker/nginx.conf`
   - Use Let's Encrypt for free certificates

## Monitoring

### Container Metrics

```bash
# View resource usage
docker stats

# Continuous monitoring
docker stats --no-stream

# Export metrics
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Application Metrics

```bash
# View application stats
curl http://localhost:8000/api/v1/stats

# Health monitoring
watch -n 5 'curl -s http://localhost:8000/api/v1/health | jq'
```

## Next Steps

1. **Configure CI/CD** - Automated deployments
2. **Add monitoring** - Prometheus, Grafana
3. **Implement logging** - ELK stack, CloudWatch
4. **Set up alerts** - PagerDuty, Slack
5. **Enable auto-scaling** - Kubernetes, Docker Swarm

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review documentation: `/docs`
- Open an issue on GitHub

---

**Built with FastAPI + Docker**
**Version:** 2.2.0
**Status:** Production-Ready [DONE]
