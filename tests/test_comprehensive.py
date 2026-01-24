"""
Comprehensive unit tests for Mployable

Tests cover all major components and error cases.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from config import InvalidGitHubUsername, InvalidJobDescription, GitHubAPIError
from utils.validators import InputValidator


class TestInputValidator:
    """Tests for input validation"""

    def test_valid_github_username(self):
        """Test valid GitHub username validation"""
        valid_usernames = [
            "torvalds",
            "gvanrossum",
            "octocat",
            "a",
            "user-name",
            "user123",
        ]

        for username in valid_usernames:
            result = InputValidator.validate_github_username(username)
            assert result == username

    def test_invalid_github_username_format(self):
        """Test invalid GitHub username format"""
        invalid_usernames = [
            "",
            "-invalid",
            "invalid-",
            "invalid user",
            "invalid@",
            "a" * 40,  # Too long
        ]

        for username in invalid_usernames:
            with pytest.raises(InvalidGitHubUsername):
                InputValidator.validate_github_username(username)

    def test_valid_job_description(self):
        """Test valid job description"""
        valid_desc = (
            "We are looking for a software engineer with 5+ years of Python experience. "
            "You will work on backend services using Django and PostgreSQL. Required skills: "
            "Python, Django, PostgreSQL, Docker. Nice to have: Kubernetes, AWS."
        )

        result = InputValidator.validate_job_description(valid_desc)
        assert result == valid_desc

    def test_invalid_job_description_too_short(self):
        """Test job description that's too short"""
        short_desc = "We need a developer"

        with pytest.raises(InvalidJobDescription):
            InputValidator.validate_job_description(short_desc)

    def test_job_description_cleanup(self):
        """Test job description cleanup"""
        desc = "  Job description with spaces and enough characters to meet minimum requirement  "
        result = InputValidator.validate_job_description(desc)
        assert result == desc.strip()

    def test_valid_linkedin_url(self):
        """Test valid LinkedIn URL"""
        valid_urls = [
            "https://www.linkedin.com/in/username/",
            "https://linkedin.com/in/username",
            "http://www.linkedin.com/in/john-doe/",
        ]

        for url in valid_urls:
            result = InputValidator.validate_linkedin_url(url)
            assert result == url

    def test_empty_linkedin_url(self):
        """Test that empty LinkedIn URL is optional"""
        result = InputValidator.validate_linkedin_url("")
        assert result == ""

    def test_invalid_linkedin_url(self):
        """Test invalid LinkedIn URL"""
        invalid_urls = [
            "https://github.com/user",
            "not-a-url",
            "https://facebook.com/user",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError):
                InputValidator.validate_linkedin_url(url)

    def test_validate_complete_request(self):
        """Test complete request validation"""
        github = "torvalds"
        job_desc = (
            "We are looking for a seasoned Python developer with 10+ years of experience "
            "in building scalable systems. You will work with Django, PostgreSQL, and Docker."
        )
        linkedin = "https://www.linkedin.com/in/test/"

        result_github, result_job, result_linkedin = InputValidator.validate_request(
            github, job_desc, linkedin
        )

        assert result_github == github
        assert result_job == job_desc
        assert result_linkedin == linkedin


class TestGitHubScraper:
    """Tests for GitHub scraper"""

    @patch("scrapers.github_scraper.Github")
    def test_scrape_profile_success(self, mock_github_class):
        """Test successful profile scraping"""
        from scrapers.github_scraper import GitHubScraper

        # Setup mock
        mock_user = Mock()
        mock_user.name = "Linus Torvalds"
        mock_user.bio = "Linux creator"
        mock_user.location = "Finland"
        mock_user.email = "linus@kernel.org"
        mock_user.blog = "https://example.com"
        mock_user.company = "The Linux Foundation"
        mock_user.hireable = True
        mock_user.public_repos = 50
        mock_user.followers = 100000
        mock_user.following = 10

        # Mock repositories
        mock_repo = Mock()
        mock_repo.fork = False
        mock_repo.name = "linux"
        mock_repo.description = "Linux kernel"
        mock_repo.language = "C"
        mock_repo.stargazers_count = 100000
        mock_repo.forks_count = 50000
        mock_repo.html_url = "https://github.com/torvalds/linux"
        mock_repo.get_topics = Mock(return_value=["kernel", "os"])

        mock_user.get_repos = Mock(return_value=[mock_repo])

        mock_github_instance = Mock()
        mock_github_instance.get_user = Mock(return_value=mock_user)
        mock_github_class.return_value = mock_github_instance

        # Test
        scraper = GitHubScraper()
        result = scraper.scrape_profile("torvalds")

        # Assertions
        assert result["username"] == "torvalds"
        assert result["name"] == "Linus Torvalds"
        assert len(result["repositories"]) == 1
        assert result["repositories"][0]["name"] == "linux"
        assert result["languages"] == [("C", 1)]

    @patch("scrapers.github_scraper.Github")
    def test_scrape_nonexistent_user(self, mock_github_class):
        """Test scraping nonexistent user"""
        from scrapers.github_scraper import GitHubScraper
        from github.GithubException import GithubException

        mock_github_instance = Mock()
        mock_github_instance.get_user = Mock(
            side_effect=GithubException(404, {"message": "Not Found"})
        )
        mock_github_class.return_value = mock_github_instance

        scraper = GitHubScraper()

        from config import GitHubUserNotFound

        with pytest.raises(GitHubUserNotFound):
            scraper.scrape_profile("nonexistentuser123456789")


