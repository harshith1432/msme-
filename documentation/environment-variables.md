# Environment Variables Specification

| Variable | Description | Required in Production | Default |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Application environment (`development`, `testing`, `production`) | Yes | `production` |
| `SECRET_KEY` | Flask cryptographic session key (64+ hex characters) | Yes | None |
| `DATABASE_URL` | PostgreSQL connection string | Yes | None |
| `DB_POOL_SIZE` | SQLAlchemy connection pool size | No | `10` |
| `DB_MAX_OVERFLOW` | SQLAlchemy maximum overflow connections | No | `20` |
| `REDIS_URL` | Redis broker and cache connection URL | Yes | `redis://127.0.0.1:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | No | Same as `REDIS_URL` |
| `CELERY_TASK_ALWAYS_EAGER` | Run Celery tasks synchronously (useful in tests) | No | `false` |
| `STORAGE_BACKEND` | Storage driver (`local` or `s3`) | Yes | `s3` |
| `S3_ENDPOINT_URL` | S3 API endpoint URL (AWS or MinIO) | If S3 | `https://s3.ap-south-1.amazonaws.com` |
| `S3_ACCESS_KEY` | IAM Access Key ID | If S3 | None |
| `S3_SECRET_KEY` | IAM Secret Access Key | If S3 | None |
| `S3_BUCKET_PRIVATE` | Bucket name for private documents | If S3 | `msme-private-documents` |
| `S3_BUCKET_KNOWLEDGE`| Bucket name for approved knowledge sources | If S3 | `msme-knowledge-sources` |
| `S3_REGION` | AWS / S3 region name | No | `ap-south-1` |
| `MAX_CONTENT_LENGTH`| Maximum upload size in bytes | No | `16777216` (16MB) |
