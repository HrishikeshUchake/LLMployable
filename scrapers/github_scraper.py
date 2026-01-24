"""
GitHub Profile Scraper

Scrapes a user's GitHub profile to extract:
- Bio and profile information
- Repositories and their descriptions
- Languages used
- Top projects
"""

from github import Github
import os
from typing import Dict, List


class GitHubScraper:
    def __init__(self):
        """Initialize GitHub scraper with optional authentication"""
        token = os.getenv('GITHUB_TOKEN')
        self.github = Github(token) if token else Github()
    
    def scrape_profile(self, username: str) -> Dict:
        """
        Scrape a GitHub profile and return structured data
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary containing profile data
        """
        try:
            user = self.github.get_user(username)
            
            # Get user information
            profile_data = {
                'username': username,  # Store the actual username
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
            
            # Get repositories
            repos = []
            for repo in user.get_repos(sort='updated', direction='desc')[:20]:  # Top 20 repos
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
            
            profile_data['repositories'] = repos
            
            # Aggregate languages
            languages = {}
            for repo in repos:
                lang = repo.get('language', '')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            profile_data['languages'] = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            
            # Get top projects (by stars)
            top_projects = sorted(repos, key=lambda x: x['stars'], reverse=True)[:5]
            profile_data['top_projects'] = top_projects
            
            return profile_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error scraping GitHub profile: {error_msg}")
            return {
                'username': username,  # Store the actual username
                'name': username,
                'bio': '',
                'error': error_msg,
                'repositories': [],
                'languages': [],
                'top_projects': [],
                'location': '',
                'email': '',
                'public_repos': 0
            }
