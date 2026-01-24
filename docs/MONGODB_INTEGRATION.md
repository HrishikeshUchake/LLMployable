# Mployable MongoDB Integration Summary

## What's Been Implemented

### 1. MongoDB Configuration
- **File:** `config/config.py`
- MongoDB connection details added to base `Config` class
- Support for authenticated and unauthenticated connections
- Environment-based configuration loading
- Connection pooling and timeout settings

### 2. Database Models
- **File:** `database/mongodb.py`

#### Models Created:
1. **User** - User accounts and authentication
   - Email, username, password hash
   - GitHub/LinkedIn profiles
   - Preferences and settings
   - Timestamps for creation/updates

2. **Resume** - Generated resumes with versioning
   - User association
   - Job matching details
   - Resume content storage
   - Version history
   - Archive capability

3. **JobApplication** - Track job applications
   - Application status (applied, interviewing, offered, rejected, withdrawn)
   - Job details and resume association
   - Application timeline

4. **APIKey** - API authentication
   - Per-user API tokens
   - Expiration dates
   - Usage tracking

5. **JobCache** - Job description analysis caching
   - Hash-based deduplication
   - TTL-based auto-expiration (24-48 hours)

6. **GitHubProfileCache** - GitHub profile caching
   - TTL-based auto-expiration (1-2 hours)

7. **AuditLog** - Compliance and debugging
   - Track all operations
   - User and action logging
   - Error tracking
   - IP and user-agent information

### 3. Repository Layer
- **File:** `database/repositories.py`

#### Repositories:
- `UserRepository` - User CRUD and authentication
- `ResumeRepository` - Resume management with versioning
- `JobApplicationRepository` - Job application tracking
- `CacheRepository` - Cache management
- `APIKeyRepository` - API key management
- `AuditLogRepository` - Audit logging

### 4. Docker Support
- **File:** `docker-compose.yml`
- MongoDB 7 service with authentication
- Persistent data volumes
- Health checks
- Network connectivity with other services

### 5. Database Manager
- **File:** `database/mongodb.py` - `DatabaseManager` class
- Singleton pattern for connection management
- Connection pooling
- Health checks
- Automatic index creation

### 6. Documentation
- **File:** `MONGODB_GUIDE.md`
- Comprehensive setup guide
- Query examples
- Performance optimization tips
- Backup and recovery procedures
- Troubleshooting guide

## Key Features

### Automatic Index Creation
```python
# Automatically created on init_db()
- user_id (for queries)
- email, username (for authentication)
- created_at (for sorting/filtering)
- expires_at (TTL index for cache expiration)
```

### TTL Indexes (Automatic Deletion)
```python
# Cache expires after configured TTL
JobCache - 24-48 hours
GitHubProfileCache - 1-2 hours
```

### Connection Pooling
```python
# Optimized for production
maxPoolSize: 100
minPoolSize: 10
```

### Audit Trail
Every important operation is logged:
- Resume generation
- User authentication
- API key usage
- Application updates

## Usage Examples

### Initialize Database
```python
from database import init_db

init_db()  # Creates connection, collections, and indexes
```

### Create User
```python
from database.repositories import UserRepository

user = UserRepository.create_user(
    email="user@example.com",
    username="johndoe",
    password="secure_password"
)
```

### Generate and Store Resume
```python
from database.repositories import ResumeRepository

resume = ResumeRepository.create_resume(
    user_id=str(user.id),
    github_username="johndoe",
    job_title="Senior Engineer",
    job_description="Job details...",
    tailored_content={...}
)
```

### Track Job Application
```python
from database.repositories import JobApplicationRepository

app = JobApplicationRepository.create_application(
    user_id=str(user.id),
    job_title="Senior Engineer",
    company="Google",
    resume_id=str(resume.id)
)

# Update status
JobApplicationRepository.update_application_status(
    str(app.id), 
    "interviewing"
)
```

### Cache Job Analysis
```python
from database.repositories import CacheRepository

# Store analysis
CacheRepository.cache_job_analysis(
    job_description="...",
    analyzed_content={...},
    ttl_hours=48
)

# Retrieve cached analysis
cached = CacheRepository.get_cached_job_analysis("...")
if cached:
    # Use cached result
    pass
```

## Environment Variables

