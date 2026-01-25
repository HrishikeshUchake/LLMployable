# MongoDB Setup & Usage Guide for Mployable

## Overview

Mployable now uses **MongoDB** as its primary database for:
- User management and authentication
- Resume storage and versioning
- Job application tracking
- API key management
- Audit logging
- Caching (job analysis, GitHub profiles)

## Installation & Setup

### Local Development

#### Option 1: Using Docker Compose (Recommended)

```bash
# Start MongoDB with Redis and the app
docker-compose up -d

# View logs
docker-compose logs -f mongodb

# Stop all services
docker-compose down
```

MongoDB will be available at: `mongodb://localhost:27017/mployable`

#### Option 2: Direct MongoDB Installation

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt-get update
apt-get install -y mongodb-org
systemctl start mongod
```

**Windows:**
```bash
choco install mongodb
# or download from https://www.mongodb.com/try/download/community
```

### Configuration

Update your `.env` file:

```env
DATABASE_URL=mongodb://localhost:27017/mployable
DATABASE_NAME=mployable
DATABASE_HOST=localhost
DATABASE_PORT=27017
DATABASE_USERNAME=          # Leave empty for local dev
DATABASE_PASSWORD=          # Leave empty for local dev
```

## Database Models

### 1. User Model
Stores user account information and preferences.

```python
user = User.objects.create(
    email="user@example.com",
    username="johndoe",
    password_hash="hashed...",
    github_username="johndoe-github",
    first_name="John",
    last_name="Doe"
)
```

### 2. Resume Model
Stores generated resumes with version history.

```python
resume = Resume.objects.create(
    user_id=str(user.id),
    github_username="johndoe-github",
    job_title="Senior Python Engineer",
    job_description="We need...",
    tailored_content={...},
    pdf_path="/temp/resume_123.pdf"
)

# Add a new version
resume.add_version(
    content={...},
    notes="Updated with new project"
)
```

### 3. JobApplication Model
Track job applications and their status.

```python
app = JobApplication.objects.create(
    user_id=str(user.id),
    job_title="Senior Engineer",
    company="Google",
    job_url="https://...",
    resume_id=str(resume.id),
    status="applied"  # or: interviewing, offered, rejected, withdrawn
)

# Update status
app.status = "interviewing"
app.save()
```

### 4. APIKey Model
API authentication tokens.

```python
api_key = APIKey.objects.create(
    user_id=str(user.id),
    key="secure_token_...",
    name="Mobile App",
    expires_at=datetime.utcnow() + timedelta(days=365)
)
```

### 5. Cache Models
- `JobCache`: Caches analyzed job descriptions (24-48 hour TTL)
- `GitHubProfileCache`: Caches GitHub profiles (1-2 hour TTL)

### 6. AuditLog Model
Tracks all important operations for compliance and debugging.

```python
AuditLog.objects.create(
    user_id=str(user.id),
    action="generate_resume",
    resource_type="resume",
    resource_id=str(resume.id),
    status="success",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)
```

## Using the Repository Layer

### UserRepository

```python
from database.repositories import UserRepository

# Create user
user = UserRepository.create_user(
    email="user@example.com",
    username="johndoe",
    password="secure_password"
)

# Authenticate
user = UserRepository.authenticate("johndoe", "secure_password")

# Update
UserRepository.update_user(str(user.id), github_username="new-username")
```

### ResumeRepository

```python
from database.repositories import ResumeRepository

# Create resume
resume = ResumeRepository.create_resume(
    user_id=str(user.id),
    github_username="johndoe",
    job_title="Senior Engineer",
    job_description="Job details...",
    tailored_content={...}
)

# Get user's resumes
resumes = ResumeRepository.get_user_resumes(str(user.id))

# Add version
ResumeRepository.add_resume_version(
    str(resume.id),
    content={...},
    notes="Updated with new skills"
)
```

### JobApplicationRepository

```python
from database.repositories import JobApplicationRepository

# Create application
app = JobApplicationRepository.create_application(
    user_id=str(user.id),
    job_title="Senior Engineer",
    company="Google",
    resume_id=str(resume.id)
)

# Get applications
apps = JobApplicationRepository.get_user_applications(str(user.id))

# Update status
JobApplicationRepository.update_application_status(str(app.id), "interviewing")
```

### CacheRepository

```python
from database.repositories import CacheRepository

# Cache job analysis
CacheRepository.cache_job_analysis(
    job_description="...",
    analyzed_content={...}
)

# Get cached analysis
cached = CacheRepository.get_cached_job_analysis("...")
if cached:
    use_cached_analysis(cached)
```

## Database Initialization

When starting the application:

```python
from database import init_db

# Initialize MongoDB connection and create indexes
if init_db():
    print("Database ready")
else:
    print("Database connection failed")
```

This will:
1. Connect to MongoDB
2. Create all collections
3. Set up indexes for optimal performance
4. Set up TTL indexes for automatic cache expiration

## Queries with MongoEngine

### Basic Queries

```python
from database import User, Resume

