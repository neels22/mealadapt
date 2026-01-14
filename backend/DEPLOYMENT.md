# MainMeal Backend - Deployment Guide

This guide covers deploying the MainMeal FastAPI backend to production using Docker Compose with Google Cloud SQL.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Cloud SQL Proxy Configuration](#cloud-sql-proxy-configuration)
4. [Deployment Steps](#deployment-steps)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

## Prerequisites

Before deploying, ensure you have:

- Docker and Docker Compose installed
- Access to Google Cloud Platform (GCP) project
- Google Cloud SQL PostgreSQL instance created and running
- Cloud SQL instance connection name: `gen-lang-client-0515155454:us-central1:free-trial-first-project`
- GCP service account with Cloud SQL Client role (if using file-based authentication)
- Google Gemini API key
- Production frontend URL for CORS configuration

## Environment Setup

### 1. Create `.env` File

Copy `env.example` to `.env` and fill in all required values:

```bash
cd backend
cp env.example .env
```

### 2. Required Environment Variables

Edit `.env` and set the following **REQUIRED** variables:

#### Cloud SQL Configuration
```env
CLOUD_SQL_USER=your-cloud-sql-username
CLOUD_SQL_PASSWORD=your-cloud-sql-password
CLOUD_SQL_DATABASE=your-database-name
DATABASE_URL=postgresql+asyncpg://${CLOUD_SQL_USER}:${CLOUD_SQL_PASSWORD}@cloud-sql-proxy:5433/${CLOUD_SQL_DATABASE}
DB_SCHEMA=mealadapt
```

#### Security
```env
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=your-secure-jwt-secret-at-least-32-characters
```

#### API Keys
```env
GEMINI_API_KEY=your-gemini-api-key
```

#### CORS Configuration
```env
# Replace with your production frontend URL(s)
CORS_ORIGINS=https://your-production-domain.com,https://www.your-production-domain.com
```

#### Production Settings
```env
SQL_ECHO=false
DEBUG_DB=false
```

### 3. Generate JWT Secret

Generate a secure JWT secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and set it as `JWT_SECRET` in your `.env` file.

## Cloud SQL Proxy Configuration

The deployment uses Cloud SQL Proxy as a Docker service to securely connect to your Cloud SQL instance.

### Authentication Options

#### Option 1: Application Default Credentials (Recommended for GCP)

If running on Google Cloud Platform (Cloud Run, GCE, etc.), the proxy will automatically use Application Default Credentials. No additional configuration needed.

#### Option 2: Service Account Key File

If running outside GCP or need explicit authentication:

1. **Create Service Account:**
   - Go to GCP Console → IAM & Admin → Service Accounts
   - Create a new service account
   - Grant "Cloud SQL Client" role

2. **Download Key:**
   - Create and download JSON key file
   - Save as `gcp-service-account.json` in the `backend/` directory

3. **Update docker-compose.yml:**
   - Uncomment the volumes section in `cloud-sql-proxy` service:
   ```yaml
   volumes:
     - ./gcp-service-account.json:/secrets/cloudsql/key.json:ro
   environment:
     GOOGLE_APPLICATION_CREDENTIALS: /secrets/cloudsql/key.json
   ```

4. **Add to .gitignore:**
   Ensure `gcp-service-account.json` is in `.gitignore` (already included)

## Deployment Steps

### 1. Verify Configuration

Before deploying, verify:
- All environment variables are set in `.env`
- Cloud SQL instance is running
- Service account has proper permissions (if using file-based auth)
- Frontend URL is correct in `CORS_ORIGINS`

### 2. Build and Start Services

```bash
cd backend

# Build and start all services
docker-compose up -d --build
```

This will:
- Build the backend Docker image
- Start Cloud SQL Proxy service
- Start Backend API service
- Wait for Cloud SQL Proxy to be ready before starting backend

### 3. Check Service Status

```bash
# Check all services are running
docker-compose ps

# Expected output should show:
# - mainmeal_cloud_sql_proxy (Up)
# - mainmeal_backend (Up)
```

### 4. View Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View Cloud SQL Proxy logs only
docker-compose logs -f cloud-sql-proxy
```

## Verification

### 1. Health Check

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Root Endpoint

Test the root endpoint:

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"message": "MainMeal API is running", "version": "1.0.0"}
```

### 3. Database Connection

Check backend logs for database initialization:

```bash
docker-compose logs backend | grep -i "database"
```

You should see:
```
✅ Database schema 'mealadapt' and tables created successfully
```

### 4. API Documentation

Access interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Cloud SQL Proxy Connection Issues

**Problem:** Backend can't connect to Cloud SQL

**Solutions:**
1. Verify Cloud SQL instance is running in GCP Console
2. Check Cloud SQL Proxy logs: `docker-compose logs cloud-sql-proxy`
3. Verify connection name in `docker-compose.yml` matches your instance
4. Check service account permissions if using file-based auth
5. Ensure Cloud SQL Proxy service is healthy: `docker-compose ps`

### Database Schema Creation Fails

**Problem:** Database schema/tables not created

**Solutions:**
1. Verify `DB_SCHEMA` environment variable is set
2. Check database user has CREATE SCHEMA permission
3. Review backend logs for specific error messages
4. Verify `DATABASE_URL` format is correct

### Backend Won't Start

**Problem:** Backend container exits immediately

**Solutions:**
1. Check logs: `docker-compose logs backend`
2. Verify all required environment variables are set
3. Check JWT_SECRET is at least 32 characters
4. Verify GEMINI_API_KEY is valid
5. Ensure Cloud SQL Proxy is running before backend starts

### CORS Issues

**Problem:** Frontend can't connect to API

**Solutions:**
1. Verify `CORS_ORIGINS` includes your frontend URL
2. Check for trailing slashes in URLs
3. Ensure URLs match exactly (including protocol: http vs https)
4. Restart backend after changing CORS_ORIGINS

### Port Already in Use

**Problem:** Port 8000 or 5433 already in use

**Solutions:**
1. Change port mapping in `docker-compose.yml`
2. Stop conflicting services
3. Check what's using the port: `lsof -i :8000` or `lsof -i :5433`

## Security Best Practices

### 1. Environment Variables

- **Never commit `.env` files** to version control
- Use secrets management services (GCP Secret Manager, AWS Secrets Manager, etc.)
- Rotate secrets periodically, especially `JWT_SECRET`
- Use different secrets for development and production

### 2. Service Account Keys

- Store service account keys securely
- Use least privilege principle (only Cloud SQL Client role needed)
- Rotate keys periodically
- Never commit keys to version control

### 3. Database Security

- Use strong passwords for database users
- Enable SSL/TLS for database connections (if supported)
- Restrict database access to necessary IPs
- Regularly update database software

### 4. Application Security

- Keep dependencies updated: `pip list --outdated`
- Use production-ready settings (`SQL_ECHO=false`)
- Monitor logs for suspicious activity
- Implement rate limiting (already configured)
- Use HTTPS in production (configure reverse proxy)

### 5. Docker Security

- Run containers as non-root user (already configured)
- Keep base images updated
- Scan images for vulnerabilities
- Use multi-stage builds (already implemented)

## Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Verify deployment
curl http://localhost:8000/health
```

### Viewing Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Stopping Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes data)
docker-compose down -v
```

### Database Backups

Regularly backup your Cloud SQL database using GCP Console or `gcloud` CLI:

```bash
gcloud sql backups create --instance=your-instance-name
```

## Production Considerations

### Reverse Proxy

For production, use a reverse proxy (nginx, Traefik, etc.) in front of the backend:

- SSL/TLS termination
- Rate limiting
- Request logging
- Load balancing (if multiple backend instances)

### Monitoring

Set up monitoring for:
- Application health (`/health` endpoint)
- Database connection status
- API response times
- Error rates
- Resource usage (CPU, memory)

### Scaling

To scale the backend:
- Increase `--workers` in Dockerfile CMD (currently 4)
- Run multiple backend containers behind a load balancer
- Monitor database connection pool limits
- Consider read replicas for database

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review this documentation
3. Check GCP Cloud SQL status
4. Verify environment variables

## Quick Reference

```bash
# Start services
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Check status
docker-compose ps

# Health check
curl http://localhost:8000/health

# Rebuild after code changes
docker-compose up -d --build
```
