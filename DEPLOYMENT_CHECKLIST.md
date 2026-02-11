# [DEPLOY] Deployment Checklist

## Before Deploying

- [ ] **Get Groq API Key**
  - Sign up at [console.groq.com](https://console.groq.com)
  - Create API key
  - Keep it secure!

- [ ] **Environment Variables Set**
  ```
  GROQ_API_KEY=gsk_xxx...
  DATABASE_URL=postgresql://user:pass@host:5432/dbname
  ENVIRONMENT=production
  ```

- [ ] **Database Ready**
  - PostgreSQL database created
  - Connection string obtained
  - Tables will be auto-created on first run

- [ ] **Code Committed**
  ```bash
  git add .
  git commit -m "Production ready"
  git push origin main
  ```

- [ ] **Dependencies Updated**
  - Check `requirements.txt` is complete
  - All packages installable

- [ ] **Tests Passing**
  ```bash
  pytest tests/ -v
  python test_e2e_manual.py
  ```

## After Deploying

- [ ] **Health Check**
  - Visit: `https://your-app.com/api/v1/health`
  - Should return: `{"status": "healthy"}`

- [ ] **Test API Endpoint**
  ```bash
  curl -X POST https://your-app.com/api/v1/query \
    -H "Content-Type: application/json" \
    -d '{"query": "When is payday?", "user_id": "test_001"}'
  ```

- [ ] **Test Gradio UI**
  - Visit: `https://your-app.com/ui`
  - Try a few queries

- [ ] **Monitor Logs**
  - Check for errors
  - Verify queries are processing

- [ ] **Set Up Monitoring** (Optional)
  - Sentry for error tracking
  - Datadog/NewRelic for performance
  - Uptime monitoring

## Security Checklist

- [ ] **API Keys Secure**
  - Never commit `.env` to git
  - Use environment variables only

- [ ] **HTTPS Enabled**
  - Railway/Render provide this automatically
  - For VPS: Use Let's Encrypt + Nginx

- [ ] **Database Secured**
  - Strong password
  - SSL enabled
  - Firewall rules set

- [ ] **CORS Configured**
  - Check `src/api/app.py` for allowed origins
  - Update for your domain

## Performance Tuning

- [ ] **Enable Caching** (Phase 2)
  - Redis for FAQ cache
  - Vector store caching

- [ ] **Database Indexing**
  - Indexes already defined in models.py
  - Monitor slow queries

- [ ] **CDN** (Optional)
  - CloudFlare for static assets
  - Improve global latency

## Maintenance

- [ ] **Backup Database**
  - Daily backups enabled
  - Test restore process

- [ ] **Update Dependencies**
  ```bash
  pip list --outdated
  pip install --upgrade package-name
  ```

- [ ] **Monitor Usage**
  - Track Groq API usage
  - Monitor database size
  - Watch response times

---

**Ready to deploy!** [SUCCESS]
