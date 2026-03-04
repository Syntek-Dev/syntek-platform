# Production Environment Commands

## Deployment

```bash
# Deploy to production (requires proper access)
# This should typically be done through CI/CD pipeline

# Emergency manual deployment
docker-compose -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.prod.yml up -d --no-deps backend
docker-compose -f docker/docker-compose.prod.yml up -d --no-deps frontend
docker-compose -f docker/docker-compose.prod.yml up -d --no-deps security
```

## Database Operations

```bash
# Run migrations (with zero-downtime strategy)
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py migrate --check
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py migrate

# Create database backup before operations
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U postgres syntek_cms | gzip > "backup_$(date +%Y%m%d_%H%M%S).sql.gz"
```

## Monitoring and Health Checks

```bash
# Check service health
curl https://api.syntek-cms.com/health/
curl https://app.syntek-cms.com/health/
curl https://auth.syntek-cms.com/health/

# View production logs (limited access)
docker-compose -f docker/docker-compose.prod.yml logs --tail=100 backend
docker-compose -f docker/docker-compose.prod.yml logs --tail=100 security

# Monitor GraphQL performance
curl -X POST https://api.syntek-cms.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"query": "query { __schema { queryType { name } } }"}'
```

## Performance Monitoring

```bash
# Check database performance
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U postgres syntek_cms -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Monitor API response times
# Access Grafana dashboard: https://monitoring.syntek-cms.com

# Check Redis cache hit rates
docker-compose -f docker/docker-compose.prod.yml exec redis redis-cli INFO stats
```

## Security Operations

```bash
# Rotate JWT secrets (requires coordination)
# 1. Generate new secret
# 2. Update backend configuration
# 3. Update security layer configuration
# 4. Rolling restart services

# Check security logs
docker-compose -f docker/docker-compose.prod.yml exec security journalctl -u auth-service --since "1 hour ago"

# SSL certificate renewal (automated via Let's Encrypt)
# Manual renewal if needed:
# certbot renew --nginx
```

## Backup Operations

```bash
# Automated daily backup (runs via cron)
# Manual backup for emergency situations
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U postgres syntek_cms | \
  gzip | \
  aws s3 cp - s3://syntek-cms-backups/manual/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup user uploads
docker-compose -f docker/docker-compose.prod.yml exec backend tar -czf - media/ | \
  aws s3 cp - s3://syntek-cms-backups/media/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz
```

## Emergency Procedures

```bash
# Emergency rollback (requires previous image tags)
docker-compose -f docker/docker-compose.prod.yml pull syntek/cms-backend:previous
docker-compose -f docker/docker-compose.prod.yml up -d --no-deps backend

# Emergency database restore
# 1. Stop application services
docker-compose -f docker/docker-compose.prod.yml stop backend frontend security

# 2. Restore database
zcat backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U postgres syntek_cms

# 3. Restart services
docker-compose -f docker/docker-compose.prod.yml up -d

# Emergency scale up (for traffic spikes)
docker-compose -f docker/docker-compose.prod.yml up -d --scale backend=3 --scale security=2
```

## Maintenance

```bash
# Planned maintenance mode
# 1. Enable maintenance page
# 2. Stop application services
# 3. Perform maintenance
# 4. Restart services
# 5. Disable maintenance page

# Clear application caches
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py clear_cache
docker-compose -f docker/docker-compose.prod.yml exec redis redis-cli FLUSHDB

# Update dependencies (in maintenance window)
# This should be tested in staging first
docker-compose -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Troubleshooting

```bash
# Check system resources
docker stats
df -h
free -m

# Database connection issues
docker-compose -f docker/docker-compose.prod.yml exec postgres pg_isready -U postgres

# GraphQL API issues
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py shell
# >>> from django.test.client import Client
# >>> client = Client()
# >>> response = client.post('/graphql', {'query': '{ __schema { types { name } } }'})

# Network connectivity
docker-compose -f docker/docker-compose.prod.yml exec backend ping postgres
docker-compose -f docker/docker-compose.prod.yml exec backend ping redis
```

---

**⚠️ Production Commands Warning**
- Always test in staging first
- Have rollback plan ready
- Coordinate with team before major operations
- Monitor system health during and after changes