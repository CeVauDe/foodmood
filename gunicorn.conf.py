"""Gunicorn configuration file for FoodMood production deployment."""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 2))
worker_class = "sync"
worker_connections = 1000

# Restart workers after this many requests, to help prevent memory leaks
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = 50

# Logging
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr

# Process naming
proc_name = "foodmood"

# Preload application for better performance
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=foodmood.settings",
]

# Graceful shutdown
graceful_timeout = 30


def when_ready(server) -> None:
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker) -> None:
    """Called just after a worker has been killed by a signal."""
    worker.log.info("worker received INT or QUIT signal")


def pre_fork(server, worker) -> None:
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_fork(server, worker) -> None:
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)
