"""
Input validation utilities for Mployable

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

    # LinkedIn URL pattern
    LINKEDIN_URL_PATTERN = r"^https?://(?:www\.)?linkedin\.com/.*"

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
    def validate_linkedin_url(cls, url: str) -> str:
        """
        Validate LinkedIn profile URL

        Args:
            url: LinkedIn URL to validate

        Returns:
            Cleaned URL

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            return ""  # Optional field

        url = url.strip()

        if not re.match(cls.LINKEDIN_URL_PATTERN, url, re.IGNORECASE):
            raise ValueError("Invalid LinkedIn URL format")

        return url

    @classmethod
    def validate_request(
        cls, github_username: str, job_description: str, linkedin_url: str = ""
    ) -> Tuple[str, str, str]:
        """
        Validate complete request input

        Args:
            github_username: GitHub username
            job_description: Job description
            linkedin_url: LinkedIn profile URL (optional)

        Returns:
            Tuple of (github_username, job_description, linkedin_url)

        Raises:
            InvalidGitHubUsername: If username is invalid
            InvalidJobDescription: If job description is invalid
            ValueError: If LinkedIn URL is invalid
        """
        github_username = cls.validate_github_username(github_username)
        job_description = cls.validate_job_description(job_description)
        linkedin_url = cls.validate_linkedin_url(linkedin_url)

        return github_username, job_description, linkedin_url

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
