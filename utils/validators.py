"""
Input validation utilities for LLMployable

Provides validation functions for all user inputs before processing.
"""

import re
from typing import Tuple
from config.exceptions import (
    InvalidGitHubUsername,
    InvalidJobDescription,
)


class InputValidator:
    """Validates user input before processing"""

    # GitHub username pattern: alphanumeric and hyphens only, 1-39 chars
    GITHUB_USERNAME_PATTERN = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$"

    # Job description: minimum 50 chars, maximum 50000 chars
    MIN_JOB_DESC_LENGTH = 50
    MAX_JOB_DESC_LENGTH = 50000

    @classmethod
    def validate_github_username(cls, username: str) -> str:
        """
        Validate GitHub username format

        Args:
            username: GitHub username to validate

        Returns:
            Cleaned username or empty string

        Raises:
            InvalidGitHubUsername: If username is invalid
        """
        if not username:
            return ""

        username = username.strip()

        if not re.match(cls.GITHUB_USERNAME_PATTERN, username):
            raise InvalidGitHubUsername(username)

        if len(username) > 39:
            raise InvalidGitHubUsername(username)

        return username

    @classmethod
    def validate_job_description(cls, job_desc: str) -> str:
        """
        Validate job description

        Args:
            job_desc: Job description text to validate

        Returns:
            Cleaned job description

        Raises:
            InvalidJobDescription: If job description is invalid
        """
        if not job_desc:
            raise InvalidJobDescription("Job description cannot be empty")

        job_desc = job_desc.strip()

        if len(job_desc) < cls.MIN_JOB_DESC_LENGTH:
            raise InvalidJobDescription(
                f"Job description must be at least {cls.MIN_JOB_DESC_LENGTH} characters"
            )

        if len(job_desc) > cls.MAX_JOB_DESC_LENGTH:
            raise InvalidJobDescription(
                f"Job description must not exceed {cls.MAX_JOB_DESC_LENGTH} characters"
            )

        return job_desc

    @classmethod
    def validate_request(
        cls, github_username: str, job_description: str
    ) -> Tuple[str, str]:
        """
        Validate complete request input

        Args:
            github_username: GitHub username
            job_description: Job description

        Returns:
            Tuple of (github_username, job_description)

        Raises:
            InvalidGitHubUsername: If username is invalid
            InvalidJobDescription: If job description is invalid
        """
        github_username = cls.validate_github_username(github_username)
        job_description = cls.validate_job_description(job_description)

        return github_username, job_description

    @classmethod
    def is_valid_github_username(cls, username: str) -> bool:
        """Check if username is valid without raising exception"""
        try:
            cls.validate_github_username(username)
            return True
        except InvalidGitHubUsername:
            return False

    @classmethod
    def is_valid_job_description(cls, job_desc: str) -> bool:
        """Check if job description is valid without raising exception"""
        try:
            cls.validate_job_description(job_desc)
            return True
        except InvalidJobDescription:
            return False