```env
# MongoDB Connection
DATABASE_URL=mongodb://localhost:27017/mployable
DATABASE_NAME=mployable
DATABASE_HOST=localhost
DATABASE_PORT=27017
DATABASE_USERNAME=          # Leave empty for local dev
DATABASE_PASSWORD=          # Leave empty for local dev
```

## Docker Deployment

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f mongodb
```

### MongoDB Shell Access
```bash
docker-compose exec mongodb mongosh
use mployable
show collections
```

## Performance Considerations

### Indexed Queries
All frequently accessed fields are indexed:
- `user_id` - Primary filtering
- `email`, `username` - Authentication
- `created_at` - Sorting and range queries
- `expires_at` - TTL management

### Connection Pooling
- Min 10, Max 100 connections
- Automatic connection recycling
- Handles concurrent requests efficiently

### Caching Strategy
- Job analysis: 24-48 hour cache
- GitHub profiles: 1-2 hour cache
- Automatic expiration via TTL indexes

## Data Model Relationships

```
User
├── Resume (one-to-many)
│   ├── ResumeVersion (embedded)
│   └── JobApplication (references)
├── JobApplication (one-to-many)
│   └── Resume (references)
├── APIKey (one-to-many)
└── AuditLog (one-to-many)

JobCache (global)
├── Keyed by job description hash
└── Auto-expires

GitHubProfileCache (global)
├── Keyed by username
└── Auto-expires
```

## Production Readiness

### Checklist
- [x] Connection pooling configured
- [x] TTL indexes for auto-cleanup
- [x] Audit logging enabled
- [x] Error handling with fallbacks
- [x] Health checks implemented
- [x] Docker support ready
- [ ] Replication setup (when scaling)
- [ ] Backup automation (manual guide provided)
- [ ] Security hardening (auth required in prod)
- [ ] Monitoring dashboards (optional, MongoDB Atlas)

## Next Steps

### Phase 1: Testing
- Run comprehensive test suite
- Load testing with concurrent users
- Cache hit rate optimization

### Phase 2: Monitoring
- Set up MongoDB monitoring
- Track connection pool usage
- Monitor query performance

### Phase 3: Scaling
- Configure replica sets for HA
- Enable sharding if needed
- Set up automated backups

### Phase 4: Security
- Enable TLS/SSL encryption
- Implement user authentication
- Set up network policies
- Regular security audits

## Integration with App

The production app (`app_production.py`) will need minimal updates:
1. Import database modules at startup
2. Call `init_db()` during app initialization
3. Use repositories for data operations
4. Log operations to AuditLog

Example:
```python
from database import init_db
from database.repositories import ResumeRepository, AuditLogRepository

# In Flask app initialization
init_db()

# When generating resume
resume = ResumeRepository.create_resume(...)
AuditLogRepository.log_action(
    user_id=user_id,
    action="generate_resume",
    resource_id=str(resume.id)
)
```

## Files Created/Modified

### New Files
- `database/mongodb.py` - Models and connection manager
- `database/repositories.py` - Repository layer
- `database/__init__.py` - Package initialization
- `MONGODB_GUIDE.md` - Complete usage guide

### Modified Files
- `docker-compose.yml` - MongoDB service (replaced PostgreSQL)
- `.env.example` - MongoDB configuration
- `config/config.py` - MongoDB connection settings
- `requirements.txt` - Added pymongo and mongoengine

## Troubleshooting

### Connection Issues
```bash
# Check if MongoDB is running
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Test connection
mongosh "mongodb://localhost:27017/mployable"
```

### Query Issues
- Use `.explain()` to analyze queries
- Check indexes: `db.collection.getIndexes()`
- Monitor slow queries with profiling

### Performance Issues
- Add indexes for frequently filtered fields
- Use connection pooling (already configured)
- Consider caching at application level

## Security Notes

### For Development
- MongoDB runs without authentication
- Use default network isolation

### For Production
- Enable authentication (credentials in `.env`)
- Use TLS/SSL for connections
- Restrict network access
- Enable encryption at rest
- Regular security audits

## Support & Resources

- MongoDB Docs: https://docs.mongodb.com/
- MongoEngine Docs: http://mongoengine.org/
- Docker Hub: https://hub.docker.com/_/mongo
