# Docker Quick Start Guide

## TL;DR - Get Running in 3 Commands

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your API keys

# 2. Build and run
docker-compose up -d

# 3. Access
# Open http://localhost:8000
```

---

## Step-by-Step Setup

### 1. Prerequisites

- Docker Desktop installed
- API keys for Groq and OpenAI

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env (use notepad, vim, or any editor)
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Minimum required:**
```env
GROQ_API_KEY=your_actual_groq_key
OPENAI_API_KEY=your_actual_openai_key
```

### 3. Run Development

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application

- **Web UI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/api/v1/health

### 5. Stop

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

---

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi_app
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart one service
docker-compose restart fastapi_app
```

### Execute Commands
```bash
# Open shell in container
docker exec -it smartsupport_app bash

# Run Python command
docker exec -it smartsupport_app python -c "print('Hello')"
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats
```

---

## Production Deployment

### Quick Production Deploy

```bash
# Update .env for production
ENVIRONMENT=production
DATABASE_URL=postgresql://smartsupport_user:STRONG_PASSWORD@postgres:5432/smartsupport
SECRET_KEY=your-very-long-random-secret-key-min-32-characters

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Or Use Deploy Script

```bash
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh production
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

### Container Won't Start
```bash
# Check logs
docker logs smartsupport_app --tail 50

# Check all logs
docker-compose logs
```

### Database Connection Error
```bash
# Check postgres is running
docker ps | grep postgres

# Restart postgres
docker-compose restart postgres
```

### Permission Denied
```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER data logs

# Windows - run Docker Desktop as admin
```

---

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI | 8000 | Main application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| Nginx | 80, 443 | Reverse proxy |

---

## File Structure

```
.
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Development
├── docker-compose.prod.yml # Production
├── .dockerignore          # Exclude files
├── .env.example           # Environment template
├── docker/
│   ├── entrypoint.sh      # Startup script
│   ├── nginx.conf         # Nginx config
│   └── wait-for-it.sh     # Wait for services
└── scripts/
    ├── docker-build.sh    # Build image
    ├── docker-run.sh      # Run containers
    └── docker-deploy.sh   # Production deploy
```

---

## Next Steps

1. [DONE] Get it running locally
2. [DONE] Test the API at /docs
3. [DONE] Try the web interface
4.  Read [DOCKER_README.md](DOCKER_README.md) for advanced usage
5.  Deploy to cloud (AWS, GCP, Azure)

---

## Need Help?

- **Logs:** `docker-compose logs -f`
- **Status:** `docker-compose ps`
- **Documentation:** [DOCKER_README.md](DOCKER_README.md)
- **Full docs:** http://localhost:8000/docs

---

**Version:** 2.2.0
**Status:** Production-Ready [DONE]