# Find by ID
user = User.objects(id=user_id).first()

# Find by field
user = User.objects(email="user@example.com").first()

# Find multiple
resumes = Resume.objects(user_id=user_id)

# Filter with conditions
recent = Resume.objects(
    user_id=user_id,
    created_at__gte=datetime.utcnow() - timedelta(days=7)
)

# Sorting
sorted_resumes = Resume.objects(user_id=user_id).order_by('-created_at')

# Limit and skip
paginated = Resume.objects(user_id=user_id).skip(10).limit(10)
```

### Advanced Queries

```python
# Count
count = Resume.objects(user_id=user_id).count()

# Exists check
exists = Resume.objects(id=resume_id).count() > 0

# Delete
Resume.objects(id=resume_id).delete()

# Update multiple
Resume.objects(user_id=user_id, is_archived=False).update(
    set__is_archived=True
)

# Aggregate
pipeline = [
    {'$match': {'user_id': user_id}},
    {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
]
results = JobApplication.objects.aggregate(*pipeline)
```

## Performance Optimization

### Indexes
Indexes are automatically created on:
- `user_id` (for fast user lookups)
- `email`, `username` (for authentication)
- `created_at` (for sorting and filtering)
- `expires_at` (TTL index for auto-deletion of expired records)

### Query Optimization

```python
# Good: Select only needed fields
resumes = Resume.objects(user_id=user_id).only('id', 'job_title', 'created_at')

# Avoid: Loading all fields if only few needed
resumes = Resume.objects(user_id=user_id)  # Loads everything

# Good: Use indexes for common queries
resumes = Resume.objects(user_id=user_id, created_at__gte=since_date)

# Good: Limit results when appropriate
recent = Resume.objects(user_id=user_id).limit(10)
```

## Backup & Recovery

### Manual Backup

```bash
# Using Docker
docker exec mployable-mongodb mongodump --out /backup

# Direct mongodump
mongodump --uri="mongodb://localhost:27017/mployable" --out /backup
```

### Restore

```bash
# Using Docker
docker exec mployable-mongodb mongorestore /backup

# Direct mongorestore
mongorestore --uri="mongodb://localhost:27017/mployable" /backup
```

### Automated Backups

Create a script (e.g., `backup_db.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups/mployable-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
mongodump --uri="mongodb://localhost:27017/mployable" --out "$BACKUP_DIR"

# Keep only last 30 days of backups
find /backups -type d -mtime +30 -exec rm -rf {} +
```

Schedule with cron:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup_db.sh
```

## Monitoring & Maintenance

### Connection Health Check

```python
from database import get_db_manager

db_manager = get_db_manager()
if db_manager.health_check():
    print("MongoDB is healthy")
else:
    print("MongoDB connection failed")
```

### MongoDB Shell

```bash
# Connect to MongoDB
mongosh "mongodb://localhost:27017/mployable"

# List databases
show databases

# Switch database
use mployable

# List collections
show collections

# View documents
db.users.find()
db.resumes.find()

# Count documents
db.resumes.countDocuments()

# Create index
db.resumes.createIndex({user_id: 1, created_at: -1})
```

## Migration from SQLite/PostgreSQL

If migrating from SQL databases:

```python
# 1. Export data from old database
# 2. Transform to MongoDB document format
# 3. Bulk insert into MongoDB

from database import Resume
from database.repositories import ResumeRepository

# Example migration for resumes
old_resumes = get_old_sql_resumes()

for old_resume in old_resumes:
    ResumeRepository.create_resume(
        user_id=old_resume['user_id'],
        github_username=old_resume['github_username'],
        job_title=old_resume['job_title'],
        job_description=old_resume['job_description'],
        tailored_content=old_resume['content']
    )
```

## Troubleshooting

### Connection Errors

```
MongoEngineConnectionError: MongoDB connection error: [Errno 111] Connection refused
```

**Solution:**
- Ensure MongoDB is running: `docker-compose ps`
- Check connection string in `.env`
- Verify MongoDB port (27017) is not blocked

### Authentication Errors

```
OperationFailure: authentication failed
```

**Solution:**
- Check `DATABASE_USERNAME` and `DATABASE_PASSWORD` in `.env`
- Ensure user exists in MongoDB: `db.getUser("username")`
- For development, leave credentials empty

### Performance Issues

**Solution:**
- Check indexes: `db.resumes.getIndexes()`
- Analyze slow queries: Enable profiling
- Use `.explain()` to check query plans

## Production Considerations

1. **Replication**: Set up replica sets for high availability
2. **Backups**: Automated daily backups to S3 or other storage
3. **Monitoring**: Use MongoDB Atlas or Ops Manager
4. **Sharding**: For large datasets exceeding node capacity
5. **Security**: Enable authentication, use TLS/SSL encryption
6. **Indexing**: Regularly review and optimize indexes
7. **Connection Pooling**: Already configured in `DatabaseManager`

## Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [MongoEngine Documentation](http://mongoengine.org/)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-checklist/)
