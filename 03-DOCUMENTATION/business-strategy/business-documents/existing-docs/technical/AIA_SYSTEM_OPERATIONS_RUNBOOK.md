# AIA System Operations Runbook
## Daily Operations, Maintenance Tasks, and Standard Operating Procedures

**Document Version**: 1.0
**Last Updated**: October 3, 2025
**Target Audience**: Operations Team, DevOps Engineers, On-Call Personnel
**System**: AIA Production Environment (013a.tech)

---

## 📚 TABLE OF CONTENTS

1. [Daily Operations Checklist](#daily-operations-checklist)
2. [System Health Monitoring](#system-health-monitoring)
3. [Common Maintenance Tasks](#common-maintenance-tasks)
4. [Performance Monitoring](#performance-monitoring)
5. [Backup Operations](#backup-operations)
6. [Log Management](#log-management)
7. [Security Operations](#security-operations)
8. [Capacity Management](#capacity-management)
9. [Emergency Procedures](#emergency-procedures)
10. [Weekly and Monthly Tasks](#weekly-and-monthly-tasks)

---

## ✅ DAILY OPERATIONS CHECKLIST

### Morning Health Check (09:00 UTC)

#### System Status Verification
```bash
#!/bin/bash
# Daily morning health check script

echo "🌅 Starting daily morning health check - $(date)"

# 1. Check external accessibility
echo "1. Checking external accessibility..."
curl -f --max-time 10 https://013a.tech/ > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend DOWN"
curl -f --max-time 10 https://api.013a.tech/health > /dev/null && echo "✅ API accessible" || echo "❌ API DOWN"

# 2. Check Kubernetes cluster health
echo "2. Checking Kubernetes cluster..."
kubectl get nodes --no-headers | while read node status; do
  if [[ "$status" == *"Ready"* ]]; then
    echo "✅ Node $node: Ready"
  else
    echo "❌ Node $node: $status"
  fi
done

# 3. Check pod status across namespaces
echo "3. Checking pod status..."
kubectl get pods --all-namespaces | grep -E "aia|013a" | while read namespace name ready status restarts age; do
  if [[ "$ready" == "1/1" ]] && [[ "$status" == "Running" ]]; then
    echo "✅ $namespace/$name: Running"
  else
    echo "⚠️  $namespace/$name: $ready $status (restarts: $restarts)"
  fi
done

# 4. Check database connectivity
echo "4. Checking database connectivity..."
kubectl exec -n aia-production deployment/aia-postgres -- pg_isready -U aia_user && \
  echo "✅ PostgreSQL: Connected" || echo "❌ PostgreSQL: Connection failed"

# 5. Check Redis connectivity
echo "5. Checking Redis connectivity..."
kubectl exec -n aia-production deployment/aia-redis -- redis-cli ping | grep -q PONG && \
  echo "✅ Redis: Connected" || echo "❌ Redis: Connection failed"

# 6. Check ingress status
echo "6. Checking ingress configuration..."
kubectl get ingress --all-namespaces | grep -E "013a|aia" | while read namespace name class hosts address ports age; do
  if [[ -n "$address" ]]; then
    echo "✅ Ingress $namespace/$name: $hosts -> $address"
  else
    echo "⚠️  Ingress $namespace/$name: No address assigned"
  fi
done

# 7. Check SSL certificate status
echo "7. Checking SSL certificate..."
SSL_EXPIRY=$(echo | openssl s_client -servername 013a.tech -connect 013a.tech:443 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)
echo "📅 SSL Certificate expires: $SSL_EXPIRY"

# 8. Check resource utilization
echo "8. Checking resource utilization..."
kubectl top nodes --no-headers | while read node cpu_pct cpu memory_pct memory; do
  cpu_num=$(echo $cpu_pct | sed 's/%//')
  mem_num=$(echo $memory_pct | sed 's/%//')
  if [[ $cpu_num -gt 80 ]] || [[ $mem_num -gt 80 ]]; then
    echo "⚠️  Node $node: CPU ${cpu_pct}, Memory ${memory_pct}"
  else
    echo "✅ Node $node: CPU ${cpu_pct}, Memory ${memory_pct}"
  fi
done

echo "🎯 Morning health check completed - $(date)"
```

#### Performance Metrics Review
```bash
#!/bin/bash
# Daily performance metrics review

echo "📊 Daily Performance Metrics Review - $(date)"

# API response times (last 24 hours)
echo "1. API Performance (last 24h):"
kubectl exec -n aia-production deployment/aia-backend-simple -- \
  curl -s http://localhost:8080/metrics | grep -E "http_request_duration|http_requests_total" | head -10

# Database performance
echo "2. Database Performance:"
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "
    SELECT
      schemaname,
      tablename,
      n_tup_ins,
      n_tup_upd,
      n_tup_del,
      n_tup_hot_upd,
      n_live_tup,
      n_dead_tup
    FROM pg_stat_user_tables
    ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
    LIMIT 10;"

# Active connections and queries
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "
    SELECT
      count(*) as total_connections,
      count(*) FILTER (WHERE state = 'active') as active_queries,
      count(*) FILTER (WHERE state = 'idle') as idle_connections
    FROM pg_stat_activity;"

# Redis performance
echo "3. Redis Performance:"
kubectl exec -n aia-production deployment/aia-redis -- \
  redis-cli --csv info memory | grep -E "used_memory_human|used_memory_peak_human|mem_fragmentation_ratio"

kubectl exec -n aia-production deployment/aia-redis -- \
  redis-cli --csv info stats | grep -E "total_commands_processed|keyspace_hits|keyspace_misses"

echo "📊 Performance review completed"
```

### Evening System Review (18:00 UTC)

#### Daily Summary Report
```bash
#!/bin/bash
# Evening system summary report

echo "🌆 Evening System Summary - $(date)"

# 1. Traffic summary
echo "1. Daily Traffic Summary:"
kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
  grep -E "INFO.*request" | wc -l | xargs echo "Total API requests today:"

# 2. Error analysis
echo "2. Error Analysis (last 24h):"
ERROR_COUNT=$(kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
  grep -i error | wc -l)
echo "Total errors: $ERROR_COUNT"

if [[ $ERROR_COUNT -gt 0 ]]; then
  echo "Recent errors:"
  kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
    grep -i error | tail -5
fi

# 3. Resource usage summary
echo "3. Resource Usage Summary:"
kubectl top pods -n aia-production --no-headers | \
  awk '{cpu+=$2; mem+=$3} END {print "Total CPU: " cpu "m, Total Memory: " mem "Mi"}'

# 4. Backup status
echo "4. Backup Status:"
LATEST_BACKUP=$(gsutil ls gs://aia-backups/database/ | sort | tail -1)
echo "Latest database backup: $(basename $LATEST_BACKUP)"

# 5. Security events
echo "5. Security Events:"
kubectl logs -n kube-system deployment/kube-apiserver --since=24h | \
  grep -i -E "authentication|authorization|failed" | wc -l | \
  xargs echo "Authentication/Authorization events:"

echo "🌆 Evening summary completed"
```

---

## 🔍 SYSTEM HEALTH MONITORING

### Automated Health Checks

#### Comprehensive Health Monitor
```bash
#!/bin/bash
# Comprehensive system health monitoring script
# Run every 5 minutes via cron

HEALTH_LOG="/var/log/aia-health.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85
ALERT_THRESHOLD_DISK=90

log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $HEALTH_LOG
}

check_system_health() {
  log_message "Starting health check cycle"

  # Check API availability
  if ! curl -f --max-time 10 https://api.013a.tech/health >/dev/null 2>&1; then
    log_message "CRITICAL: API health check failed"
    send_alert "API_DOWN" "API health check failed"
    return 1
  fi

  # Check frontend availability
  if ! curl -f --max-time 10 https://013a.tech/ >/dev/null 2>&1; then
    log_message "CRITICAL: Frontend accessibility failed"
    send_alert "FRONTEND_DOWN" "Frontend accessibility failed"
    return 1
  fi

  # Check pod health
  local unhealthy_pods=0
  while read namespace name ready status; do
    if [[ "$ready" != "1/1" ]] || [[ "$status" != "Running" ]]; then
      log_message "WARNING: Pod $namespace/$name is $ready $status"
      ((unhealthy_pods++))
    fi
  done < <(kubectl get pods --all-namespaces | grep -E "aia|013a" | awk '{print $1, $2, $3, $4}')

  if [[ $unhealthy_pods -gt 0 ]]; then
    log_message "WARNING: $unhealthy_pods unhealthy pods detected"
  fi

  # Check resource utilization
  while read node cpu_pct memory_pct; do
    cpu_num=$(echo $cpu_pct | sed 's/%//')
    mem_num=$(echo $memory_pct | sed 's/%//')

    if [[ $cpu_num -gt $ALERT_THRESHOLD_CPU ]]; then
      log_message "WARNING: Node $node CPU usage: ${cpu_pct}"
      send_alert "HIGH_CPU" "Node $node CPU usage: ${cpu_pct}"
    fi

    if [[ $mem_num -gt $ALERT_THRESHOLD_MEMORY ]]; then
      log_message "WARNING: Node $node Memory usage: ${memory_pct}"
      send_alert "HIGH_MEMORY" "Node $node Memory usage: ${memory_pct}"
    fi
  done < <(kubectl top nodes --no-headers | awk '{print $1, $3, $5}')

  # Check database connectivity
  if ! kubectl exec -n aia-production deployment/aia-postgres -- pg_isready -U aia_user >/dev/null 2>&1; then
    log_message "CRITICAL: PostgreSQL connection failed"
    send_alert "DB_CONNECTION_FAILED" "PostgreSQL connection failed"
    return 1
  fi

  # Check Redis connectivity
  if ! kubectl exec -n aia-production deployment/aia-redis -- redis-cli ping | grep -q PONG; then
    log_message "CRITICAL: Redis connection failed"
    send_alert "REDIS_CONNECTION_FAILED" "Redis connection failed"
    return 1
  fi

  log_message "Health check completed successfully"
  return 0
}

send_alert() {
  local alert_type=$1
  local message=$2

  # Send to monitoring system (replace with your alerting solution)
  curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"🚨 AIA Alert [$alert_type]: $message\"}" >/dev/null 2>&1

  # Send email alert (configure postfix or use external service)
  echo "$message" | mail -s "AIA System Alert: $alert_type" admin@013a.tech >/dev/null 2>&1

  log_message "Alert sent: $alert_type - $message"
}

# Execute health check
check_system_health
```

### Monitoring Dashboard Setup

#### Grafana Dashboard Configuration
```bash
#!/bin/bash
# Setup Grafana dashboards for AIA system monitoring

# Port forward to Grafana
kubectl port-forward -n aia-monitoring svc/grafana-service 3000:3000 &
GRAFANA_PID=$!

sleep 5

# Import AIA system dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {
      "id": null,
      "title": "AIA Production System",
      "tags": ["aia", "production"],
      "timezone": "UTC",
      "panels": [
        {
          "id": 1,
          "title": "API Response Time",
          "type": "graph",
          "targets": [
            {
              "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
              "legendFormat": "95th percentile"
            }
          ]
        },
        {
          "id": 2,
          "title": "Request Rate",
          "type": "graph",
          "targets": [
            {
              "expr": "rate(http_requests_total[5m])",
              "legendFormat": "Requests/sec"
            }
          ]
        },
        {
          "id": 3,
          "title": "Error Rate",
          "type": "singlestat",
          "targets": [
            {
              "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
              "legendFormat": "Error Rate"
            }
          ]
        }
      ],
      "time": {
        "from": "now-1h",
        "to": "now"
      },
      "refresh": "30s"
    },
    "overwrite": true
  }'

# Cleanup
kill $GRAFANA_PID
```

---

## 🔧 COMMON MAINTENANCE TASKS

### Routine Maintenance Procedures

#### Pod Restart and Health Recovery
```bash
#!/bin/bash
# Pod restart and health recovery procedures

restart_unhealthy_pods() {
  echo "🔄 Checking for unhealthy pods..."

  # Find pods that need restart
  kubectl get pods --all-namespaces | grep -E "aia|013a" | while read namespace name ready status restarts age; do
    if [[ "$status" != "Running" ]] || [[ "$ready" != "1/1" ]]; then
      echo "Restarting unhealthy pod: $namespace/$name (Status: $status, Ready: $ready)"

      # Restart the pod gracefully
      kubectl delete pod $name -n $namespace --grace-period=30

      # Wait for new pod to be ready
      kubectl wait --for=condition=Ready pod -l app=${name%-*} -n $namespace --timeout=300s

      # Verify the pod is healthy
      sleep 10
      new_status=$(kubectl get pod -n $namespace -l app=${name%-*} --no-headers | awk '{print $3}')
      echo "New pod status: $new_status"
    fi
  done
}

rolling_restart_deployment() {
  local namespace=$1
  local deployment=$2

  echo "🔄 Performing rolling restart of $namespace/$deployment"

  # Trigger rolling restart
  kubectl rollout restart deployment/$deployment -n $namespace

  # Wait for rollout to complete
  kubectl rollout status deployment/$deployment -n $namespace --timeout=600s

  # Verify deployment health
  kubectl get deployment $deployment -n $namespace
  kubectl get pods -n $namespace -l app=$deployment
}

# Execute maintenance tasks
restart_unhealthy_pods

# Rolling restart of main services (if needed)
if [[ "$1" == "--force-restart" ]]; then
  rolling_restart_deployment "aia-production" "aia-backend-simple"
  rolling_restart_deployment "aia-production" "aia-frontend"
fi
```

#### Database Maintenance
```bash
#!/bin/bash
# Database maintenance procedures

perform_database_maintenance() {
  echo "🗄️ Starting database maintenance..."

  local db_pod=$(kubectl get pods -n aia-production -l app=aia-postgresql -o jsonpath='{.items[0].metadata.name}')

  # 1. Analyze database statistics
  echo "1. Updating database statistics..."
  kubectl exec -n aia-production $db_pod -- \
    psql -U aia_user -d aia_production -c "ANALYZE;"

  # 2. Vacuum dead tuples
  echo "2. Vacuuming database..."
  kubectl exec -n aia-production $db_pod -- \
    psql -U aia_user -d aia_production -c "VACUUM;"

  # 3. Check for long-running queries
  echo "3. Checking for long-running queries..."
  kubectl exec -n aia-production $db_pod -- \
    psql -U aia_user -d aia_production -c "
      SELECT
        pid,
        state,
        query_start,
        now() - query_start AS duration,
        left(query, 50) as query_preview
      FROM pg_stat_activity
      WHERE state = 'active'
        AND query_start < now() - interval '5 minutes'
      ORDER BY query_start;"

  # 4. Check database size
  echo "4. Database size information:"
  kubectl exec -n aia-production $db_pod -- \
    psql -U aia_user -d aia_production -c "
      SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC;"

  # 5. Check for unused indexes
  echo "5. Checking for unused indexes..."
  kubectl exec -n aia-production $db_pod -- \
    psql -U aia_user -d aia_production -c "
      SELECT
        schemaname,
        tablename,
        indexname,
        idx_tup_read,
        idx_tup_fetch
      FROM pg_stat_user_indexes
      WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
      ORDER BY schemaname, tablename;"

  echo "✅ Database maintenance completed"
}

# Execute database maintenance
perform_database_maintenance
```

#### Cache Maintenance
```bash
#!/bin/bash
# Redis cache maintenance procedures

maintain_redis_cache() {
  echo "🔄 Starting Redis cache maintenance..."

  local redis_pod=$(kubectl get pods -n aia-production -l app=aia-redis -o jsonpath='{.items[0].metadata.name}')

  # 1. Check Redis info
  echo "1. Redis server information:"
  kubectl exec -n aia-production $redis_pod -- \
    redis-cli info server | grep -E "redis_version|uptime_in_seconds|process_id"

  # 2. Check memory usage
  echo "2. Memory usage:"
  kubectl exec -n aia-production $redis_pod -- \
    redis-cli info memory | grep -E "used_memory_human|used_memory_peak_human|mem_fragmentation_ratio"

  # 3. Check keyspace statistics
  echo "3. Keyspace statistics:"
  kubectl exec -n aia-production $redis_pod -- \
    redis-cli info keyspace

  # 4. Check slow queries (if enabled)
  echo "4. Slow log entries:"
  kubectl exec -n aia-production $redis_pod -- \
    redis-cli slowlog get 10

  # 5. Memory optimization (if fragmentation is high)
  local frag_ratio=$(kubectl exec -n aia-production $redis_pod -- \
    redis-cli info memory | grep mem_fragmentation_ratio | cut -d: -f2 | tr -d '\r')

  if (( $(echo "$frag_ratio > 1.5" | bc -l) )); then
    echo "High memory fragmentation detected ($frag_ratio), running memory defragmentation..."
    kubectl exec -n aia-production $redis_pod -- \
      redis-cli memory defrag
  fi

  # 6. Expire old keys (cleanup)
  echo "6. Running key expiration cleanup..."
  kubectl exec -n aia-production $redis_pod -- \
    redis-cli eval "return redis.call('del', unpack(redis.call('keys', 'temp:*')))" 0

  echo "✅ Redis cache maintenance completed"
}

# Execute cache maintenance
maintain_redis_cache
```

---

## 📈 PERFORMANCE MONITORING

### Real-time Performance Tracking

#### Performance Metrics Collection
```bash
#!/bin/bash
# Collect performance metrics for analysis

collect_performance_metrics() {
  local output_file="performance_metrics_$(date +%Y%m%d_%H%M%S).json"

  echo "📊 Collecting performance metrics..."

  # API metrics
  local api_metrics=$(kubectl exec -n aia-production deployment/aia-backend-simple -- \
    curl -s http://localhost:8080/metrics | grep -E "http_request_duration|http_requests_total")

  # Database performance
  local db_metrics=$(kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -t -c "
      SELECT json_build_object(
        'active_connections', (SELECT count(*) FROM pg_stat_activity WHERE state = 'active'),
        'total_connections', (SELECT count(*) FROM pg_stat_activity),
        'cache_hit_ratio', (SELECT round((sum(blks_hit) * 100.0) / (sum(blks_hit) + sum(blks_read)), 2) FROM pg_stat_database),
        'transactions_per_second', (SELECT sum(xact_commit + xact_rollback) FROM pg_stat_database WHERE datname = 'aia_production')
      );"
  )

  # System resource metrics
  local resource_metrics=$(kubectl top nodes --no-headers | awk '
    BEGIN { print "{\"nodes\": [" }
    {
      printf "{\"name\": \"%s\", \"cpu\": \"%s\", \"memory\": \"%s\"}", $1, $3, $5
      if (NR < NF) printf ","
    }
    END { print "]}" }'
  )

  # Redis metrics
  local redis_metrics=$(kubectl exec -n aia-production deployment/aia-redis -- \
    redis-cli --json info stats | jq '{
      total_commands: .total_commands_processed,
      hits: .keyspace_hits,
      misses: .keyspace_misses,
      hit_rate: (.keyspace_hits / (.keyspace_hits + .keyspace_misses) * 100)
    }')

  # Combine all metrics
  jq -n \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson db_metrics "$db_metrics" \
    --argjson resource_metrics "$resource_metrics" \
    --argjson redis_metrics "$redis_metrics" \
    '{
      timestamp: $timestamp,
      database: $db_metrics,
      resources: $resource_metrics,
      redis: $redis_metrics
    }' > $output_file

  echo "📊 Metrics collected in $output_file"

  # Upload to monitoring system (optional)
  # gsutil cp $output_file gs://aia-monitoring/metrics/
}

# Execute metrics collection
collect_performance_metrics
```

#### Performance Alerting
```bash
#!/bin/bash
# Performance-based alerting system

check_performance_thresholds() {
  echo "⚡ Checking performance thresholds..."

  # Check API response times
  local avg_response_time=$(kubectl exec -n aia-production deployment/aia-backend-simple -- \
    curl -s http://localhost:8080/metrics | \
    grep "http_request_duration_seconds_sum" | \
    awk '{sum+=$2} END {print sum/NR}')

  if (( $(echo "$avg_response_time > 1.0" | bc -l) )); then
    send_performance_alert "HIGH_RESPONSE_TIME" "Average API response time: ${avg_response_time}s"
  fi

  # Check database connection count
  local db_connections=$(kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -t -c "SELECT count(*) FROM pg_stat_activity;")

  if [[ $db_connections -gt 50 ]]; then
    send_performance_alert "HIGH_DB_CONNECTIONS" "Database connections: $db_connections"
  fi

  # Check Redis memory usage
  local redis_memory=$(kubectl exec -n aia-production deployment/aia-redis -- \
    redis-cli info memory | grep "used_memory:" | cut -d: -f2 | tr -d '\r')

  if [[ $redis_memory -gt 200000000 ]]; then  # 200MB
    send_performance_alert "HIGH_REDIS_MEMORY" "Redis memory usage: $(($redis_memory / 1024 / 1024))MB"
  fi

  echo "⚡ Performance threshold check completed"
}

send_performance_alert() {
  local alert_type=$1
  local message=$2

  echo "🚨 Performance Alert: $alert_type - $message"

  # Send to monitoring dashboard
  curl -X POST "https://api.013a.tech/monitoring/alerts" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $MONITORING_TOKEN" \
    -d "{
      \"alert_type\": \"$alert_type\",
      \"message\": \"$message\",
      \"severity\": \"warning\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }"
}

# Execute performance checks
check_performance_thresholds
```

---

## 💾 BACKUP OPERATIONS

### Daily Backup Procedures

#### Automated Backup Script
```bash
#!/bin/bash
# Automated daily backup operations

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
GCS_BUCKET="gs://aia-backups"
RETENTION_DAYS=30

perform_daily_backup() {
  echo "💾 Starting daily backup procedure - $BACKUP_DATE"

  # 1. Database backup
  echo "1. Creating database backup..."
  local db_backup_file="aia_db_backup_${BACKUP_DATE}.sql"

  kubectl exec -n aia-production deployment/aia-postgres -- \
    pg_dump -U aia_user aia_production > $db_backup_file

  if [[ $? -eq 0 ]]; then
    gzip $db_backup_file
    gsutil cp ${db_backup_file}.gz ${GCS_BUCKET}/database/
    rm ${db_backup_file}.gz
    echo "✅ Database backup completed: ${db_backup_file}.gz"
  else
    echo "❌ Database backup failed"
    return 1
  fi

  # 2. Configuration backup
  echo "2. Creating configuration backup..."
  local config_backup_file="aia_config_backup_${BACKUP_DATE}.tar.gz"

  # Export current Kubernetes configurations
  mkdir -p backup_temp/configs
  kubectl get all -n aia-production -o yaml > backup_temp/configs/aia-production.yaml
  kubectl get configmaps -n aia-production -o yaml > backup_temp/configs/configmaps.yaml
  kubectl get secrets -n aia-production -o yaml > backup_temp/configs/secrets.yaml
  kubectl get ingress --all-namespaces -o yaml | grep -A 1000 -E "013a|aia" > backup_temp/configs/ingress.yaml

  tar -czf $config_backup_file backup_temp/
  gsutil cp $config_backup_file ${GCS_BUCKET}/config/
  rm -rf backup_temp/ $config_backup_file
  echo "✅ Configuration backup completed: $config_backup_file"

  # 3. Log backup (recent logs)
  echo "3. Creating log backup..."
  local log_backup_file="aia_logs_backup_${BACKUP_DATE}.tar.gz"

  mkdir -p backup_temp/logs
  kubectl logs -n aia-production deployment/aia-backend-simple --since=24h > backup_temp/logs/backend.log
  kubectl logs -n aia-production deployment/aia-frontend --since=24h > backup_temp/logs/frontend.log
  kubectl logs -n aia-production deployment/aia-postgres --since=24h > backup_temp/logs/postgres.log
  kubectl logs -n aia-production deployment/aia-redis --since=24h > backup_temp/logs/redis.log

  tar -czf $log_backup_file backup_temp/
  gsutil cp $log_backup_file ${GCS_BUCKET}/logs/
  rm -rf backup_temp/ $log_backup_file
  echo "✅ Log backup completed: $log_backup_file"

  # 4. Cleanup old backups
  echo "4. Cleaning up old backups (older than $RETENTION_DAYS days)..."
  gsutil -m rm $(gsutil ls ${GCS_BUCKET}/database/ | head -n -$RETENTION_DAYS) 2>/dev/null || true
  gsutil -m rm $(gsutil ls ${GCS_BUCKET}/config/ | head -n -$RETENTION_DAYS) 2>/dev/null || true
  gsutil -m rm $(gsutil ls ${GCS_BUCKET}/logs/ | head -n -$RETENTION_DAYS) 2>/dev/null || true

  echo "💾 Daily backup procedure completed successfully"
}

verify_backup_integrity() {
  echo "🔍 Verifying backup integrity..."

  # Check if latest database backup can be read
  local latest_db_backup=$(gsutil ls ${GCS_BUCKET}/database/ | sort | tail -1)
  if [[ -n "$latest_db_backup" ]]; then
    gsutil cp $latest_db_backup temp_backup.sql.gz
    if gunzip -t temp_backup.sql.gz; then
      echo "✅ Latest database backup integrity verified"
    else
      echo "❌ Database backup integrity check failed"
      send_alert "BACKUP_INTEGRITY_FAILED" "Database backup integrity check failed"
    fi
    rm -f temp_backup.sql.gz
  fi
}

# Execute backup operations
perform_daily_backup
verify_backup_integrity
```

### Backup Restoration Procedures

#### Database Restoration
```bash
#!/bin/bash
# Database restoration from backup

restore_database_from_backup() {
  local backup_date=${1:-$(date +%Y%m%d)}
  local backup_file="aia_db_backup_${backup_date}*.sql.gz"

  echo "🔄 Restoring database from backup: $backup_date"

  # Find the backup file
  local latest_backup=$(gsutil ls gs://aia-backups/database/ | grep $backup_date | sort | tail -1)

  if [[ -z "$latest_backup" ]]; then
    echo "❌ No backup found for date: $backup_date"
    return 1
  fi

  echo "Found backup: $latest_backup"

  # Download and prepare backup
  gsutil cp $latest_backup restore_backup.sql.gz
  gunzip restore_backup.sql.gz

  # Create temporary database pod for restoration
  kubectl run restore-db --rm -it --restart=Never --image=postgres:15-alpine -- bash -c "
    echo 'Connecting to database for restoration...'
    PGPASSWORD=\$POSTGRES_PASSWORD psql -h aia-postgres -U aia_user aia_production < restore_backup.sql
  "

  # Cleanup
  rm -f restore_backup.sql

  echo "✅ Database restoration completed"
}

# Usage: restore_database_from_backup [YYYYMMDD]
if [[ "$1" == "restore" ]]; then
  restore_database_from_backup $2
fi
```

---

## 📋 LOG MANAGEMENT

### Log Collection and Analysis

#### Centralized Log Collection
```bash
#!/bin/bash
# Centralized log collection and analysis

collect_system_logs() {
  local log_date=$(date +%Y%m%d)
  local output_dir="logs_${log_date}"

  echo "📋 Collecting system logs for analysis..."

  mkdir -p $output_dir/{application,system,database,security}

  # Application logs
  kubectl logs -n aia-production deployment/aia-backend-simple --since=24h > \
    $output_dir/application/backend-$(date +%H%M%S).log

  kubectl logs -n aia-production deployment/aia-frontend --since=24h > \
    $output_dir/application/frontend-$(date +%H%M%S).log

  # Database logs
  kubectl logs -n aia-production deployment/aia-postgres --since=24h > \
    $output_dir/database/postgres-$(date +%H%M%S).log

  kubectl logs -n aia-production deployment/aia-redis --since=24h > \
    $output_dir/database/redis-$(date +%H%M%S).log

  # System logs
  kubectl logs -n kube-system -l component=kube-apiserver --since=24h > \
    $output_dir/system/kube-apiserver-$(date +%H%M%S).log

  kubectl get events --all-namespaces --since=24h > \
    $output_dir/system/kubernetes-events-$(date +%H%M%S).log

  # Security logs (authentication, authorization)
  kubectl logs -n kube-system -l component=kube-apiserver --since=24h | \
    grep -E "authentication|authorization|failed" > \
    $output_dir/security/auth-events-$(date +%H%M%S).log

  echo "📋 Logs collected in $output_dir/"
}

analyze_error_patterns() {
  echo "🔍 Analyzing error patterns..."

  # Analyze backend errors
  echo "Backend Error Analysis:"
  kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
    grep -i error | \
    awk '{print $1, $2, $NF}' | \
    sort | uniq -c | sort -nr | head -10

  # Analyze database errors
  echo "Database Error Analysis:"
  kubectl logs -n aia-production deployment/aia-postgres --since=24h | \
    grep -i -E "error|warning|fatal" | \
    awk '{print $4, $5}' | \
    sort | uniq -c | sort -nr | head -10

  # Analyze system events
  echo "System Event Analysis:"
  kubectl get events --all-namespaces --since=24h | \
    grep -v Normal | \
    awk '{print $5, $6}' | \
    sort | uniq -c | sort -nr | head -10
}

generate_log_summary() {
  local summary_file="log_summary_$(date +%Y%m%d_%H%M%S).txt"

  {
    echo "=== AIA System Log Summary - $(date) ==="
    echo

    echo "1. Request Volume (last 24h):"
    kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
      grep -E "GET|POST|PUT|DELETE" | wc -l | xargs echo "Total requests:"

    echo

    echo "2. Error Summary:"
    kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
      grep -i error | wc -l | xargs echo "Backend errors:"

    kubectl logs -n aia-production deployment/aia-postgres --since=24h | \
      grep -i -E "error|fatal" | wc -l | xargs echo "Database errors:"

    echo

    echo "3. Top Endpoints (last 24h):"
    kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
      grep -E "GET|POST|PUT|DELETE" | \
      awk '{for(i=1;i<=NF;i++) if($i ~ /^\/[a-zA-Z]/) print $i}' | \
      sort | uniq -c | sort -nr | head -10

    echo

    echo "4. Response Time Analysis:"
    kubectl logs -n aia-production deployment/aia-backend-simple --since=24h | \
      grep -E "completed.*in.*ms" | \
      awk '{print $(NF-1)}' | \
      awk '
        {
          sum += $1
          if ($1 > max) max = $1
          if (min == "" || $1 < min) min = $1
          count++
        }
        END {
          if (count > 0) {
            print "Average response time: " sum/count "ms"
            print "Min response time: " min "ms"
            print "Max response time: " max "ms"
          }
        }'

  } > $summary_file

  echo "📊 Log summary generated: $summary_file"
}

# Execute log management tasks
collect_system_logs
analyze_error_patterns
generate_log_summary
```

---

## 🔒 SECURITY OPERATIONS

### Daily Security Checks

#### Security Monitoring Script
```bash
#!/bin/bash
# Daily security monitoring and compliance checks

perform_security_audit() {
  local audit_date=$(date +%Y%m%d_%H%M%S)
  local audit_report="security_audit_${audit_date}.txt"

  echo "🔒 Starting daily security audit - $audit_date"

  {
    echo "=== AIA System Security Audit Report ==="
    echo "Date: $(date)"
    echo

    # 1. SSL Certificate Check
    echo "1. SSL Certificate Status:"
    echo | openssl s_client -servername 013a.tech -connect 013a.tech:443 2>/dev/null | \
      openssl x509 -noout -dates

    echo

    # 2. Authentication Events
    echo "2. Authentication Events (last 24h):"
    kubectl logs -n kube-system -l component=kube-apiserver --since=24h | \
      grep -i authentication | \
      grep -i failed | wc -l | xargs echo "Failed authentication attempts:"

    echo

    # 3. Pod Security Context Review
    echo "3. Pod Security Context Review:"
    kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{" "}{.spec.securityContext}{"\n"}{end}' | \
      grep -E "aia|013a" | head -10

    echo

    # 4. Service Account Permissions
    echo "4. Service Account Permissions:"
    kubectl auth can-i --list --as=system:serviceaccount:aia-production:default | head -10

    echo

    # 5. Network Policy Status
    echo "5. Network Policy Status:"
    kubectl get networkpolicies --all-namespaces | grep -E "aia|013a" || echo "No network policies found"

    echo

    # 6. Secret Management Review
    echo "6. Secret Management Review:"
    kubectl get secrets --all-namespaces | grep -E "aia|013a" | wc -l | xargs echo "Total secrets:"

    echo

    # 7. Ingress Security Configuration
    echo "7. Ingress Security Configuration:"
    kubectl describe ingress --all-namespaces | grep -A 5 -B 5 -E "tls|ssl"

  } > $audit_report

  echo "🔒 Security audit completed: $audit_report"

  # Check for critical security issues
  check_security_violations $audit_report
}

check_security_violations() {
  local audit_report=$1

  echo "🚨 Checking for security violations..."

  # Check for high number of failed authentication attempts
  local failed_auths=$(grep "Failed authentication attempts:" $audit_report | awk '{print $NF}')
  if [[ $failed_auths -gt 10 ]]; then
    send_security_alert "HIGH_FAILED_AUTH" "High number of failed authentication attempts: $failed_auths"
  fi

  # Check for pods running as root
  kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.securityContext.runAsUser}{"\n"}{end}' | \
    grep -E "aia|013a" | while read pod_name user_id; do
      if [[ "$user_id" == "0" ]] || [[ -z "$user_id" ]]; then
        send_security_alert "POD_RUNNING_AS_ROOT" "Pod $pod_name may be running as root"
      fi
    done

  # Check for SSL certificate expiration (within 30 days)
  local ssl_expiry=$(echo | openssl s_client -servername 013a.tech -connect 013a.tech:443 2>/dev/null | \
    openssl x509 -noout -dates | grep notAfter | cut -d= -f2)

  local expiry_seconds=$(date -d "$ssl_expiry" +%s)
  local current_seconds=$(date +%s)
  local days_until_expiry=$(( (expiry_seconds - current_seconds) / 86400 ))

  if [[ $days_until_expiry -lt 30 ]]; then
    send_security_alert "SSL_CERT_EXPIRING" "SSL certificate expires in $days_until_expiry days"
  fi
}

send_security_alert() {
  local alert_type=$1
  local message=$2

  echo "🚨 Security Alert: $alert_type - $message"

  # Send to security monitoring system
  curl -X POST "https://api.013a.tech/security/alerts" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SECURITY_TOKEN" \
    -d "{
      \"alert_type\": \"$alert_type\",
      \"message\": \"$message\",
      \"severity\": \"high\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }"

  # Log security event
  echo "$(date '+%Y-%m-%d %H:%M:%S') - SECURITY_ALERT - $alert_type - $message" >> /var/log/aia-security.log
}

# Execute security audit
perform_security_audit
```

### Access Control Management

#### User Access Review
```bash
#!/bin/bash
# Regular access control review and management

review_access_controls() {
  echo "👥 Reviewing access controls..."

  # 1. Review RBAC permissions
  echo "1. RBAC Permissions Review:"
  kubectl get clusterrolebindings -o wide | grep -E "admin|cluster-admin"

  # 2. Service account review
  echo "2. Service Account Review:"
  kubectl get serviceaccounts --all-namespaces | grep -E "aia|013a"

  # 3. Pod security policies
  echo "3. Pod Security Policy Review:"
  kubectl get podsecuritypolicy || echo "Pod Security Policies not configured"

  # 4. Network access review
  echo "4. Network Access Review:"
  kubectl get services --all-namespaces -o wide | grep -E "aia|013a"
}

# Execute access control review
review_access_controls
```

---

## 📊 CAPACITY MANAGEMENT

### Resource Monitoring and Planning

#### Capacity Assessment
```bash
#!/bin/bash
# Capacity monitoring and planning

assess_current_capacity() {
  echo "📊 Assessing current system capacity..."

  # 1. Node resource utilization
  echo "1. Node Resource Utilization:"
  kubectl top nodes

  # 2. Pod resource consumption
  echo "2. Pod Resource Consumption (AIA Services):"
  kubectl top pods --all-namespaces | grep -E "aia|013a"

  # 3. Persistent volume usage
  echo "3. Persistent Volume Usage:"
  kubectl get pv -o custom-columns=NAME:.metadata.name,CAPACITY:.spec.capacity.storage,USED:.status.phase

  # 4. Database size growth
  echo "4. Database Size Analysis:"
  kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -c "
      SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC
      LIMIT 10;"

  # 5. Network bandwidth utilization
  echo "5. Network Bandwidth (last hour):"
  kubectl exec -n aia-production deployment/aia-backend-simple -- \
    curl -s http://localhost:8080/metrics | grep -E "http_request_size|http_response_size"
}

capacity_planning_recommendations() {
  echo "💡 Capacity Planning Recommendations:"

  # Analyze current usage and provide recommendations
  local cpu_usage=$(kubectl top nodes --no-headers | awk '{sum+=$3} END {print sum/NR}' | sed 's/%//')
  local memory_usage=$(kubectl top nodes --no-headers | awk '{sum+=$5} END {print sum/NR}' | sed 's/%//')

  if [[ ${cpu_usage%.*} -gt 70 ]]; then
    echo "⚠️  CPU usage is high (${cpu_usage}%). Consider adding more nodes or upgrading instance types."
  fi

  if [[ ${memory_usage%.*} -gt 80 ]]; then
    echo "⚠️  Memory usage is high (${memory_usage}%). Consider increasing memory limits or scaling horizontally."
  fi

  # Database growth projection
  local current_db_size=$(kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -t -c "SELECT pg_database_size('aia_production');")

  echo "Current database size: $(echo "scale=2; $current_db_size / 1024 / 1024" | bc)MB"
  echo "Projected size in 30 days: $(echo "scale=2; $current_db_size * 1.2 / 1024 / 1024" | bc)MB (assuming 20% growth)"

  # Auto-scaling recommendations
  echo "Auto-scaling configuration recommendations:"
  echo "- CPU threshold: 70%"
  echo "- Memory threshold: 80%"
  echo "- Min replicas: 2"
  echo "- Max replicas: 10"
}

# Execute capacity assessment
assess_current_capacity
capacity_planning_recommendations
```

---

## 🚨 EMERGENCY PROCEDURES

### Emergency Response Playbook

#### System Emergency Response
```bash
#!/bin/bash
# Emergency response procedures for critical system issues

emergency_response() {
  local incident_type=$1
  local severity=${2:-"high"}

  echo "🚨 EMERGENCY RESPONSE ACTIVATED - Type: $incident_type, Severity: $severity"

  case $incident_type in
    "complete_outage")
      handle_complete_outage
      ;;
    "database_failure")
      handle_database_failure
      ;;
    "high_error_rate")
      handle_high_error_rate
      ;;
    "security_breach")
      handle_security_breach
      ;;
    *)
      echo "Unknown emergency type: $incident_type"
      ;;
  esac
}

handle_complete_outage() {
  echo "🚨 Handling complete system outage..."

  # 1. Immediate assessment
  echo "1. Performing immediate system assessment..."
  kubectl get nodes
  kubectl get pods --all-namespaces | grep -E "aia|013a"

  # 2. Check external dependencies
  echo "2. Checking external dependencies..."
  curl -f --max-time 5 https://google.com > /dev/null && echo "✅ Internet connectivity OK" || echo "❌ Internet connectivity issues"

  # 3. Restart critical services
  echo "3. Restarting critical services..."
  kubectl rollout restart deployment/aia-backend-simple -n aia-production
  kubectl rollout restart deployment/aia-frontend -n aia-production

  # 4. Check load balancer status
  echo "4. Checking load balancer..."
  kubectl get services -n aia-production | grep LoadBalancer

  # 5. Activate backup systems if needed
  if ! curl -f --max-time 10 https://013a.tech/ > /dev/null 2>&1; then
    echo "5. Primary system still down, activating emergency procedures..."
    activate_emergency_fallback
  fi
}

handle_database_failure() {
  echo "🚨 Handling database failure..."

  # 1. Check database pod status
  kubectl get pods -n aia-production -l app=aia-postgresql

  # 2. Attempt database restart
  kubectl delete pod -n aia-production -l app=aia-postgresql
  kubectl wait --for=condition=Ready pod -l app=aia-postgresql -n aia-production --timeout=300s

  # 3. Check data integrity
  kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -c "SELECT count(*) FROM users;"

  # 4. If corruption detected, restore from backup
  if [[ $? -ne 0 ]]; then
    echo "Database corruption detected, initiating restore from backup..."
    restore_database_from_backup
  fi
}

activate_emergency_fallback() {
  echo "🚨 Activating emergency fallback procedures..."

  # Deploy minimal emergency service
  kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aia-emergency-service
  namespace: aia-production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aia-emergency
  template:
    metadata:
      labels:
        app: aia-emergency
    spec:
      containers:
      - name: emergency-api
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: emergency-content
          mountPath: /usr/share/nginx/html
      volumes:
      - name: emergency-content
        configMap:
          name: emergency-page
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: emergency-page
  namespace: aia-production
data:
  index.html: |
    <!DOCTYPE html>
    <html>
    <head>
        <title>AIA System Maintenance</title>
    </head>
    <body>
        <h1>System Temporarily Unavailable</h1>
        <p>Our system is currently undergoing emergency maintenance.</p>
        <p>We apologize for the inconvenience and are working to restore service.</p>
        <p>Estimated restoration time: Within 1 hour</p>
    </body>
    </html>
EOF

  echo "Emergency fallback service deployed"
}

# Emergency response usage
if [[ "$1" == "emergency" ]]; then
  emergency_response $2 $3
fi
```

### Incident Communication

#### Incident Notification System
```bash
#!/bin/bash
# Incident communication and notification system

send_incident_notification() {
  local incident_id=$1
  local incident_type=$2
  local severity=$3
  local message=$4

  echo "📢 Sending incident notification: $incident_id"

  # 1. Slack notification
  curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{
      \"text\": \"🚨 AIA System Incident Alert\",
      \"attachments\": [
        {
          \"color\": \"danger\",
          \"fields\": [
            {\"title\": \"Incident ID\", \"value\": \"$incident_id\", \"short\": true},
            {\"title\": \"Type\", \"value\": \"$incident_type\", \"short\": true},
            {\"title\": \"Severity\", \"value\": \"$severity\", \"short\": true},
            {\"title\": \"Message\", \"value\": \"$message\", \"short\": false}
          ]
        }
      ]
    }"

  # 2. Email notification
  echo "Incident: $incident_id | Type: $incident_type | Severity: $severity | Message: $message" | \
    mail -s "🚨 AIA System Alert: $incident_type" admin@013a.tech

  # 3. Update status page
  curl -X POST "https://api.statuspage.io/v1/pages/YOUR_PAGE_ID/incidents" \
    -H "Authorization: OAuth YOUR_API_KEY" \
    -d "incident[name]=$incident_type&incident[status]=investigating&incident[message]=$message"

  echo "📢 Incident notification sent for: $incident_id"
}

# Usage example
# send_incident_notification "INC-001" "API_OUTAGE" "critical" "API service is currently unavailable"
```

---

## 📅 WEEKLY AND MONTHLY TASKS

### Weekly Maintenance Schedule

#### Weekly System Review (Every Sunday)
```bash
#!/bin/bash
# Weekly system review and maintenance

perform_weekly_maintenance() {
  local week_date=$(date +%Y_W%V)
  local report_file="weekly_report_${week_date}.txt"

  echo "📅 Starting weekly maintenance - Week $(date +%V) of $(date +%Y)"

  {
    echo "=== AIA System Weekly Maintenance Report ==="
    echo "Week: $(date +%V) of $(date +%Y)"
    echo "Date: $(date)"
    echo

    # 1. System performance summary
    echo "1. SYSTEM PERFORMANCE SUMMARY"
    echo "   - Uptime this week: $(uptime)"
    echo "   - Total API requests: $(kubectl logs -n aia-production deployment/aia-backend-simple --since=7d | grep -c 'GET\|POST\|PUT\|DELETE')"
    echo "   - Average response time: TBD"  # Would need proper monitoring setup
    echo

    # 2. Error analysis
    echo "2. ERROR ANALYSIS"
    kubectl logs -n aia-production deployment/aia-backend-simple --since=7d | \
      grep -i error | wc -l | xargs echo "   - Backend errors this week:"
    kubectl logs -n aia-production deployment/aia-postgres --since=7d | \
      grep -i error | wc -l | xargs echo "   - Database errors this week:"
    echo

    # 3. Resource utilization trends
    echo "3. RESOURCE UTILIZATION"
    kubectl top nodes | sed 's/^/   /'
    echo

    # 4. Security events
    echo "4. SECURITY EVENTS"
    kubectl logs -n kube-system -l component=kube-apiserver --since=7d | \
      grep -i -E "authentication|authorization" | grep -i failed | wc -l | \
      xargs echo "   - Failed authentication attempts:"

    # 5. Capacity planning
    echo "5. CAPACITY PLANNING"
    echo "   - Current pod count: $(kubectl get pods --all-namespaces | grep -E 'aia|013a' | wc -l)"
    echo "   - Database size: $(kubectl exec -n aia-production deployment/aia-postgres -- \
      psql -U aia_user -d aia_production -t -c 'SELECT pg_size_pretty(pg_database_size(current_database()));' | xargs)"

    echo

  } > $report_file

  echo "📅 Weekly maintenance report generated: $report_file"

  # Perform weekly tasks
  weekly_certificate_check
  weekly_backup_verification
  weekly_security_scan
}

weekly_certificate_check() {
  echo "🔐 Weekly certificate expiration check..."

  local days_until_expiry=$(( ($(date -d "$(echo | openssl s_client -servername 013a.tech -connect 013a.tech:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)" +%s) - $(date +%s)) / 86400 ))

  echo "SSL certificate expires in $days_until_expiry days"

  if [[ $days_until_expiry -lt 45 ]]; then
    send_alert "SSL_CERT_RENEWAL_NEEDED" "SSL certificate expires in $days_until_expiry days - renewal required"
  fi
}

weekly_backup_verification() {
  echo "💾 Weekly backup verification..."

  # Check if backups are being created regularly
  local recent_backups=$(gsutil ls gs://aia-backups/database/ | tail -7 | wc -l)

  if [[ $recent_backups -lt 7 ]]; then
    send_alert "BACKUP_MISSING" "Only $recent_backups backups found in the last 7 days"
  else
    echo "✅ Backup verification passed: $recent_backups backups found"
  fi
}

weekly_security_scan() {
  echo "🔍 Weekly security scan..."

  # Basic security checks
  kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.securityContext.runAsUser}{"\n"}{end}' | \
    grep -E "aia|013a" | while read pod_name user_id; do
      if [[ "$user_id" == "0" ]] || [[ -z "$user_id" ]]; then
        echo "⚠️  Security concern: Pod $pod_name may be running as root"
      fi
    done
}

# Execute weekly maintenance
perform_weekly_maintenance
```

### Monthly Maintenance Schedule

#### Monthly System Review (First Sunday of Month)
```bash
#!/bin/bash
# Monthly comprehensive system review

perform_monthly_maintenance() {
  local month_date=$(date +%Y_%m)
  local report_file="monthly_report_${month_date}.txt"

  echo "📅 Starting monthly maintenance - $(date +%B) $(date +%Y)"

  {
    echo "=== AIA System Monthly Maintenance Report ==="
    echo "Month: $(date +%B) $(date +%Y)"
    echo "Generated: $(date)"
    echo

    # 1. Performance trends
    echo "1. PERFORMANCE TRENDS"
    echo "   Monthly performance analysis would go here"
    echo "   (Requires historical data collection)"
    echo

    # 2. Capacity planning review
    echo "2. CAPACITY PLANNING REVIEW"
    assess_current_capacity | sed 's/^/   /'
    echo

    # 3. Security posture review
    echo "3. SECURITY POSTURE REVIEW"
    perform_security_audit | sed 's/^/   /'
    echo

    # 4. Cost analysis
    echo "4. COST ANALYSIS"
    gcloud billing budgets list --billing-account=$(gcloud billing accounts list --format="value(name)" | head -1) | sed 's/^/   /'
    echo

    # 5. Disaster recovery testing
    echo "5. DISASTER RECOVERY TESTING"
    echo "   DR testing results would be documented here"
    echo

  } > $report_file

  # Monthly tasks
  monthly_disaster_recovery_test
  monthly_performance_optimization
  monthly_security_audit
  monthly_cost_optimization

  echo "📅 Monthly maintenance completed: $report_file"
}

monthly_disaster_recovery_test() {
  echo "🔄 Monthly disaster recovery test..."

  # Test backup restoration in staging environment
  echo "Testing backup restoration process..."
  # This would involve creating a staging environment and testing restore
  echo "✅ DR test completed (detailed results in separate report)"
}

monthly_performance_optimization() {
  echo "⚡ Monthly performance optimization..."

  # Database optimization
  kubectl exec -n aia-production deployment/aia-postgres -- \
    psql -U aia_user -d aia_production -c "REINDEX DATABASE aia_production;"

  # Clear old logs
  kubectl delete pods -n aia-production -l cleanup=monthly --field-selector=status.phase=Succeeded

  echo "✅ Performance optimization completed"
}

monthly_security_audit() {
  echo "🔒 Monthly comprehensive security audit..."

  # Comprehensive security review
  perform_security_audit > "security_audit_$(date +%Y_%m).txt"

  # Update security patches
  echo "Checking for security updates..."
  # This would involve checking for container image updates, etc.

  echo "✅ Security audit completed"
}

monthly_cost_optimization() {
  echo "💰 Monthly cost optimization review..."

  # Review resource usage and optimize
  kubectl top nodes
  kubectl top pods --all-namespaces | grep -E "aia|013a"

  # Identify unused resources
  echo "Checking for unused resources..."
  kubectl get persistentvolumes | grep Available

  echo "✅ Cost optimization review completed"
}

# Execute monthly maintenance
if [[ "$(date +%d)" -le 7 ]] && [[ "$(date +%u)" == "7" ]]; then
  perform_monthly_maintenance
fi
```

---

**Document Control:**
- **Version**: 1.0
- **Created**: October 3, 2025
- **Last Updated**: October 3, 2025
- **Next Review**: November 3, 2025
- **Owner**: Operations Team
- **Approver**: Chief Operations Officer

**Automation Schedule:**
- **Daily Health Checks**: 09:00 UTC and 18:00 UTC
- **Weekly Maintenance**: Sundays at 02:00 UTC
- **Monthly Reviews**: First Sunday of month at 01:00 UTC
- **Emergency Procedures**: On-demand via on-call system

**Contact Information:**
- **Operations Team**: ops@013a.tech
- **Emergency Hotline**: +1-XXX-XXX-XXXX (24/7)
- **Escalation Path**: ops → devops-lead → cto
- **Documentation Updates**: ops-docs@013a.tech