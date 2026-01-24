"""
Database repository/service layer

Provides high-level operations on MongoDB documents.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
from config import get_logger
from database import (
    User, Resume, JobApplication, APIKey, JobCache, 
    GitHubProfileCache, AuditLog
)

logger = get_logger(__name__)


class UserRepository:
    """Repository for user operations"""
    
    @staticmethod
    def create_user(email: str, username: str, password: str, 
                   first_name: str = "", last_name: str = "") -> User:
        """Create a new user"""
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        logger.info(f"User created: {username}")
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.objects(email=email).first()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return User.objects(username=username).first()
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = User.objects(username=username).first()
        if user and user.is_active and user.check_password(password):
            user.last_login = datetime.utcnow()
            user.save()
            return user
        return None
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = User.objects(id=user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key) and key != 'password':
                    setattr(user, key, value)
                elif key == 'password':
                    user.set_password(value)
            user.save()
            logger.info(f"User updated: {user_id}")
        return user


class ResumeRepository:
    """Repository for resume operations"""
    
    @staticmethod
    def create_resume(user_id: str, github_username: str, job_title: str,
                     job_description: str, tailored_content: Dict) -> Resume:
        """Create a new resume"""
        resume = Resume(
            user_id=user_id,
            github_username=github_username,
            job_title=job_title,
            job_description=job_description,
            tailored_content=tailored_content
        )
        resume.save()
        logger.info(f"Resume created for user {user_id}: {resume.id}")
        return resume
    
    @staticmethod
    def get_resume(resume_id: str) -> Optional[Resume]:
        """Get resume by ID"""
        return Resume.objects(id=resume_id).first()
    
    @staticmethod
    def get_user_resumes(user_id: str, archived: bool = False) -> List[Resume]:
        """Get all resumes for a user"""
        query = Resume.objects(user_id=user_id, is_archived=archived)
        return list(query)
    
    @staticmethod
    def update_resume(resume_id: str, **kwargs) -> Optional[Resume]:
        """Update resume"""
        resume = Resume.objects(id=resume_id).first()
        if resume:
            for key, value in kwargs.items():
                if hasattr(resume, key):
                    setattr(resume, key, value)
            resume.save()
            logger.info(f"Resume updated: {resume_id}")
        return resume
    
    @staticmethod
    def add_resume_version(resume_id: str, content: Dict, notes: str = None) -> Optional[Resume]:
        """Add a new version to a resume"""
        resume = Resume.objects(id=resume_id).first()
        if resume:
            resume.add_version(content, notes)
            return resume
        return None
    
    @staticmethod
    def archive_resume(resume_id: str) -> Optional[Resume]:
        """Archive a resume"""
        return ResumeRepository.update_resume(resume_id, is_archived=True)


class JobApplicationRepository:
    """Repository for job application operations"""
    
    @staticmethod
    def create_application(user_id: str, job_title: str, company: str,
                          resume_id: str = None, job_url: str = None,
                          job_description: str = None) -> JobApplication:
        """Create a new job application record"""
        application = JobApplication(
            user_id=user_id,
            job_title=job_title,
            company=company,
            resume_id=resume_id,
            job_url=job_url,
            job_description=job_description
        )
        application.save()
        logger.info(f"Job application created for user {user_id}: {company} - {job_title}")
        return application
    
    @staticmethod
    def get_application(app_id: str) -> Optional[JobApplication]:
        """Get application by ID"""
        return JobApplication.objects(id=app_id).first()
    
    @staticmethod
    def get_user_applications(user_id: str, status: str = None) -> List[JobApplication]:
        """Get applications for a user"""
        query = JobApplication.objects(user_id=user_id)
        if status:
            query = query.filter(status=status)
        return list(query)
    
    @staticmethod
    def update_application_status(app_id: str, status: str) -> Optional[JobApplication]:
        """Update application status"""
        valid_statuses = ['applied', 'interviewing', 'offered', 'rejected', 'withdrawn']
        if status not in valid_statuses:
            logger.warning(f"Invalid status: {status}")
            return None
        
        application = JobApplication.objects(id=app_id).first()
        if application:
            application.status = status
            application.save()
            logger.info(f"Application {app_id} status updated to: {status}")
        return application


class CacheRepository:
    """Repository for cache operations"""
    
    @staticmethod
    def cache_job_analysis(job_description: str, analyzed_content: Dict,
                          ttl_hours: int = 48) -> JobCache:
        """Cache job analysis result"""
        # Create hash of job description
        desc_hash = hashlib.sha256(job_description.encode()).hexdigest()
        
        # Check if already cached
        existing = JobCache.objects(job_description_hash=desc_hash).first()
        if existing:
            existing.delete()
        
        # Create new cache
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        cache = JobCache(
            job_description_hash=desc_hash,
            job_description=job_description,
            analyzed_content=analyzed_content,
            expires_at=expires_at
        )
        cache.save()
        logger.debug(f"Job analysis cached with hash: {desc_hash}")
        return cache
    
    @staticmethod
    def get_cached_job_analysis(job_description: str) -> Optional[Dict]:
        """Get cached job analysis"""
        desc_hash = hashlib.sha256(job_description.encode()).hexdigest()
        cache = JobCache.objects(
            job_description_hash=desc_hash,
            expires_at__gt=datetime.utcnow()  # Not expired
        ).first()
        
        if cache:
            logger.debug(f"Job analysis cache hit")
            return cache.analyzed_content
        
        logger.debug(f"Job analysis cache miss")
        return None
    
    @staticmethod
    def cache_github_profile(username: str, profile_data: Dict,
                            ttl_hours: int = 1) -> GitHubProfileCache:
        """Cache GitHub profile"""
        # Check if already cached
        existing = GitHubProfileCache.objects(username=username).first()
        if existing:
            existing.delete()
        
        # Create new cache
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        cache = GitHubProfileCache(
            username=username,
            profile_data=profile_data,
            expires_at=expires_at
        )
        cache.save()
        logger.debug(f"GitHub profile cached: {username}")
        return cache
    
    @staticmethod
    def get_cached_github_profile(username: str) -> Optional[Dict]:
        """Get cached GitHub profile"""
        cache = GitHubProfileCache.objects(
            username=username,
            expires_at__gt=datetime.utcnow()  # Not expired
        ).first()
        
        if cache:
            logger.debug(f"GitHub profile cache hit: {username}")
            return cache.profile_data
        
        logger.debug(f"GitHub profile cache miss: {username}")
        return None


class AuditLogRepository:
    """Repository for audit log operations"""
    
    @staticmethod
    def log_action(user_id: str, action: str, resource_type: str = None,
                  resource_id: str = None, status: str = "success",
                  details: Dict = None, error_message: str = None,
                  ip_address: str = None, user_agent: str = None) -> AuditLog:
        """Log an action"""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details or {},
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        log_entry.save()
        logger.debug(f"Audit log created: {action} by {user_id}")
        return log_entry
    
    @staticmethod
    def get_user_logs(user_id: str, action: str = None,
                     days: int = 30) -> List[AuditLog]:
        """Get audit logs for a user"""
        since = datetime.utcnow() - timedelta(days=days)
        query = AuditLog.objects(user_id=user_id, created_at__gte=since)
        
        if action:
            query = query.filter(action=action)
        
        return list(query)
    
    @staticmethod
    def get_action_logs(action: str, days: int = 30) -> List[AuditLog]:
        """Get logs for a specific action"""
        since = datetime.utcnow() - timedelta(days=days)
        return list(AuditLog.objects(action=action, created_at__gte=since))


class APIKeyRepository:
    """Repository for API key operations"""
    
    @staticmethod
    def create_api_key(user_id: str, name: str, expires_days: int = 365) -> APIKey:
        """Create a new API key"""
        import secrets
        
        key = secrets.token_urlsafe(32)
        api_key = APIKey(
            user_id=user_id,
            key=key,
            name=name,
            expires_at=datetime.utcnow() + timedelta(days=expires_days)
        )
        api_key.save()
        logger.info(f"API key created for user {user_id}")
        return api_key
    
    @staticmethod
    def get_api_key(key: str) -> Optional[APIKey]:
        """Get API key"""
        return APIKey.objects(key=key, is_active=True).first()
    
    @staticmethod
    def get_user_api_keys(user_id: str) -> List[APIKey]:
        """Get all API keys for a user"""
        return list(APIKey.objects(user_id=user_id))
    
    @staticmethod
    def verify_api_key(key: str) -> bool:
        """Verify API key is valid and active"""
        api_key = APIKey.objects(
            key=key,
            is_active=True,
            expires_at__gt=datetime.utcnow()  # Not expired
        ).first()
        
        if api_key:
            api_key.last_used = datetime.utcnow()
            api_key.save()
            return True
        
        return False
    
    @staticmethod
    def revoke_api_key(key: str) -> bool:
        """Revoke an API key"""
        api_key = APIKey.objects(key=key).first()
        if api_key:
            api_key.is_active = False
            api_key.save()
            logger.info(f"API key revoked")
            return True
        return False
