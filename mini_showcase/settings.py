# General
PROVIDERS_API_TIMEOUT = 30  # secs

# Redis
REDIS_SEARCH_TTL = 10 * 60 # 10 minutes
REDIS_URL = "redis://mini_showcase_redis"

# Postgres
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "postgres"
DB_TYPE = "postgres"
USERNAME = POSTGRES_USER
PASSWORD = POSTGRES_PASSWORD
HOST = "postgres"
DB_NAME = POSTGRES_DB
DB_URI = f"{DB_TYPE}://{USERNAME}:{PASSWORD}@{HOST}:5432/{POSTGRES_DB}"
