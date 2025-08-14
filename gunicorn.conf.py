import os

# Bind to the port that Render provides
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Worker configuration for Render
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
worker_class = "sync"
worker_connections = 1000

# Timeout and restart settings
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Security
forwarded_allow_ips = "*"
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}