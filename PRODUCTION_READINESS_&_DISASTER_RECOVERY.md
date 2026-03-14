# Production Readiness & Disaster Recovery Plan
**NexusFlow Engine** — Complete Guide to Never Crash in Production

---

## 1. PRE-DEPLOYMENT CHECKLIST (MUST DO EVERY TIME)

### 1.1 Code Quality Checks
```bash
# Run all tests locally BEFORE deploying
cd apps/engine
python -m pytest tests/ -v

# Check for syntax errors
python -m py_compile apps/engine/main.py

# Check dependencies locally
pip install -r requirements.txt --dry-run
```

### 1.2 Docker Build Validation
```bash
# Build Docker image locally and test
docker build -t nexusflow:test .
docker run -e PORT=8000 -p 8000:8000 nexusflow:test

# Verify it starts without errors
# Verify /health endpoint responds
curl http://localhost:8000/health
```

### 1.3 Configuration Validation
```bash
# Check all config files are correct
cat railway.json      # Should be minimal
cat Dockerfile        # Should use hardcoded PORT
cat .railwayignore    # Should exclude web app
cat entrypoint.sh     # Should exist and be executable
```

### 1.4 Environment Variables
```bash
# Document all required env vars
DATABASE_URL        # Must be valid PostgreSQL URL
SECRET_KEY          # Must be set and random
ALLOWED_ORIGINS     # Should match frontend domain
```

---

## 2. DEPLOYMENT STAGES & BACKUP PLANS

### Stage 1: Building Docker Image
**Primary:** Railway auto-builds from Dockerfile
**Backup Plan A:** Manually build and push to DockerHub
```bash
docker build -t yourdockerhub/nexusflow:v1.0 .
docker push yourdockerhub/nexusflow:v1.0
# Then deploy from DockerHub image instead
```

**Backup Plan B:** Switch to Render.com (often more reliable than Railway)
```
https://render.com
1. Sign up with GitHub
2. Create Web Service → Select Docker
3. Connect repo → Deploy
```

**Backup Plan C:** Use Heroku (simplest)
```
Create Procfile:
web: python -m uvicorn apps.engine.main:app --host 0.0.0.0 --port $PORT
```

### Stage 2: Container Starting
**Primary:** Railway runs Dockerfile CMD
**Backup Plan A:** Direct Python command (no Docker)
```bash
# SSH into Railway container and run directly:
python -m uvicorn apps.engine.main:app --host 0.0.0.0 --port 8000
```

**Backup Plan B:** Use minimal startup script
```bash
#!/bin/bash
cd /app
exec python -m uvicorn apps.engine.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Stage 3: Application Crashes
**Primary:** Monitoring + Auto-restart
```bash
# Add to Dockerfile:
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; assert requests.get('http://localhost:8000/health').status_code == 200"
```

**Backup Plan A:** Manual restart from Railway dashboard
**Backup Plan B:** Use PM2 for process management
**Backup Plan C:** Kubernetes for auto-healing

### Stage 4: Database Connection Fails
**Primary:** Connection pooling + retry logic
```python
# In apps/engine/db/session.py:
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Test connection before use
    pool_recycle=3600,   # Recycle connections hourly
    connect_args={"timeout": 10}
)
```

**Backup Plan A:** Use SQLite as fallback
```python
if not os.getenv('DATABASE_URL'):
    DATABASE_URL = 'sqlite:///./fallback.db'
```

**Backup Plan B:** In-memory cache (Redis) if DB is slow
**Backup Plan C:** Read-only mode if DB goes down

---

## 3. MONITORING & ALERTS

### 3.1 Health Check Endpoint
```python
@app.get("/health")
def health_check():
    """Health check for load balancers"""
    try:
        db.query(User).limit(1).all()  # Test DB connection
        return {
            "status": "healthy",
            "service": "NexusFlow Engine",
            "version": "0.3.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 503
```

### 3.2 Error Logging
```python
# In main.py:
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()  # Also to stdout for Railway
    ]
)

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {"error": "Internal server error", "request_id": request.headers.get("x-request-id")}
```

### 3.3 External Monitoring
```bash
# Option 1: Uptime monitoring (free)
https://betterstack.com/uptime-monitoring
- Monitor: https://your-backend.railway.app/health
- Alert on: Down, Slow response

# Option 2: Error tracking (free tier)
https://sentry.io
- Add to requirements.txt: sentry-sdk
- Initialize in main.py

# Option 3: Log aggregation (free tier)
https://papertrail.com
- Centralized log viewing
```

---

## 4. CRASH PREVENTION PATTERNS

### 4.1 Graceful Degradation
```python
# If external API fails, return cached data
@app.get("/content/trending")
def get_trending(db: Session = Depends(get_db)):
    try:
        # Try to fetch from external API
        trending = fetch_from_external_api()
    except Exception as e:
        logger.warning(f"External API failed, using cache: {e}")
        # Fallback to database cache
        trending = db.query(TrendingCache).first()
        if not trending:
            return {"error": "Service temporarily unavailable", "status": 503}

    return trending
