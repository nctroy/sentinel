# Superset Configuration for Sentinel
# This configuration extends the default Superset settings

import os
from flask_appbuilder.security.manager import AUTH_DB

# Database configuration for Superset metadata
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.getenv('DATABASE_USER', 'superset')}:"
    f"{os.getenv('DATABASE_PASSWORD', 'superset_password')}@"
    f"{os.getenv('DATABASE_HOST', 'superset-db')}:"
    f"{os.getenv('DATABASE_PORT', '5432')}/"
    f"{os.getenv('DATABASE_DB', 'superset')}"
)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
}

# Celery configuration for async queries
class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }

CELERY_CONFIG = CeleryConfig

# Authentication type
AUTH_TYPE = AUTH_DB

# Roles
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# Enable SQL Lab
SUPERSET_WEBSERVER_TIMEOUT = 300
SQLLAB_TIMEOUT = 300

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True,
    'EMBEDDED_SUPERSET': False,
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': True,
}

# Row limit for SQL Lab
SQL_MAX_ROW = 100000
DISPLAY_SQL_MAX_ROW = 10000

# Enable data upload functionality
UPLOAD_FOLDER = '/app/superset_home/uploads/'
CSV_TO_HIVE_UPLOAD_DIRECTORY_FUNC = lambda *args: '/app/superset_home/uploads/'

# Webserver configuration
ENABLE_PROXY_FIX = True
ROW_LIMIT = 5000

# Secret key (override in production via environment variable)
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'sentinel_superset_secret_key_change_in_production')

# Timezone
TIME_ZONE = 'UTC'

# Additional customization
APP_NAME = 'Sentinel Analytics'
APP_ICON = '/static/assets/images/superset-logo-horiz.png'
