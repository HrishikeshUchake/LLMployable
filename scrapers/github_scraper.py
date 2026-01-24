"""
GitHub Profile Scraper

from config import get_logger, GitHubAPIError, GitHubUserNotFound, GitHubRateLimitExceeded, config
Scrapes a user's GitHub profile to extract:
- Bio and profile information
- Repositories and their descriptions
- Languages used
- Top projects
"""

from github import Github
from github.GithubException import GithubException
import os
from typing import Dict, List

from config import get_logger, GitHubAPIError, GitHubUserNotFound, GitHubRateLimitExceeded, config

logger = get_logger(__name__)


class GitHubScraper:
    def __init__(self):
        """Initialize GitHub scraper with optional authentication"""
        token = os.getenv('GITHUB_TOKEN')
        self.github = Github(token, timeout=config.GITHUB_API_TIMEOUT) if token else Github(timeout=config.GITHUB_API_TIMEOUT)
        logger.debug(f"GitHubScraper initialized with {'authenticated' if token else 'unauthenticated'} access")
    
    def scrape_profile(self, username: str) -> Dict:
        """
        Scrape a GitHub profile and return structured data
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary containing profile data
            
        Raises:
            GitHubUserNotFound: If user doesn't exist
            GitHubRateLimitExceeded: If API rate limit exceeded
            GitHubAPIError: For other API errors
        """
        logger.info(f"Scraping GitHub profile for user: {username}")
        
        try:
            user = self.github.get_user(username)
            
            # Get user information
            profile_data = {
                'username': username,
                'name': user.name or username,
                'bio': user.bio or '',
                'location': user.location or '',
                'email': user.email or '',
                'blog': user.blog or '',
                'company': user.company or '',
                'hireable': user.hireable,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following,
            }
            
            logger.debug(f"Successfully fetched profile for {username}")
            
            # Get repositories
            repos = []
            try:
                for repo in user.get_repos(sort='updated', direction='desc')[:config.GITHUB_MAX_REPOS]:
                    if not repo.fork:  # Exclude forked repos
                        repos.append({
                            'name': repo.name,
                            'description': repo.description or '',
                            'language': repo.language or '',
                            'stars': repo.stargazers_count,
                            'forks': repo.forks_count,
                            'url': repo.html_url,
                            'topics': repo.get_topics() if hasattr(repo, 'get_topics') else []
                        })
                logger.debug(f"Fetched {len(repos)} repositories for {username}")
            except GithubException as e:
                logger.warning(f"Failed to fetch repositories for {username}: {e}")
                # Continue with empty repos list
            
            profile_data['repositories'] = repos
            
            # Aggregate languages
            languages = {}
            for repo in repos:
                lang = repo.get('language', '')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            profile_data['languages'] = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            
            # Get top projects (by stars)
            top_projects = sorted(repos, key=lambda x: x['stars'], reverse=True)[:config.GITHUB_MAX_TOP_PROJECTS]
            profile_data['top_projects'] = top_projects
            
            logger.info(f"Successfully scraped GitHub profile for {username}")
            return profile_data
            
        except GithubException as e:
            logger.error(f"GitHub API error for user {username}: {e}")
            
            # Check for specific error types
            if e.status == 404:
                raise GitHubUserNotFound(username)
            elif e.status == 403:
                # Check if it's a rate limit error
                if "API rate limit exceeded" in str(e):
                    raise GitHubRateLimitExceeded()
                raise GitHubAPIError(str(e), 403)
            else:
                raise GitHubAPIError(str(e), e.status or 503)
        
        except Exception as e:
            logger.error(f"Unexpected error scraping GitHub profile for {username}: {e}", exc_info=True)
            raise GitHubAPIError(f"Failed to scrape GitHub profile: {str(e)}")