```

### 4.2 Circuit Breaker Pattern
```python
# For risky operations (external APIs)
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.last_failure = None

    def call(self, func, *args, **kwargs):
        if self.failure_count >= self.threshold:
            if time.time() - self.last_failure < self.timeout:
                raise Exception("Circuit breaker is open")
            else:
                self.failure_count = 0

        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure = time.time()
            raise
```

### 4.3 Timeout Protection
```python
# Always set timeouts on external requests
import httpx

client = httpx.Client(timeout=10.0)  # 10 second timeout
response = client.get(url)  # Won't hang forever
```

### 4.4 Rate Limiting (Already Implemented)
```python
# In main.py - prevents overload
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/signup")
@limiter.limit("5/minute")
def signup(email: str):
    # Max 5 signups per minute per IP
    pass
```

---

## 5. DATA BACKUP & RECOVERY

### 5.1 Database Backups
```bash
# Weekly backup to S3
0 2 * * 0 pg_dump $DATABASE_URL | gzip > /backups/db-$(date +%Y%m%d).sql.gz

# Restore from backup
gunzip < /backups/db-20260314.sql.gz | psql $DATABASE_URL
```

### 5.2 Code Rollback Plan
```bash
# If deployment breaks everything:
git revert HEAD              # Revert to previous commit
git push origin main         # Redeploy previous version
```

### 5.3 Environment Variable Backup
```bash
# Save to GitHub Secrets (encrypted)
# Or use Railway's built-in secrets manager
# NEVER commit .env files
```

---

## 6. LOAD TESTING & STRESS TESTS

```bash
# Test with load before going live
pip install locust

# Create locustfile.py:
from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/health")

    @task
    def create_content(self):
        self.client.post("/content/generate", json={...})

# Run: locust -f locustfile.py -u 100 -r 10
```

---

## 7. PRODUCTION CHECKLIST BEFORE GO-LIVE

- [ ] All tests passing locally
- [ ] Docker builds successfully locally
- [ ] `/health` endpoint responds with 200
- [ ] Database connection works
- [ ] All environment variables set in Railway
- [ ] Error logging configured
- [ ] Monitoring set up (Sentry/Better Stack)
- [ ] Backup plan documented (Render.com ready)
- [ ] Load tested (at least 50 concurrent users)
- [ ] CORS configured for frontend domain
- [ ] Rate limiting enabled
- [ ] Secret key is random and strong
- [ ] No hardcoded credentials in code
- [ ] Database has recent backup
- [ ] Rollback procedure tested
- [ ] On-call runbook created

---

## 8. INCIDENT RESPONSE PLAYBOOK

### When Server is Down:

**Step 1: Check Logs (2 min)**
```bash
# In Railway dashboard → Logs tab
# Look for error messages
# Common issues:
# - Database connection failed
# - Out of memory
# - Port already in use
# - Missing environment variable
```

**Step 2: Health Check (1 min)**
```bash
curl https://your-backend.railway.app/health
# If 503 → App is degraded
# If 404 → App crashed
# If timeout → Network issue
```

**Step 3: Restart Container (1 min)**
```bash
# In Railway:
# - Click project
# - Find deployment
# - Click "Restart"
```

**Step 4: Rollback if Necessary (2 min)**
```bash
git revert HEAD
git push origin main
# Railway auto-redeploys
```

**Step 5: Investigate Root Cause**
- Check recent code changes
- Check database status
- Check external API status
- Review error logs in Sentry

---

## 9. DOCUMENTATION FOR TEAM

Keep these files in repo root:
- `PRODUCTION_READINESS_&_DISASTER_RECOVERY.md` (this file)
- `DEPLOYMENT_TO_PRODUCTION_PLAN.md` (step-by-step guide)
- `INCIDENT_RESPONSE_GUIDE.md` (what to do when down)
- `.env.example` (sample environment variables)

---

## 10. DEPLOYMENT WORKFLOW (EVERY TIME)

```bash
# 1. Local validation
pytest tests/ -v
docker build -t test . && docker run -p 8000:8000 test

# 2. Code review (if team)
git push --set-upstream origin feature-branch
# Create PR, get approval

# 3. Merge to main
git checkout main
git merge feature-branch

# 4. Push to GitHub
git push origin main

# 5. Railway auto-deploys
# - Watch deployment logs
# - Verify /health endpoint
# - Test key endpoints

# 6. Monitor for 1 hour
# - Check error logs
# - Monitor response times
# - Verify user reports work

# 7. If issues arise
# - Check logs immediately
# - Restart container
# - Or rollback if critical
```

---

## 11. NEVER DEPLOY WITHOUT TESTING

❌ **DON'T:**
- Deploy without running tests
- Deploy without building Docker locally
- Deploy untested dependencies
- Deploy with hardcoded secrets
- Deploy without backup plan

✅ **DO:**
- Test locally first
- Build Docker image locally
- Verify dependencies exist
- Use environment variables
- Have rollback ready
- Monitor after deploy

---

## Summary: 3-Layer Safety Net

**Layer 1: Prevention** → Tests + Docker build validation
**Layer 2: Detection** → Health checks + Error logging
**Layer 3: Recovery** → Backup platforms + Rollback procedure

With these in place, you'll NEVER have unplanned downtime. 🛡️
