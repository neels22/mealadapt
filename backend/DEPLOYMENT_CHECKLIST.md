# MainMeal Backend - Pre-Deployment Checklist

Use this checklist to verify everything is ready before deploying to production.

## Environment Configuration

### Required Environment Variables

- [ ] **CLOUD_SQL_USER** - Cloud SQL database username is set
- [ ] **CLOUD_SQL_PASSWORD** - Cloud SQL database password is set and secure
- [ ] **CLOUD_SQL_DATABASE** - Cloud SQL database name is correct
- [ ] **DATABASE_URL** - Database connection URL is properly formatted
  - Format: `postgresql+asyncpg://${CLOUD_SQL_USER}:${CLOUD_SQL_PASSWORD}@cloud-sql-proxy:5433/${CLOUD_SQL_DATABASE}`
- [ ] **DB_SCHEMA** - Database schema name is set (default: `mealadapt`)
- [ ] **JWT_SECRET** - JWT secret key is set and at least 32 characters long
  - Generated using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **GEMINI_API_KEY** - Google Gemini API key is set and valid
- [ ] **CORS_ORIGINS** - CORS origins include production frontend URL(s)
  - Should NOT include `http://localhost:3000` in production
  - Format: `https://yourdomain.com,https://www.yourdomain.com`
- [ ] **SQL_ECHO** - Set to `false` for production
- [ ] **DEBUG_DB** - Set to `false` for production (optional)

### Optional Environment Variables

- [ ] **LLM_LIMIT_ANALYZE_RECIPE** - Custom rate limit (default: 50)
- [ ] **LLM_LIMIT_ANALYZE_INGREDIENT_IMAGE** - Custom rate limit (default: 30)
- [ ] **LLM_LIMIT_SUGGEST_RECIPES** - Custom rate limit (default: 20)
- [ ] **LLM_LIMIT_EXTRACT_INGREDIENTS** - Custom rate limit (default: 30)
- [ ] **LLM_LIMIT_ANALYZE_INGREDIENTS** - Custom rate limit (default: 40)

## Google Cloud Platform Setup

### Cloud SQL Instance

- [ ] Cloud SQL PostgreSQL instance is created and running
- [ ] Cloud SQL instance connection name matches: `gen-lang-client-0515155454:us-central1:free-trial-first-project`
- [ ] Database user exists with proper permissions
- [ ] Database password is strong and secure
- [ ] Database name is correct

### Authentication

- [ ] **Option A:** Application Default Credentials configured (if running on GCP)
- [ ] **Option B:** Service account key file downloaded (if using file-based auth)
  - Service account has "Cloud SQL Client" role
  - Key file saved as `gcp-service-account.json` in `backend/` directory
  - Key file is in `.gitignore` (not committed to version control)
  - `docker-compose.yml` volumes section is uncommented if using file-based auth

## Code and Configuration

### Files Verification

- [ ] `Dockerfile` uses production settings (`--workers 4`)
- [ ] `docker-compose.yml` includes Cloud SQL Proxy service
- [ ] `docker-compose.yml` backend service has `DB_SCHEMA` environment variable
- [ ] `docker-compose.yml` backend `DATABASE_URL` points to Cloud SQL Proxy
- [ ] `.env` file exists and contains all required variables
- [ ] `.env` file is NOT committed to version control (check `.gitignore`)
- [ ] `gcp-service-account.json` is NOT committed (if using file-based auth)

### Security

- [ ] `.env` file is not in version control
- [ ] `gcp-service-account.json` is not in version control (if used)
- [ ] JWT_SECRET is unique and not shared with other environments
- [ ] Database passwords are strong and unique
- [ ] CORS_ORIGINS does not include development URLs

## Docker and Infrastructure

### Docker Setup

- [ ] Docker is installed and running
- [ ] Docker Compose is installed (version 3.8+)
- [ ] Port 8000 is available (or change in docker-compose.yml)
- [ ] Port 5433 is available (or change in docker-compose.yml)

### Network and Connectivity

- [ ] Server has internet access (for pulling Docker images)
- [ ] Server can reach Google Cloud Platform
- [ ] Firewall allows outbound connections to GCP
- [ ] If using service account key, file permissions are correct (read-only)

## Pre-Deployment Testing

### Local Build Test

- [ ] Docker build succeeds: `docker build -t mainmeal-backend .`
- [ ] No build errors or warnings
- [ ] All dependencies install correctly

### Service Startup Test

- [ ] Cloud SQL Proxy service starts: `docker-compose up cloud-sql-proxy -d`
- [ ] Cloud SQL Proxy connects to Cloud SQL instance
- [ ] Backend service can connect to Cloud SQL via proxy
- [ ] All services start without errors: `docker-compose up -d`

### Health Checks

- [ ] Health endpoint responds: `curl http://localhost:8000/health`
  - Expected: `{"status": "healthy"}`
- [ ] Root endpoint responds: `curl http://localhost:8000/`
  - Expected: `{"message": "MainMeal API is running", "version": "1.0.0"}`
- [ ] Database schema is created (check logs for success message)
- [ ] API documentation accessible: `http://localhost:8000/docs`

### Log Verification

- [ ] Backend logs show no errors
- [ ] Cloud SQL Proxy logs show successful connection
- [ ] Database initialization successful in logs
- [ ] No authentication errors in logs

## Production Readiness

### Performance

- [ ] Uvicorn workers configured (4 workers in Dockerfile)
- [ ] Database connection pool settings appropriate
- [ ] Rate limiting configured (if custom limits needed)

### Monitoring

- [ ] Health check endpoint working (`/health`)
- [ ] Logs are accessible and readable
- [ ] Error tracking configured (if applicable)

### Documentation

- [ ] Deployment documentation reviewed (`DEPLOYMENT.md`)
- [ ] Team members know how to access logs
- [ ] Team members know how to restart services
- [ ] Emergency contact information documented

## Post-Deployment Verification

After deployment, verify:

- [ ] All services running: `docker-compose ps`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] API endpoints respond correctly
- [ ] Database operations work (test a simple API call)
- [ ] CORS headers are correct (test from frontend)
- [ ] Authentication works (test login endpoint)
- [ ] AI features work (test with GEMINI_API_KEY)

## Rollback Plan

- [ ] Previous version backup available
- [ ] Rollback procedure documented
- [ ] Database migration rollback plan (if applicable)

## Notes

Use this section to document any environment-specific configurations or issues:

```
Date: ___________
Deployed by: ___________
Environment: ___________
Notes:
_________________________________________________
_________________________________________________
_________________________________________________
```

## Quick Verification Commands

```bash
# Check all services are running
docker-compose ps

# Check backend logs
docker-compose logs backend | tail -50

# Check Cloud SQL Proxy logs
docker-compose logs cloud-sql-proxy | tail -50

# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# Verify environment variables are set
docker-compose exec backend env | grep -E "(DATABASE_URL|JWT_SECRET|GEMINI_API_KEY|CORS_ORIGINS)"
```

---

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Blocked

**Last Updated:** ___________
