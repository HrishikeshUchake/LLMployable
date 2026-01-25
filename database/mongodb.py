"""
MongoDB database integration for Mployable

Provides connection management, models, and utilities for MongoDB operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from mongoengine import (
    connect,
    disconnect,
    Document,
    StringField,
    EmailField,
    URLField,
    IntField,
    FloatField,
    DateTimeField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    DictField,
    BooleanField,
    CASCADE,
    DENY,
)
from config import get_logger, config

logger = get_logger(__name__)


class DatabaseManager:
    """Manages MongoDB connection and initialization"""

    _instance = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Connect to MongoDB"""
        if self._connected:
            logger.debug("Already connected to MongoDB")
            return

        try:
            logger.info(
                f"Connecting to MongoDB at {config.DATABASE_HOST}:{config.DATABASE_PORT}"
            )

            # Build connection string
            if config.DATABASE_USERNAME and config.DATABASE_PASSWORD:
                connection_string = (
                    f"mongodb://{config.DATABASE_USERNAME}:{config.DATABASE_PASSWORD}"
                    f"@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"
                )
            else:
                connection_string = f"mongodb://{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"

            # Connect with connection pooling
            connect(
                db=config.DATABASE_NAME,
                host=connection_string,
                maxPoolSize=100,
                minPoolSize=10,
                connect=True,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )

            self._connected = True
            logger.info("Successfully connected to MongoDB")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise

    def disconnect(self):
        """Disconnect from MongoDB"""
        if not self._connected:
            return

        try:
            disconnect()
            self._connected = False
            logger.info("Disconnected from MongoDB")
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {e}")

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self._connected

    def health_check(self) -> bool:
        """Check MongoDB connection health"""
        try:
            # Try to ping the database
            from mongoengine.connection import get_connection

            conn = get_connection()
            conn.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False


# Document Models
class ResumeVersion(EmbeddedDocument):
    """Embedded document for resume versions"""

    version_number = IntField(required=True)
    content = DictField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    notes = StringField()


class Resume(Document):
    """Resume document model"""

    user_id = StringField(required=True, unique=False, index=True)
    github_username = StringField()
    job_title = StringField()
    job_description = StringField()
    tailored_content = DictField(required=True)
    pdf_path = StringField()
    versions = ListField(EmbeddedDocumentField(ResumeVersion))
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    updated_at = DateTimeField(default=datetime.utcnow)
    is_archived = BooleanField(default=False)

    meta = {
        "collection": "resumes",
        "indexes": [
            "user_id",
            "created_at",
            ("user_id", "-created_at"),
        ],
        "ordering": ["-created_at"],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def add_version(self, content: Dict, notes: str = None) -> None:
        """Add a new version of the resume"""
        new_version = ResumeVersion(
            version_number=len(self.versions) + 1, content=content, notes=notes
        )
        self.versions.append(new_version)
        self.save()
        logger.debug(f"Resume {self.id} version {new_version.version_number} created")


class JobApplication(Document):
    """Job application tracking"""

    user_id = StringField(required=True, index=True)
    job_title = StringField(required=True)
    company = StringField(required=True)
    job_url = StringField()
    resume_id = StringField(index=True)
    status = StringField(
        choices=["applied", "interviewing", "offered", "rejected", "withdrawn"],
        default="applied",
    )
    applied_date = DateTimeField(default=datetime.utcnow)
    last_updated = DateTimeField(default=datetime.utcnow)
    notes = StringField()
    job_description = StringField()

    meta = {
        "collection": "job_applications",
        "indexes": [
            "user_id",
            "status",
            ("user_id", "-applied_date"),
        ],
        "ordering": ["-applied_date"],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.last_updated = datetime.utcnow()
        return super().save(*args, **kwargs)


class User(Document):
    """User document model"""

    email = EmailField(unique=True, required=True, index=True)
    username = StringField(unique=True, required=True, index=True)
    password_hash = StringField(required=True)
    github_username = StringField()
    first_name = StringField()
    last_name = StringField()
    bio = StringField()

    # Account settings
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()

    # Preferences
    email_notifications = BooleanField(default=True)
    theme = StringField(default="light", choices=["light", "dark"])

    meta = {
        "collection": "users",
        "indexes": [
            "email",
            "username",
            ("created_at", "-1"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def set_password(self, password: str) -> None:
        """Hash and set password"""
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password"""
        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)


class APIKey(Document):
    """API Key for authentication"""

    user_id = StringField(required=True, index=True)
    key = StringField(required=True, unique=True, index=True)
    name = StringField(required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    last_used = DateTimeField()
    expires_at = DateTimeField()

    meta = {
        "collection": "api_keys",
        "indexes": [
            "user_id",
            "key",
        ],
    }


class JobCache(Document):
    """Cache for analyzed job descriptions"""

    job_description_hash = StringField(required=True, unique=True, index=True)
    job_description = StringField(required=True)
    analyzed_content = DictField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)  # TTL

    meta = {
        "collection": "job_cache",
        "indexes": [
            ("expires_at", 1),  # MongoDB will auto-delete after this date
        ],
    }


class GitHubProfileCache(Document):
    """Cache for GitHub profiles"""

    username = StringField(required=True, unique=True, index=True)
    profile_data = DictField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)  # TTL

    meta = {
        "collection": "github_cache",
        "indexes": [
            ("expires_at", 1),  # MongoDB will auto-delete after this date
        ],
    }


class AuditLog(Document):
    """Audit log for tracking operations"""

    user_id = StringField(index=True)
    action = StringField(required=True)  # generate_resume, create_user, etc.
    resource_type = StringField()  # resume, user, api_key, etc.
    resource_id = StringField()
    status = StringField(choices=["success", "failure"], default="success")
    details = DictField()
    error_message = StringField()
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    ip_address = StringField()
    user_agent = StringField()

    meta = {
        "collection": "audit_logs",
        "indexes": [
            "user_id",
            "action",
            "created_at",
            ("created_at", -1),
        ],
    }


# Database initialization
def init_db():
    """Initialize database connection and create indexes"""
    try:
        db_manager = DatabaseManager()
        db_manager.connect()

        # Ensure all collections have proper indexes
        User.ensure_indexes()
        Resume.ensure_indexes()
        JobApplication.ensure_indexes()
        APIKey.ensure_indexes()
        JobCache.ensure_indexes()
        GitHubProfileCache.ensure_indexes()
        AuditLog.ensure_indexes()

        logger.info("Database initialization completed successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False


def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    return DatabaseManager()