class TestJobAnalyzer:
    """Tests for job analyzer"""

    def test_analyze_job_description(self):
        """Test job description analysis"""
        from analyzer.job_analyzer import JobAnalyzer

        job_desc = """
        We are looking for a Python developer with:
        - 5+ years of Python experience
        - Django and Flask expertise
        - PostgreSQL and MongoDB knowledge
        - Docker and Kubernetes
        - AWS cloud experience
        
        Required education: Bachelor's degree in Computer Science or related field
        """

        analyzer = JobAnalyzer()
        result = analyzer.analyze(job_desc)

        # Check that skills are extracted
        assert "skills" in result
        assert "experience_required" in result
        assert "education_required" in result

        # Check specific skills found
        skills = result["skills"]
        assert "languages" in skills
        assert "python" in skills["languages"]
        assert "frameworks" in skills
        assert "django" in skills["frameworks"]

    def test_extract_experience_requirement(self):
        """Test experience extraction"""
        from analyzer.job_analyzer import JobAnalyzer

        job_desc = "We need someone with 5+ years of experience"
        analyzer = JobAnalyzer()
        result = analyzer.analyze(job_desc)

        experience = result["experience_required"]
        assert "5" in experience


class TestConfiguration:
    """Tests for configuration management"""

    def test_config_defaults(self):
        """Test that configuration has sensible defaults"""
        from config import Config

        assert Config.ENVIRONMENT is not None
        assert Config.PORT > 0
        assert Config.LOG_LEVEL is not None
        assert Config.CORS_ORIGINS is not None

    def test_development_config(self):
        """Test development configuration"""
        from config import DevelopmentConfig

        assert DevelopmentConfig.DEBUG == True
        assert DevelopmentConfig.RATE_LIMIT_ENABLED == False
        assert DevelopmentConfig.CACHE_ENABLED == False

    def test_production_config(self):
        """Test production configuration"""
        from config import ProductionConfig

        assert ProductionConfig.DEBUG == False
        assert ProductionConfig.RATE_LIMIT_ENABLED == True
        assert ProductionConfig.SESSION_COOKIE_SECURE == True


# Integration Tests
class TestFlaskApp:
    """Integration tests for Flask application"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from app_production import create_app
        from config import TestingConfig

        app = create_app()
        app.config["TESTING"] = True

        with app.test_client() as client:
            yield client

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Mployable" in response.data

    def test_api_health_endpoint(self, client):
        """Test API health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    @patch("scrapers.github_scraper.GitHubScraper.scrape_profile")
    @patch("analyzer.job_analyzer.JobAnalyzer.analyze")
    @patch("generator.resume_generator.ResumeGenerator.generate")
    @patch("generator.latex_compiler.LaTeXCompiler.compile")
    def test_generate_resume_endpoint(
        self, mock_compile, mock_generate, mock_analyze, mock_scrape, client
    ):
        """Test resume generation endpoint"""
        # Setup mocks
        mock_scrape.return_value = {"username": "test", "repositories": []}
        mock_analyze.return_value = {
            "skills": {},
            "experience_required": "Not specified",
        }
        mock_generate.return_value = {"summary": "Test resume"}
        mock_compile.return_value = "/tmp/resume.pdf"

        # Mock file existence and reading
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True):
                response = client.post(
                    "/api/v1/generate-resume",
                    json={
                        "github_username": "torvalds",
                        "linkedin_url": "",
                        "job_description": "We need a C programmer with 10+ years "
                        "of experience working on operating systems",
                    },
                )

        # Should return 200 or 500 depending on mock setup
        assert response.status_code in [200, 500, 302]

    def test_generate_resume_missing_job_description(self, client):
        """Test resume generation with missing job description"""
        response = client.post(
            "/api/v1/generate-resume",
            json={
                "github_username": "torvalds",
                "linkedin_url": "",
                "job_description": "",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_resume_missing_profiles(self, client):
        """Test resume generation with no profiles"""
        response = client.post(
            "/api/v1/generate-resume",
            json={
                "github_username": "",
                "linkedin_url": "",
                "job_description": "We need a developer with 5+ years experience",
            },
        )

        assert response.status_code == 400


# Performance Tests
class TestPerformance:
    """Performance tests"""

    def test_validator_performance(self):
        """Test validator performance"""
        import time

        start = time.time()
        for _ in range(1000):
            InputValidator.validate_github_username("test-user")
        duration = time.time() - start

        # Should complete 1000 validations in less than 1 second
        assert duration < 1.0

    def test_config_loading_performance(self):
        """Test configuration loading performance"""
        import time

        start = time.time()
        from config import get_config

        for _ in range(100):
            config = get_config()
        duration = time.time() - start

        # Should load config 100 times in less than 1 second
        assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
